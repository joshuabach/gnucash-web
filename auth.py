from functools import wraps

from flask import render_template, url_for, request, redirect, session
from piecash import open_book
from sqlalchemy.exc import OperationalError

from main import app, config, logger

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

def end_session():
    if config.AUTH_MECHANISM == 'passthrough':
        logger.debug(f'Logged out {session["username"]}')
        del session['username']
        del session['password']
    else:
        raise NotImplementedError('Only passthrough auth is currently supported')

def is_authenticated():
    return 'username' in session

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
