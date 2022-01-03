from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.parse import unquote_plus
from itertools import accumulate

from flask import render_template, url_for, request, redirect, session, Blueprint
from flask import current_app as app
from piecash import Transaction, Split, GnucashException
from werkzeug.exceptions import BadRequest, NotFound
from markupsafe import escape

from .auth import requires_auth, get_db_credentials
from .utils.gnucash import open_book, get_account
from .utils.jinja import account_url


bp = Blueprint('book', __name__, url_prefix='/book')


class AccountNotFound(NotFound):
    def __init__(self, fullname, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_name = fullname

@bp.app_errorhandler(AccountNotFound)
def handle_account_not_found(e: AccountNotFound):
    body = render_template('error_account_not_found.j2', account_name=e.account_name)
    return body, e.code


@bp.route('/accounts/<path:account_name>')
@bp.route('/accounts/', defaults={'account_name': ''})
@requires_auth
def show_account(account_name):
    # Pendant to `account_url`
    account_name = ':'.join(unquote_plus(name) for name in account_name.split('/'))

    with open_book(uri_conn=app.config.DB_URI(*get_db_credentials())) as book:
        account = get_account(book, fullname=account_name) if account_name else book.root_account

        return render_template(
            'account.j2',
            account=account,
            book=book,
            today=date.today(),
        )

@bp.route('/transaction', methods=['POST'])
@requires_auth
def add_transaction():
    try:
        account_name = request.form['account_name']
        transaction_date = date.fromisoformat(request.form['date'])
        description = request.form['description']
        value = Decimal(request.form['value'])
        contra_account_name = request.form['contra_account_name']
    except (InvalidOperation, ValueError) as e:
        # TODO: Say which parameter the error is about
        raise BadRequest(f'Invalid form parameter: {e}') from e

    with open_book(uri_conn=app.config.DB_URI(*get_db_credentials()), readonly=False, do_backup=False) as book:
        account = get_account(book, fullname=account_name)
        contra_account = get_account(book, fullname=contra_account_name)

        if account.placeholder:
            raise BadRequest(f'{account.fullname} is a placeholder')

        if contra_account.placeholder:
            raise BadRequest(f'{contra_account.fullname} is a placeholder')

        # TODO: Support accounts with different currencies
        assert account.commodity == contra_account.commodity, \
            f'Incompatible accounts: {account.commodity} != {contra_account.commodity}.' \
            'Transaction form in account.j2 should not have allowed this.'

        common_currency = account.commodity

        # This can not fail, since currency is a valid commodity, description can be any
        # string, post_date is a valid datetime.date, account and contra_account are valid
        # non-placeholder accounts and value is a Decimal. Any other error should be
        # considered a bug.
        transaction = Transaction(
            currency=common_currency,
            description=description,
            post_date=transaction_date,
            splits=[
                Split(account=account, value=value),
                Split(account=contra_account, value=-value),
            ],
        )

        book.save()

        return redirect(account_url(account))
