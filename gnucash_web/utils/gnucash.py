from contextlib import contextmanager

from werkzeug.exceptions import NotFound, Locked
from flask import request
import piecash
import sqlalchemy

class AccessDenied(Exception):
    pass

class AccountNotFound(NotFound):
    def __init__(self, fullname, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.account_name = fullname

class DatabaseLocked(Locked):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@contextmanager
def open_book(*args, **kwargs):
    try:
        if 'open_if_lock' not in kwargs:
            kwargs['open_if_lock'] = request.args.get('open_if_lock', default=False, type=bool)

        with piecash.open_book(*args, **kwargs) as book:
            yield book

    except piecash.GnucashException as e:
        if 'Lock on the file' in str(e):
            raise DatabaseLocked()
        else:
            raise e

    except sqlalchemy.exc.OperationalError as e:
        if 'Access denied' in str(e):
            raise AccessDenied from e
        else:
            raise e

def get_account(book, *args, **kwargs):
    try:
        return book.accounts.get(*args, **kwargs)
    except KeyError:
        raise AccountNotFound(*args, **kwargs)
