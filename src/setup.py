#!python
from setuptools import setup, find_packages
from os.path import exists

readme = open('README.md') if exists('README.md') else open('../README.md')
version = open('gnucash_web/version.txt')

setup(
    name='gnucash_web',
    version=version.read().strip(),
    author='Joshua Bachmeier',
    author_email='joshua@bachmeier.cc',
    description='A simple, easy to use, mobile-friendly webinterface for GnuCash intended for self-hosting',
    long_description=readme.read(),
    long_description_content_type='text/markdown; charset=UTF-8; variant=GFM',
    url='https://github.com/joshuabach/gnucash-web',
    project_urls={
        'Bug Tracker' : 'https://github.com/joshuabach/gnucash-web/issues',
        'Source Code' : 'https://github.com/joshuabach/gnucash-web',
    },
    license='GPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
    ],
    keywords=['bootstrap', 'flask', 'web', 'gnucash'],

    packages=find_packages(),
    package_data={
        'gnucash_web': [
            'version.txt',
            'templates/*.j2',
            'static/*.js', 'static/*.css',
            'static/bootstrap/css/*.min.css',
            'static/bootstrap/js/*.min.js',
            'static/bootstrap-icon-font/*.css',
            'static/bootstrap-icon-font/fonts/*',
            'static/selectize/css/*.css',
            'static/selectize/js/*.js',
            'static/img/official/*/apps/*',
        ],
    },

    # Because of datetime.date.fromisoformat (3.7) and importlib.metadata (3.8)
    # Piecash requires <3.12 until e9faaa3 is included in release over there
    python_requires=">=3.8,<3.12",

    # Flask <2.3 is required for encrypted_session, see #41
    # Werkzeug <3.0.0 is required for Flask, see https://stackoverflow.com/a/77214086
    install_requires=[
        'Flask>=2.0.2,<2.3.0',
        'Werkzeug<3.0.0',
        'piecash>=1.2.0',
        'pycryptodome>=3.12.0',
        'babel>=2.9.1',
        'requests>=2.27.1',
        'Flask-Session>=0.8.0'
    ],
    extras_require={
        'pgsql': 'psycopg2',
        'mysql': 'mysql',
        'redis': 'redis'
    },

    entry_points={
        'console_scripts': [
            'gnucash-web = gnucash_web:cli',
        ],
    },
)
