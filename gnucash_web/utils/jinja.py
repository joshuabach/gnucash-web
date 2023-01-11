"""Utilities for templates."""
import re
from urllib.parse import quote_plus
from itertools import islice, accumulate
from math import copysign

from flask import url_for
from babel import numbers
from markupsafe import Markup, escape
from jinja2 import Environment, BaseLoader, pass_eval_context


def safe_display_string(string):
    """Process string for HTML display.

    If it is empty, `'<blank string>'` is shown instead.

    :param string: The string to be displayed
    :returns: Camera-ready version of the string

    """
    return re.sub('^\\s*$', '<blank string>', string)


def css_escape(name):
    """Escape string for usage as CSS id selector, as in '#{name}'.

    This basically escapes anything in ASCII range, except [_A-zA-Z0-9-] with a
    preceding backslash and keeps the rest untouched.

    See https://www.w3.org/TR/CSS22/syndata.html for further information.

    :param name: The name to be used as a CSS ID selector
    :return: Escaped string

    """
    return re.sub("(?=[\\x00-\\x7f])([^_a-zA-Z0-9-])", "\\\\\\1", name)


def parent_accounts(account):
    """Generate all parent accounts of the given account.

    :param account: GnuCash account
    :returns: Parent accounts

    """
    if account:
        yield from parent_accounts(account.parent)
        yield account


@pass_eval_context
def money(eval_ctx, amount, commodity):
    """Render monetary value for human consumption.

    :param eval_ctx: Jinja evaluation context
    :param amount: The amount to be displayed
    :param commodity: Commodity in which the amount is represented
    :returns: HTML snippet

    """
    if numbers.get_currency_symbol(commodity.mnemonic) != commodity.mnemonic:
        value = numbers.format_currency(amount, commodity.mnemonic)
    else:
        value = f"{amount} {commodity.mnemonic}"

    if eval_ctx.autoescape:
        value = escape(value)

    return Markup(
        Environment(loader=BaseLoader())
        .from_string(
            """
      <span class="text-{% if amount >= 0 %}secondary{% else %}danger{% endif %}">
        {{ value }}
      </span>
    """
        )
        .render(amount=amount, value=value)
    )


def account_url(account, *args, **kwargs):
    """Get URL to view the given account.

    Percent-encodes each account name individually (important when account name contains
    slashes) and then joins the components with slashes.

    :param account: The target account
    :returns: URL suitable for redirection ore use as hyperlink

    """
    return Markup(
        url_for(
            "book.show_account",
            account_name="/".join(
                quote_plus(account.name)
                for account in islice(
                    parent_accounts(account), 1, None
                )  # Skip root account
            ),
            *args,
            **kwargs,
        )
    )


def full_account_names(account_name):
    """Return list of full account names for all parent accounts of the given account.

    Goes up to, but not including the root account.

    Does only string operations, no actual querying of the accounts with piecash and
    is thus safe for use with non-existent accounts.

    :param account_name: Account name in question.
    :returns: List of parent account names

    """
    return accumulate(account_name.split(":"), lambda sup, sub: sup + ":" + sub)

def contra_splits(split):
    """Return list of splits on the other side of the given split in the transaction.

    In other words, return all splits whose value has the opposite sign.

    :param split: Split in question
    :returns: List of contra splits
    """
    return [contra_split for contra_split in split.transaction.splits if copysign(split.value, contra_split.value) == -float(split.value) ]

def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(islice(iterable, n, None), default)
