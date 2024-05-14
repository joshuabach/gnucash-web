"""Default GnuCash Web configuration."""
import logging
import os

SECRET_KEY = bytes.fromhex(os.getenv('SECRET_KEY', '00000000'))

LOG_LEVEL = logging.getLevelName(os.getenv('LOG_LEVEL', 'WARN'))

DB_DRIVER = os.getenv('DB_DRIVER', 'sqlite')
DB_NAME = os.getenv('DB_NAME', 'db/gnucash.sqlite')
DB_HOST = os.getenv('DB_HOST', 'localhost')

AUTH_MECHANISM = os.getenv('AUTH_MECHANISM')

TRANSACTION_PAGE_LENGTH = int(os.getenv('TRANSACTION_PAGE_LENGTH', 25))
PRESELECTED_CONTRA_ACCOUNT = os.getenv('PRESELECTED_CONTRA_ACCOUNT')

SESSION_TYPE = os.getenv('SESSION_TYPE', 'redis')
if SESSION_TYPE == 'redis':
    import redis
    SESSION_REDIS = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
    )
