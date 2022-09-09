GnuCash Web
===========

*GnuCash Web* is a simple, easy to use, mobile-friendly webinterface for
[GnuCash](https://gnucash.org/) intended for self-hosting. It can access a single
GnuCash-Database in [sqlite3](https://sqlite.org/index.html),
[postgres](https://www.postgresql.org/) or [mysql](https://www.mysql.com/de/) (including
[mariadb](https://mariadb.org/)) format using the great
[piecash](https://pypi.org/project/piecash/) GnuCash library for Python.

Development status should be considered at most *Alpha*, see [below](#Contributing) for
more information.

Features
--------

The primary use case for *GnuCash Web* is adding simple (non-split) transactions on the
go, e.g. to record a cash expense when buying a coffee.

Key features include:

- Browse account hierarchy
- View non-split transaction history and balance for an account
- Add non-split transactions
- Simple single-user authentication
- Ease of use, especially on mobile

| Browse account hierarchy                                                  | View and add transactions                                            |
|---------------------------------------------------------------------------|----------------------------------------------------------------------|
| ![Browse account hierarchy](/screenshots/book.accounts.list.png?raw=true) | ![View transactions](/screenshots/book.accounts.ledger.png?raw=true) |

Core Technology Stack
---------------------

- [Python](https://www.python.org/)
- [piecash](https://pypi.org/project/piecash/) for accessing GnuCash database
- [Flask](https://palletsprojects.com/p/flask/) web framework
- [Bootstrap](https://getbootstrap.com/) for frontend design

Installation
------------

*GnuCash Web* is [available on PyPI](https://pypi.org/project/GnuCash-Web/), so you can
simply install it via `pip install gnucash_web`. Additionally, you may need to install
`mysql` or `psycopg2`, depending on which backend you want to use (sqlite backend ist
included in the python standard library).

Note that at least Python 3.8 is required.

Usage
-----

*GnuCash Web* is aimed at system administrators, but is otherwise easy to set up.

### Configuration

Create a config file in `/etc/gnucash_web/config.py` or in
`~/.config/gnucash_web/config.py`.  If both files are present, values from the latter
override those from the former.  Set the environment variable `GNUCASH_WEB_CONFIG` to load
a different config file. If set, no other config files are read.

The config file is a python script. The following example illustrates possible values for
all available options. This is the normal Flask configuration file, so all [standard
configuration
variables](https://flask.palletsprojects.com/en/2.0.x/config/#builtin-configuration-values)
can also be set.

```python
import logging

# A 32-bit-key used e.g. to encrypt the session cookie or for other cryptographic operations
SECRET_KEY = 'devel'

# Python standard library log level
LOG_LEVEL = logging.WARN

# Supported values: 'sqlite', 'mysql' or 'postgres'
DB_DRIVER = mysql

# Hostname of the database (ignored for DB_DRIVER = 'sqlite')
DB_HOST = database.example.org

# Name of the Database on the host (for DB_DRIVER = 'sqlite', this is the 'path/to/db.sqlite')
DB_NAME = 'gnucash_data'

# Supported values: None, 'passthrough'. See below for details.
AUTH_MECHANISM = None

# The maximum number of transactions per page in the ledger
TRANSACTION_PAGE_LENGTH = 25
```

### Running

It is not recommended to use the builtin Flask webserver in production. *GnuCash Web*
comes as a [WSGI](https://wsgi.readthedocs.io/en/latest/) application, so there are [many
options](https://flask.palletsprojects.com/en/2.0.x/deploying/) available to run it.

Most WSGI Webserver require setting a "module", which is the WSGI object that runs the
app. For *GnuCash Web*, this is `gnucash_web.wsgi:app`.

For example, the following `.ini`-file might be used as a config for
[uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/):

```ini
[uwsgi]
module = gnucash_web.wsgi:app
pidfile = gnucash_web.pid
master = true
processes = 1
http-socket = :8080
chmod-socket = 660
vacuum = true
```

### Authentication

Currently, there are only two authentication mechanisms supported, `None` and `'passthrough'`.

When using no authentication, anyone can access the web interface and no credentials are
provided to the database host. This is generally only usefull when using the sqlite
backend (which does not accept credentials).

When using passthrough auth, *GnuCash Web* asks for username and password upon login,
which are provided as credentails for the database hosts. They are also stored in an
encrypted session cookie in the users browser. "Logging out" simply deletes the session
cookie.



Development
-----------

Initialise submodules and install dependencies:
```sh
    git submodule init
    git submodule update
    pip install -r requirements.txt

```

Run it:
```sh
    export FLASK_APP=gnucash_web
    export FLASK_ENV=development
    flask run
```

Build and upload package:
```sh
    python -m build
    python -m twine upload dist/*
```

Contributing
------------

**Development is at an early stage, but contributions are welcome.**

This is (currently) a personal project to play around with and satisfy my own everyday
needs and intellectual curiosity.

Since *GnuCash Web* fulfills my primary use case for it, I don't expect much development
in the near future. However, if anyone is willing to help taking this into a more
feature-rich direction, I am motivated to work on that.

See [Issues](https://github.com/joshuabach/gnucash-web/issues) and
[Milestones](https://github.com/joshuabach/gnucash-web/milestones) for some ideas on how
to get started.

License
-------

Copyright © 2021 Joshua Bachmeier <joshua@bachmeier.cc>

This program is free software: you can redistribute it and/or modify it under the terms of
the GNU General Public License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but **without any
warranty**; without even the implied warranty of **merchantability** or **fitness for a
particular purpose**.  See the GNU General Public License for more details.

See [LICENSE](LICENSE) in this repository or https://www.gnu.org/licenses/ for a copy of
the GNU General Public License.

The contents of the submodules
[EncryptedSession](https://github.com/SaintFlipper/EncryptedSession) (GPLv3),
[Selectize](https://github.com/selectize/selectize.js) (Apache License 2.0),
[Bootstrap](https://github.com/twbs/bootstrap) (MIT License) and
[GnuCash](https://github.com/Gnucash/gnucash) (mutually-compatible set of licenses) as
well as all dependencies are published under their own licenses by their respective authors.
