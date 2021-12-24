import re

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
