import re
from urllib.parse import quote_plus
from itertools import islice

from flask import url_for
from babel import numbers
from markupsafe import Markup, escape
from jinja2 import Environment, BaseLoader, pass_eval_context

from main import app

def safe_display_string(string):
    return re.sub('^\s*$', '<blank string>', string)

app.jinja_env.filters['display'] = safe_display_string

def css_escape(name):
    """Escape string for usage as CSS id selector, as in '#{name}'.

    This basically escapes anything in ASCII range, except [_A-zA-Z0-9-] with a preceding
    backslash and keeps the rest untouched.

    See https://www.w3.org/TR/CSS22/syndata.html for further information.

    """
    #  escape account.fullname as CSS name
    return re.sub('(?=[\\x00-\\x7f])([^_a-zA-Z0-9-])', '\\\\\\1', name)

app.jinja_env.filters['cssescape'] = css_escape

def parent_accounts(account):
    if account:
        yield from parent_accounts(account.parent)
        yield account

app.jinja_env.filters['parentaccounts'] = parent_accounts

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

app.jinja_env.filters['money'] = money

def account_url(account):
    # Percent-encode each account name individually (important when account name contains
    # slashes) and then join with slashes
    return Markup(url_for(
        'show_account',
        account_name='/'.join(
            quote_plus(account.name)
            for account in islice(parent_accounts(account), 1, None)  # Skip root account
        )
    ))

app.jinja_env.filters['accounturl'] = account_url
