"""Default GnuCash Web configuration."""
import logging

SECRET_KEY = b'00000000000000000000000000000000'

LOG_LEVEL = logging.WARN

DB_DRIVER = 'sqlite'
DB_NAME = 'db/gnucash.sqlite'

AUTH_MECHANISM = None

TRANSACTION_PAGE_LENGTH = 25
PRESELECTED_CONTRA_ACCOUNT = None
