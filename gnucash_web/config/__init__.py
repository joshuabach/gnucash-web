"""App configuration management."""
import os

from flask import Config

from . import default

CONFIG_FILES = [
    "/etc/gnucash-web/config.py",
    f'{os.environ["HOME"]}/.config/gnucash-web/config.py',
]
CONFIG_ENVVAR = "GNUCASH_WEB_CONFIG"


class GnuCashWebConfig(Config):
    """GnuCash Web configuration manager.

    The main purpose of this is as opposed to the default `flask.Config` is define
    properties and helper functions for accessing the configuration options.

    """

    def __init__(self, app):
        """Initialize configuration manager for the given app.

        :param app: The Flask app
        :returns: Configuration manager

        """
        super().__init__(app.root_path)
        self.from_mapping(app.config)
        self.from_object(default)

        if CONFIG_ENVVAR in os.environ:
            if os.environ[CONFIG_ENVVAR]:
                app.logger.debug(f"Reading config file {os.environ[CONFIG_ENVVAR]}")
                self.from_envvar(CONFIG_ENVVAR)
        else:
            for path in filter(os.path.isfile, CONFIG_FILES):
                app.logger.debug(f"Reading config file {path}")
                self.from_pyfile(path)

    def DB_URI(self, user=None, password=None):
        """Get URI for the GnuCash database, possibly including credentials.

        :param user: Database username
        :param password: Database password
        :returns: Database URI for `piecash.open_book`
        :raises ValueError: If `DB_DRIVER == "sqlite"` and `user` or `password` is
          not `None`

        """
        if self["DB_DRIVER"] == "sqlite":
            if user or password:
                raise ValueError(
                    "DB_DRIVER 'sqlite' does not accept credentials"
                    " (maybe AUTH_MECHANISM 'passthrough' is set?)"
                )
            else:
                return "{DB_DRIVER}:///{DB_NAME}".format(
                    **self,
                )
        else:
            auth = ":".join(elt for elt in [user, password] if elt)
            location = "/".join(
                elt for elt in [self["DB_HOST"], self["DB_NAME"]] if elt
            )
            return "{DB_DRIVER}://{uri}".format(
                **self, uri="@".join(elt for elt in [auth, location] if elt)
            )

    @property
    def SESSION_CRYPTO_KEY(self):
        """Get key for EncryptedSession.

        We simply use the Flask SECRET_KEY here.

        :returns: 32-bit AES key as bytes

        """
        return self["SECRET_KEY"]

    def __getattr__(self, attr):
        """Entry point to get config options from gnucash_web code.

        :param attr: Name of the configuration option
        :returns: Value of the configuration option

        """
        return super().__getitem__(attr)

    def __getitem__(self, key):
        """Entry point to get config options from Flask code.

        :param key: Name of the configuration option
        :returns: Value of the configration option

        """
        if hasattr(self, key):
            return getattr(self, key)
        else:
            return super().__getitem__(key)

    def __contains__(self, key):
        """Check if configuration option is provided.

        :param key: Name of the configuration option
        :returns: True, iff the option is set

        """
        return hasattr(self, key) or super().__contains__(key)
