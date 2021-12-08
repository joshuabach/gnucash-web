from datetime import date
from decimal import Decimal

from flask import Flask, render_template, url_for, request, redirect
from piecash import open_book, GnucashException, Transaction, Split

GNUCASH_URI = 'mysql://USER:PASSWORD@HOST:PORT/DATABASE'

app = Flask(__name__)

@app.route('/accounts/<path:account_name>')
@app.route('/accounts/', defaults={'account_name': ''})
def show_account(account_name):
    account_name = account_name.replace('/', ':')

    with open_book(uri_conn=GNUCASH_URI) as book:
        account = book.accounts.get(fullname=account_name) if account_name else book.root_account

        # TODO: Support non-placeholder accounts with subaccounts
        if account.placeholder or account.type == 'ROOT':
            # List all subaccounts
            return render_template(
                'accounts.j2',
                base_account=account,
                account_name=account.fullname or 'Book',
            )
        else:
            # List transactions in account
            return render_template(
                'account.j2',
                account=account,
                book=book,
            )

@app.route('/transaction', methods=['POST'])
def add_transaction():
    account_name = request.form['account_name']
    transaction_date = date.fromisoformat(request.form['date'])
    description = request.form['description']
    value = Decimal(request.form['value'])
    contra_account_name = request.form['contra_account_name']

    with open_book(uri_conn=GNUCASH_URI, readonly=False, do_backup=False) as book:
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
