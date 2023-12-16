from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.parse import unquote_plus, urlencode
from math import ceil
import calendar

from flask import render_template, request, redirect, Blueprint, jsonify
from flask import current_app as app
from piecash import Transaction, Split, Budget
from werkzeug.exceptions import BadRequest
import pandas as pd
import numpy as np
from datetime import datetime

from .auth import requires_auth, get_db_credentials
from .utils.gnucash import open_book, get_account, get_budgets, get_budget, AccountNotFound, DatabaseLocked
from .utils.jinja import account_url


bp = Blueprint("budget", __name__, url_prefix="/budget")

@bp.route("/")
@requires_auth
def list_budgets():
    """
    """
    with open_book(
            uri_conn=app.config.DB_URI(*get_db_credentials()),
            open_if_lock=True,
            readonly=True,
        ) as book:
            budgetsInBook = get_budgets(book)

            return render_template('budgets.html', budgets=budgetsInBook)

@bp.route("/<path:budget_name>")
@requires_auth
def show_budget(budget_name):
    """
    """

    try:
        budget_name = ":".join(unquote_plus(name) for name in budget_name.split("/"))
    except ValueError as e:
        raise BadRequest(f'Invalid query parameter: {e}') from e

    with open_book(
        uri_conn=app.config.DB_URI(*get_db_credentials()),
        open_if_lock=True,
        readonly=True,
    ) as book:
        budget = (
            get_budget(book, name=budget_name)
        )

        _df = []
        budget_start_date = budget.recurrence.recurrence_period_start
        month_year = budget_start_date.strftime('%Y-%m')

        if budget.recurrence.recurrence_period_type == "month":
            date_modifier = 'M'

        for amount in budget.amounts:
            _row = {}
            _period = np.datetime64(month_year) + np.timedelta64(amount.period_num, date_modifier)
            _period = _period.astype(datetime)
            _row['_period'] = _period
            _row['period'] = _period.strftime('%B %Y')
            _row['amount'] = amount.amount
            _row['account'] = amount.account.name

            _df.append(_row)

        df = pd.DataFrame(_df).sort_values(by=['_period'])
        _periods = df['period'].unique()
        __periods = [ (t, datetime.strptime(t, '%B %Y').strftime("%Y-%m")) for t in _periods ]

        return render_template('budget.html', budgetData=budget, budgetFrame=df, _periods=__periods)