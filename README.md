[WIP] GnuCash Web
=================

*GnuCash Web* is a simple, easy to use, mobile-friendly webinterface for
[GnuCash](https://gnucash.org/) intended for self-hosting. It can access a single
GnuCash-Database in [sqlite3](https://sqlite.org/index.html),
[postgres](https://www.postgresql.org/) or [mysql](https://www.mysql.com/de/) (including
[mariadb](https://mariadb.org/)) format using the great
[piecash](https://pypi.org/project/piecash/) GnuCash library for Python.

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

Core Technology Stack
---------------------

- [Python](https://www.python.org/)
- [piecash](https://pypi.org/project/piecash/) for accessing GnuCash database
- [flask](https://palletsprojects.com/p/flask/) web framework
- [Bootstrap](https://getbootstrap.com/) for frontend design

Installation
------------
TBD

Configuration & Usage
---------------------
TBD

Development
-----------
```sh
    pip install -r requirements.txt
    export FLASK_ENV=development
    flask run
```

Contributing
------------

**Contributions are not yet welcome, until the initial release.**

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
[Bootstrap](https://github.com/twbs/bootstrap) (MIT License) and
[GnuCash](https://github.com/Gnucash/gnucash) (mutually-compatible set of licenses) as
well as all dependencies are published under their own licenses by their respective authors.
