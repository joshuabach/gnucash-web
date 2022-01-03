from contextlib import contextmanager

from werkzeug.exceptions import Locked
import piecash
import sqlalchemy

from ..auth import AccessDenied

@contextmanager
def open_book(*args, **kwargs):
    try:
        with piecash.open_book(*args, **kwargs) as book:
            yield book
    except piecash.GnucashException as e:
        if 'Lock on the file' in str(e):
            raise Locked('GnuCash Database is locked')
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
        # Import here, because of circular import
        from ..book import AccountNotFound
        raise AccountNotFound(*args, **kwargs)
