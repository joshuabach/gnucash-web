import os
import logging
from datetime import date
from decimal import Decimal

from flask import Flask, render_template, url_for, request, redirect
from piecash import open_book, GnucashException, Transaction, Split

from config import Config, DefaultConfig

# Main Flask Web App
app = Flask(__name__)

# Start with a INFO-Logger, so we can log during config parsinig
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config files
CONFIG_FILES = [
    '/etc/gnucash-web/config.py',
    f'{os.environ["HOME"]}/.config/gnucash-web/config.py',
]
CONFIG_ENVVAR = 'GNUCASH_WEB_CONFIG'

app.config.from_object(DefaultConfig())
for path in filter(os.path.isfile, CONFIG_FILES):
    logger.info(f'Reading config file {path}')
    app.config.from_pyfile(path)
if CONFIG_ENVVAR in os.environ:
    logger.info(f'Reading config file {CONFIG_ENVVAR}')
    app.config.from_envvar(CONFIG_ENVVAR)

config = ConfigWrapper(app)

# Now we set the log level to what is configured
logger.info(f'Log level is {logging.getLevelName(config.EFFECTIVE_LOG_LEVEL)}')
logger.setLevel(config.EFFECTIVE_LOG_LEVEL)

# TODO Add auth mechanism
USER = 'user'
PASSWORD = 'password'

@app.route('/accounts/<path:account_name>')
@app.route('/accounts/', defaults={'account_name': ''})
def show_account(account_name):
    account_name = account_name.replace('/', ':')

    with open_book(uri_conn=config.DB_URI(USER, PASSWORD)) as book:
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

    with open_book(uri_conn=config.DB_URI(USER, PASSWORD), readonly=False, do_backup=False) as book:
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
