import os
import sys
import logging

from flask import Flask

sys.path.append('EncryptedSession')
from encrypted_session import EncryptedSessionInterface

from config import ConfigWrapper, DefaultConfig

# Main Flask Web App
app = Flask('app')

# Start with a INFO-Logger, so we can log during config parsinig
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load config files
CONFIG_FILES = [
    '/etc/gnucash-web/config.py',
    f'{os.environ["HOME"]}/.config/gnucash-web/config.py',
]
CONFIG_ENVVAR = 'GNUCASH_WEB_CONFIG'

app.config.from_object(DefaultConfig())
if CONFIG_ENVVAR in os.environ:
    logger.info(f'Reading config file {CONFIG_ENVVAR}')
    if os.environ[CONFIG_ENVVAR]:
        app.config.from_envvar(CONFIG_ENVVAR)
else:
    for path in filter(os.path.isfile, CONFIG_FILES):
        logger.info(f'Reading config file {path}')
        app.config.from_pyfile(path)

config = ConfigWrapper(app)

# We encrypt the session-cookie, so the DB-password is not stored in plaintext when using
# AUTH_MECHANISM == 'passthrough'.
app.config['SESSION_CRYPTO_KEY'] = app.config['SECRET_KEY'] or app.debug and 'DEBUG'
app.session_interface = EncryptedSessionInterface()

# Now we set the log level to what is configured
logger.info(f'Log level is {logging.getLevelName(config.EFFECTIVE_LOG_LEVEL)}')
logger.setLevel(config.EFFECTIVE_LOG_LEVEL)

