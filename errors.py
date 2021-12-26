from main import app, config, logger

from werkzeug.exceptions import NotFound
from itertools import accumulate

from markupsafe import escape
from flask import render_template


def full_account_names(account_name):
    return accumulate(
        account_name.split(':'),
        lambda sup, sub: sup + ':' + sub
    )
app.jinja_env.filters['full_account_names'] = full_account_names


class AccountNotFound(NotFound):
    def __init__(self, account_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_name = account_name

@app.errorhandler(AccountNotFound)
def handle_account_not_found(e: AccountNotFound):
    body = render_template('error_account_not_found.j2', account_name=e.account_name)
    return body, e.code
