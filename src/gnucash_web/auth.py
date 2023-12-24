from functools import wraps

from flask import Blueprint, render_template, url_for, request, redirect, session
from flask import current_app as app
from sqlalchemy.exc import OperationalError

from .utils.gnucash import open_book, AccessDenied

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.app_errorhandler(AccessDenied)
def handle_account_not_found(e: AccessDenied):
    end_session()
    return redirect(url_for('auth.login'))


def get_db_credentials():
    if not app.config.AUTH_MECHANISM:
        return (None, None)
    elif app.config.AUTH_MECHANISM == 'passthrough':
        return (session['username'], session['password'])
    else:
        raise NotImplementedError('Only passthrough auth is currently supported')

def authenticate(username, password):
    if not app.config.AUTH_MECHANISM:
        return True
    elif app.config.AUTH_MECHANISM == 'passthrough':
        try:
            # Check authn by attempting to connect to database
            with open_book(uri_conn=app.config.DB_URI(username, password),
                           readonly=True, open_if_lock=True) as book:
                app.logger.debug(f'Authentication succeeded for {username}')
                session['username'] = username
                session['password'] = password
                return True
        except AccessDenied:
            app.logger.debug(f'Authentication failed for {username}')
            return False
    else:
        raise NotImplementedError('Only passthrough auth is currently supported')

def end_session():
    if not app.config.AUTH_MECHANISM:
        pass
    elif app.config.AUTH_MECHANISM == 'passthrough':
        app.logger.debug(f'Logged out {session["username"]}')
        del session['username']
        del session['password']
    else:
        raise NotImplementedError('Only passthrough auth is currently supported')

def is_authenticated():
    return not app.config.AUTH_MECHANISM or 'username' in session


# Decorator for view functions
def requires_auth(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if is_authenticated():
            return func(*args, **kwargs)
        else:
            return redirect(url_for('auth.login', return_url=request.url))

    return inner


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
       authenticate(request.form['username'], request.form['password'])
       session.permanent = True
       return redirect(request.args.get('return_url') or url_for('.login'))
    else:
        if is_authenticated():
            return render_template('user.html', username=session.get('username', 'no one'))
        else:
            return render_template('login.html')

@bp.route('/logout', methods=['POST'])
def logout():
    end_session()
    return redirect(url_for('auth.login'))
