from datetime import date
from decimal import Decimal
from urllib.parse import quote_plus, unquote_plus
from itertools import islice

from flask import render_template, url_for, request, redirect, session
from piecash import open_book, Transaction, Split
from jinja2 import Environment, BaseLoader, pass_eval_context
from markupsafe import Markup, escape
from babel import numbers

from main import app, config, logger
from auth import requires_auth, get_db_credentials

def parent_accounts(account):
    if account:
        yield from parent_accounts(account.parent)
        yield account

app.jinja_env.filters['parentaccounts'] = parent_accounts

@pass_eval_context
def money(eval_ctx, amount, commodity):
    if numbers.get_currency_symbol(commodity.mnemonic) != commodity.mnemonic:
        value = numbers.format_currency(amount, commodity.mnemonic)
    else:
        value = f'{amount} {commodity.mnemonic}'

    if eval_ctx.autoescape:
        value = escape(value)

    return Markup(Environment(loader=BaseLoader()).from_string('''
      <span class="text-{% if amount >= 0 %}secondary{% else %}danger{% endif %}">
        {{ value }}
      </span>
    ''').render(amount=amount, value=value))

app.jinja_env.filters['money'] = money

def account_url(account):
    # Percent-encode each account name individually (important when account name contains
    # slashes) and then join with slashes
    return Markup(url_for(
        'show_account',
        account_name='/'.join(
            quote_plus(account.name)
            for account in islice(parent_accounts(account), 1, None)  # Skip root account
        )
    ))

app.jinja_env.filters['accounturl'] = account_url

@app.route('/accounts/<path:account_name>')
@app.route('/accounts/', defaults={'account_name': ''})
@requires_auth
def show_account(account_name):
    # Pendant to `account_url`
    account_name = ':'.join(unquote_plus(name) for name in account_name.split('/'))

    with open_book(uri_conn=config.DB_URI(*get_db_credentials())) as book:
        account = book.accounts.get(fullname=account_name) if account_name else book.root_account

        return render_template(
            'account.j2',
            account=account,
            book=book,
            today=date.today(),
        )

@app.route('/transaction', methods=['POST'])
@requires_auth
def add_transaction():
    account_name = request.form['account_name']
    transaction_date = date.fromisoformat(request.form['date'])
    description = request.form['description']
    value = Decimal(request.form['value'])
    contra_account_name = request.form['contra_account_name']

    with open_book(uri_conn=config.DB_URI(*get_db_credentials()), readonly=False, do_backup=False) as book:
        account = book.accounts.get(fullname=account_name)
        contra_account = book.accounts.get(fullname=contra_account_name)

        # TODO: Support accounts with different currencies
        assert account.commodity == contra_account.commodity, \
            f'{account.commodity} != {contra_account.commodity}'
        common_currency = account.commodity

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

    return redirect(url_for(
        'show_account',
        account_name=account_name.replace(':', '/')
    ))
