from functools import wraps

from flask import Blueprint, render_template, url_for, request, redirect, session
from piecash import open_book
from sqlalchemy.exc import OperationalError

from flask import current_app as app

bp = Blueprint('auth', __name__, url_prefix='/auth')

class AccessDenied(Exception):
    pass

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
            with open_book(uri_conn=app.config.DB_URI(username, password)) as book:
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
            return redirect(url_for('auth.login'))

    return inner


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
       authenticate(request.form['username'], request.form['password'])

    if is_authenticated():
        return render_template('user.j2', username=session.get('username', 'no one'))
    else:
        return render_template('login.j2')

@bp.route('/logout', methods=['POST'])
def logout():
    end_session()
    return redirect(url_for('auth.login'))
