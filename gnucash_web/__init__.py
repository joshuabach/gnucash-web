import os
import sys
import pathlib
from importlib import metadata

from flask import Flask, redirect, url_for
from flask.cli import FlaskGroup
import click

from . import auth, book
from .utils import jinja as jinja_utils
from .config import GnuCashWebConfig

from encrypted_session import EncryptedSessionInterface


def create_app(test_config=None):
    app = Flask('gnucash_web')
    app.config = GnuCashWebConfig(app)

    if not app.debug:
        app.logger.setLevel(app.config.LOG_LEVEL)

    # We encrypt the session-cookie, so the DB-password is not stored in plaintext when using
    # AUTH_MECHANISM == 'passthrough'.
    app.session_interface = EncryptedSessionInterface()

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.jinja_env.autoescape = True
    app.jinja_env.filters['display'] = jinja_utils.safe_display_string
    app.jinja_env.filters['cssescape'] = jinja_utils.css_escape
    app.jinja_env.filters['parentaccounts'] = jinja_utils.parent_accounts
    app.jinja_env.filters['money'] = jinja_utils.money
    app.jinja_env.filters['accounturl'] = jinja_utils.account_url
    app.jinja_env.filters['full_account_names'] = jinja_utils.full_account_names
    app.jinja_env.globals['is_authenticated'] = auth.is_authenticated

    app.jinja_env.globals['pkg_version'] = metadata.version('gnucash_web')

    app.register_blueprint(auth.bp)
    app.register_blueprint(book.bp)

    @app.route('/')
    def index():
        return redirect(url_for('book.show_account'))

    return app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """GnuCash Web - A simple, easy to use, mobile-friendly webinterface intended for self-hosting"""
