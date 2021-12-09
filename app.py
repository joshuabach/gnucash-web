import os
import sys
import logging
from datetime import date
from decimal import Decimal
from functools import wraps

from flask import Flask, render_template, url_for, request, redirect, session
from piecash import open_book, GnucashException, Transaction, Split
from sqlalchemy.exc import OperationalError

sys.path.append('EncryptedSession')
from encrypted_session import EncryptedSessionInterface

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

# We encrypt the session-cookie, so the DB-password is not stored in plaintext when using
# AUTH_MECHANISM == 'passthrough'.
app.config['SESSION_CRYPTO_KEY'] = app.config['SECRET_KEY']
app.session_interface = EncryptedSessionInterface()

# Now we set the log level to what is configured
logger.info(f'Log level is {logging.getLevelName(config.EFFECTIVE_LOG_LEVEL)}')
logger.setLevel(config.EFFECTIVE_LOG_LEVEL)

def get_db_credentials():
    if config.AUTH_MECHANISM == 'passthrough':
        return (session['username'], session['password'])
    else:
        raise NotImplementedError('Only passthrough auth is currently supported')

def authenticate(username, password):
    if config.AUTH_MECHANISM == 'passthrough':
        try:
            with open_book(uri_conn=config.DB_URI(username, password)) as book:
                logger.debug(f'Authentication succeeded for {username}')
                session['username'] = username
                session['password'] = password
                return True
        except OperationalError:
            logger.debug(f'Authentication failed for {username}')
            return False
    else:
        raise NotImplementedError('Only passthrough auth is currently supported')

def is_authenticated():
    return 'username' in session

def end_session():
    if config.AUTH_MECHANISM == 'passthrough':
        logger.debug(f'Logged out {session["username"]}')
        del session['username']
        del session['password']
    else:
        raise NotImplementedError('Only passthrough auth is currently supported')

# Decorator for view functions
def requires_auth(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if is_authenticated():
            return func(*args, **kwargs)
        else:
            return redirect(url_for('login'))

    return inner


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
       authenticate(request.form['username'], request.form['password'])

    if 'username' in session:
        return render_template('user.j2', username=session['username'])
    else:
        return render_template('login.j2')

@app.route('/logout', methods=['POST'])
def logout():
    end_session()
    return redirect(url_for('login'))


@app.route('/accounts/<path:account_name>')
@app.route('/accounts/', defaults={'account_name': ''})
@requires_auth
def show_account(account_name):
    account_name = account_name.replace('/', ':')

    with open_book(uri_conn=config.DB_URI(*get_db_credentials())) as book:
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
