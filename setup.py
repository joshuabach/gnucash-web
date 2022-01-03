#!python
from setuptools import setup, find_packages

setup(
    name='GnuCash Web',
    version='0.0.1',
    author='Joshua Bachmeier',
    author_email='joshua@bachmeier.cc',
    description='A simple, easy to use, mobile-friendly webinterface for GnuCash intended for self-hosting',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown; charset=UTF-8; variant=GFM',
    url='https://github.com/joshuabach/gnucash-web',
    project_urls={
        'Bug Tracker' : 'https://github.com/joshuabach/gnucash-web/issues',
        'Source Code' : 'https://github.com/joshuabach/gnucash-web',
    },
    license='GPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
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
            'templates/*.j2',
            'static/*.js', 'static/*.css',
            'static/bootstrap/css/*.min.css',
            'static/bootstrap/js/*.min.js',
            'static/img/official/*/apps/*',
        ],
    },

    # Because of datetime.date.fromisoformat (3.7) and importlib.metadata (3.8)
    python_requires=">=3.8",

    install_requires=[
        'Flask>=2.0.2',
        'piecash>=1.2.0',
        'pycryptodome>=3.12.0',
        'babel>=2.9.1',
    ],
    extras_require={
        'PostgreSQL backend': 'psycopg2',
        'MySQL / MariaDB backend': 'mysql',
    },

    entry_points={
        'console_scripts': [
            'gnucash-web = gnucash_web:cli',
        ],
    },
)
