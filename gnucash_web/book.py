"""Functions for interacting with a GnuCash book."""
from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.parse import unquote_plus, urlencode
from math import ceil

from flask import render_template, request, redirect, Blueprint
from flask import current_app as app
from piecash import Transaction, Split
from werkzeug.exceptions import BadRequest

from .auth import requires_auth, get_db_credentials
from .utils.gnucash import open_book, get_account, AccountNotFound, DatabaseLocked
from .utils.jinja import account_url

bp = Blueprint("book", __name__, url_prefix="/book")


@bp.app_errorhandler(AccountNotFound)
def handle_account_not_found(e: AccountNotFound):
    """Show error page about the desired account not being found.

    :param e: The underlying AccountNotFound exception
    :returns: Rendered HTTP Response

    """
    body = render_template("error_account_not_found.j2", account_name=e.account_name)
    return body, e.code


@bp.app_errorhandler(DatabaseLocked)
def handle_database_locked(e: DatabaseLocked):
    """Show error page about the database beeing accessed by another user.

    Includes option to repeat the causing action ignoring the lock.

    :param e: The underlying DatabaseLocked exception
    :returns: Rendered HTTP Response

    """
    # Generate path to current view, but with open_if_lock=True
    query = {"open_if_lock": "True"}
    query.update(request.args)
    url = f"{request.url}?{urlencode(query)}"

    body = render_template(
        "error_database_locked.j2",
        ignore_lock_url=url,
    )
    return body, e.code


@bp.route("/accounts/<path:account_name>")
@bp.route("/accounts/", defaults={"account_name": ""})
@requires_auth
def show_account(account_name):
    """Show the given account, including all subaccounts and transactions.

    If the account has subaccounts, a collapsible tree view of them is rendered.

    Additionally, if the account is not a placeholder, a ledger listing all
    transaction in the account is rendered, including a HTML form to add a new
    transaction.

    :param account_name: Name of the account, with / as account name separator. Each
      componnent of the account name must be urlencoded.
    :returns: Rendered HTTP Response

    """
    try:
        account_name = ":".join(unquote_plus(name) for name in account_name.split("/"))
        page = int(request.args.get('page', 1))
    except ValueError as e:
        raise BadRequest(f'Invalid query parameter: {e}') from e

    if page < 1:
        raise BadRequest(f'Invalid query parameter: page number must be positive integer: {page}')

    with open_book(
        uri_conn=app.config.DB_URI(*get_db_credentials()),
        open_if_lock=True,
        readonly=True,
    ) as book:
        account = (
            get_account(book, fullname=account_name)
            if account_name
            else book.root_account
        )

        num_pages = max(1, ceil(len(account.splits) / app.config.TRANSACTION_PAGE_LENGTH))
        if page > num_pages:
            raise BadRequest(f'Invalid query parameter: not enough pages: {page} > {num_pages}')

        return render_template(
            "account.j2",
            account=account,
            book=book,
            today=date.today(),
            num_pages=num_pages,
            page=page,
        )


@bp.route("/transaction", methods=["POST"])
@requires_auth
def add_transaction():
    """Add a new Transaction.

    All parameters are read from `request.form`.

    A positive value will transfer the desired amount from the contra account the
    receiver account ("this" account), while a negative value will deduct from the
    receiver account and credit to the contra account. Or, in other words, a negative
    value is an expense, a positive value is an income.

    :param account_name: Name of the receiver account
    :param transaction_date: Date of the transaction
    :param description: Transaction description (not split memo)
    :param value: Value of the transaction
    :param contra_account_name: Name of the contra account

    """
    try:
        account_name = request.form["account_name"]
        transaction_date = date.fromisoformat(request.form["date"])
        description = request.form["description"]
        value = Decimal(request.form["value"])
        contra_account_name = request.form["contra_account_name"]
    except (InvalidOperation, ValueError) as e:
        # TODO: Say which parameter the error is about
        raise BadRequest(f"Invalid form parameter: {e}") from e

    with open_book(
        uri_conn=app.config.DB_URI(*get_db_credentials()),
        readonly=False,
        do_backup=False,
    ) as book:
        account = get_account(book, fullname=account_name)
        contra_account = get_account(book, fullname=contra_account_name)

        if account.placeholder:
            raise BadRequest(f"{account.fullname} is a placeholder")

        if contra_account.placeholder:
            raise BadRequest(f"{contra_account.fullname} is a placeholder")

        # TODO: Support accounts with different currencies
        assert account.commodity == contra_account.commodity, (
            f"Incompatible accounts: {account.commodity} != {contra_account.commodity}."
            "Transaction form in account.j2 should not have allowed this."
        )

        common_currency = account.commodity

        # This can not fail, since currency is a valid commodity, description can be
        # any string, post_date is a valid datetime.date, account and contra_account
        # are valid non-placeholder accounts and value is a Decimal. Any other error
        # should be considered a bug.
        _ = Transaction(
            currency=common_currency,
            description=description,
            post_date=transaction_date,
            splits=[
                Split(account=account, value=value),
                Split(account=contra_account, value=-value),
            ],
        )

        book.save()

        return redirect(account_url(account))
