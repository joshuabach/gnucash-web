import re
from urllib.parse import quote_plus
from itertools import islice, accumulate

from flask import url_for
from babel import numbers
from markupsafe import Markup, escape
from jinja2 import Environment, BaseLoader, pass_eval_context

def safe_display_string(string):
    return re.sub('^\s*$', '<blank string>', string)


def css_escape(name):
    """Escape string for usage as CSS id selector, as in '#{name}'.

    This basically escapes anything in ASCII range, except [_A-zA-Z0-9-] with a preceding
    backslash and keeps the rest untouched.

    See https://www.w3.org/TR/CSS22/syndata.html for further information.

    """
    #  escape account.fullname as CSS name
    return re.sub('(?=[\\x00-\\x7f])([^_a-zA-Z0-9-])', '\\\\\\1', name)


def parent_accounts(account):
    if account:
        yield from parent_accounts(account.parent)
        yield account


@pass_eval_context
def money(eval_ctx, amount, commodity):
    if numbers.get_currency_symbol(commodity.mnemonic) != commodity.mnemonic:
        value = numbers.format_currency(amount, commodity.mnemonic)
    else:
        value = f'{amount} {commodity.mnemonic}'

    if eval_ctx.autoescape:
        value = escape(value)

    return Markup(Environment(loader=BaseLoader()).from_string('''
      <span class="text-{% if amount >= 0 %}secondary{% else %}danger{% endif %}">
        {{ value }}
      </span>
    ''').render(amount=amount, value=value))


def account_url(account):
    # Percent-encode each account name individually (important when account name contains
    # slashes) and then join with slashes
    return Markup(url_for(
        'book.show_account',
        account_name='/'.join(
            quote_plus(account.name)
            for account in islice(parent_accounts(account), 1, None)  # Skip root account
        )
    ))


def full_account_names(account_name):
    return accumulate(
        account_name.split(':'),
        lambda sup, sub: sup + ':' + sub
    )
