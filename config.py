import logging

class DefaultConfig:
    LOG_LEVEL = logging.WARN

    DB_DRIVER = 'mysql'
    DB_HOST = '127.0.0.1'
    DB_NAME = 'gnucash'

class ConfigWrapper:
    def __init__(self, app):
        self.app = app

    def DB_URI(self, user, password):
        return '{DB_DRIVER}://{user}:{password}@{DB_HOST}/{DB_NAME}'.format(**self.app.config, user=user, password=password)

    @property
    def EFFECTIVE_LOG_LEVEL(self):
        if self.app.debug:
            return logging.DEBUG
        else:
            return self.app.config.LOG_LEVEL

    def __getattr__(self, attr):
        return self.app.config[attr]
