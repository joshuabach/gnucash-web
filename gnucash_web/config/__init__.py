import os
import logging

from flask import Config

from . import default

CONFIG_FILES = [
    '/etc/gnucash-web/config.py',
    f'{os.environ["HOME"]}/.config/gnucash-web/config.py',
]
CONFIG_ENVVAR = 'GNUCASH_WEB_CONFIG'

class GnuCashWebConfig(Config):
    def __init__(self, app):
        super().__init__(app.root_path)
        self.from_mapping(app.config)
        self.from_object(default)

        if CONFIG_ENVVAR in os.environ:
            if os.environ[CONFIG_ENVVAR]:
                app.logger.info(f'Reading config file {os.environ[CONFIG_ENVVAR]}')
                self.from_envvar(CONFIG_ENVVAR)
        else:
            for path in filter(os.path.isfile, CONFIG_FILES):
                app.logger.info(f'Reading config file {path}')
                self.from_pyfile(path)

    def DB_URI(self, user=None, password=None):
        if self['DB_DRIVER'] == 'sqlite':
            if user or password:
                raise ValueError("DB_DRIVER 'sqlite' does not accept credentials (maybe AUTH_MECHANISM 'passthrough' is set?)")
            else:
                return '{DB_DRIVER}:///{DB_NAME}'.format(
                    **self,
                )
        else:
            auth = ':'.join(elt for elt in [user, password] if elt)
            location = '/'.join(elt for elt in [self['DB_HOST'], self['DB_NAME']] if elt)
            return '{DB_DRIVER}://{uri}'.format(
                **self,
                uri='@'.join(elt for elt in [auth, location] if elt)
            )

    @property
    def SESSION_CRYPTO_KEY(self):
        return self['SECRET_KEY']

    def __getattr__(self, attr):
        return super().__getitem__(attr)

    def __getitem__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        else:
            return super().__getitem__(key)

    def __contains__(self, key):
        return hasattr(self, key) or super().__contains__(key)
