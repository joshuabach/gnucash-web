import logging

class DefaultConfig:
    LOG_LEVEL = logging.WARN

    DB_DRIVER = 'sqlite'
    DB_NAME = 'db/gnucash.sqlite'

    AUTH_MECHANISM = None

class ConfigWrapper:
    def __init__(self, app):
        self.app = app

    def DB_URI(self, user=None, password=None):
        if self.app.config['DB_DRIVER'] == 'sqlite':
            if user or password:
                raise ValueError("DB_DRIVER 'sqlite' does not accept credentials (maybe AUTH_MECHANISM 'passthrough' is set?)")
            else:
                return '{DB_DRIVER}:///{DB_NAME}'.format(
                    **self.app.config,
                )
        else:
            auth = ':'.join(elt for elt in [user, password] if elt)
            location = '/'.join(elt for elt in [self.app.config['DB_HOST'], self.app.config['DB_NAME']] if elt)
            return '{DB_DRIVER}://{uri}'.format(
                **self.app.config,
                uri='@'.join(elt for elt in [auth, location] if elt)
            )

    @property
    def EFFECTIVE_LOG_LEVEL(self):
        if self.app.debug:
            return logging.DEBUG
        else:
            return self.app.config['LOG_LEVEL']

    def __getattr__(self, attr):
        return self.app.config[attr]
