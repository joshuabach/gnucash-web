import os

from Crypto.Random import get_random_bytes

# A 32-bit-key used e.g. to encrypt the session cookie or for other cryptographic operations
# Use e.g. `from Crypto.Random import get_random_bytes; print(get_random_bytes(32))`
SECRET_KEY = get_random_bytes(32)

# Python standard library log level
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING')

# Supported values: 'sqlite', 'mysql' or 'postgres'
DB_DRIVER = os.environ.get('DB_DRIVER', 'mysql')

# Host name of the database (ignored for DB_DRIVER = 'sqlite')
DB_HOST = os.environ.get('DB_HOST', 'host.docker.internal')

# Name of the Database on the host (for DB_DRIVER = 'sqlite', this is the 'path/to/db.sqlite')
DB_NAME = os.environ.get('DB_NAME', 'gnucash')

# Supported values: None, 'passthrough'. See below for details.
AUTH_MECHANISM = os.environ.get('AUTH_MECHANISM', 'passthrough')

# The maximum number of transactions per page in the ledger
TRANSACTION_PAGE_LENGTH = int(os.environ.get('TRANSACTION_PAGE_LENGTH', 25))

# Name of the account to be preselected when creating new transactions (optional)
PRESELECTED_CONTRA_ACCOUNT = os.environ.get('PRESELECTED_CONTRA_ACCOUNT', 'Expenses:Groceries')
