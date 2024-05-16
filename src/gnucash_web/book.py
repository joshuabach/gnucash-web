"""Functions for interacting with a GnuCash book."""
from datetime import date
from decimal import Decimal, InvalidOperation
from urllib.parse import unquote_plus, urlencode
from math import ceil

from flask import render_template, request, redirect, Blueprint
from flask import current_app as app
from piecash import Transaction, Split, AccountType
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
            account_types=(t.value for t in AccountType if t != AccountType.root)
        )


@bp.route("/add_transaction", methods=["POST"])
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
    :param value: The amount to be transferred
    :param sign: The transactions sign: `+1` for deposit, `-1` for withdrawl
    :param contra_account_name: Name of the contra account
    """

    try:
        account_name = request.form["account_name"]
        transaction_date = date.fromisoformat(request.form["date"])
        description = request.form["description"]
        value = Decimal(request.form["value"])
        contra_account_name = request.form["contra_account_name"]
        sign = int(request.form["sign"])
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

        if value < 0:
            raise BadRequest(f"Value {value} must not be negative")
        value = sign*value

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


@bp.route("/edit_transaction", methods=["POST"])
@requires_auth
def edit_transaction():
    """Edit an existing Transaction.

    All parameters are read from `request.form`.

    Parameters are similar `add_transaction` and `del_transaction`.

    :param account_name: Name of the receiver account
    :param guid: GUID of the transaction to be deleted
    :param transaction_date: Date of the transaction
    :param description: Transaction description (not split memo)
    :param value: The amount to be transferred
    :param contra_account_name: Name of the contra account
    :param sign: The transactions sign: `+1` for deposit, `-1` for withdrawl
    """
    # TODO DRY: This function is very similar to add_transaction
    try:
        account_name = request.form["account_name"]
        guid = request.form["guid"]
        transaction_date = date.fromisoformat(request.form["date"])
        description = request.form["description"]
        value = Decimal(request.form["value"])
        contra_account_name = request.form["contra_account_name"]
        sign = int(request.form["sign"])
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
        transaction = book.transactions.get(guid=guid)

        if account.placeholder:
            raise BadRequest(f"{account.fullname} is a placeholder")

        if contra_account.placeholder:
            raise BadRequest(f"{contra_account.fullname} is a placeholder")

        if len(transaction.splits) > 2:
            raise BadRequest(f"Can not edit transactions with more than 2 splits.")

        if value < 0:
            raise BadRequest(f"Value {value} must not be negative")
        value = sign*value

        # TODO: Support accounts with different currencies
        assert account.commodity == contra_account.commodity, (
            f"Incompatible accounts: {account.commodity} != {contra_account.commodity}."
            "Transaction form in account.j2 should not have allowed this."
        )

        transaction.description = description
        transaction.post_date = transaction_date
        transaction.splits = [
            Split(account=account, value=value),
            Split(account=contra_account, value=-value),
        ]

        book.save()

        return redirect(account_url(account))


@bp.route("/del_transaction", methods=["POST"])
@requires_auth
def del_transaction():
    """Delete an existing Transaction.

    All parameters are read from `request.form`.

    :param guid: GUID of the transaction to be deleted
    :param account_name: The Account from which the deletion was initiated
    """
    try:
        guid = request.form["guid"]
        account_name = request.form["account_name"]
    except (InvalidOperation, ValueError) as e:
        raise BadRequest(f"Invalid form parameter: {e}") from e

    with open_book(
        uri_conn=app.config.DB_URI(*get_db_credentials()),
        readonly=False,
        do_backup=False,
    ) as book:
        account = get_account(book, fullname=account_name)
        transaction = book.transactions.get(guid=guid)

        book.delete(transaction)

        book.save()

        return redirect(account_url(account))

@bp.route("/accounts/<guid>", methods=["POST"])
@requires_auth
def edit_account(guid):
    """Edit an existing account.

    All parameters are read from `request.form` except for guid.

    :param guid: GUID of the account to edit
    :param name: New name for the account
    :param code: New code for the account
    :param description: New description for the account
    :param parent: The GUID of the new parent account
    :param account_type: The name of the new account type
    :param commodity: The mnemonic of the new commodity
    :param commodity_scu: The smallest fraction for the commodity
    :param placeholder: The placeholder state of the account
    :param hidden: The hidden state of the account
    """
    try:
        name = request.form["name"]
        code = request.form["code"]
        description = request.form["description"]
        parent = request.form["parent"]
        account_type = request.form["type"]
        commodity = request.form["commodity"]
        commodity_scu = int(request.form["commodity_scu"])
        placeholder = 1 if request.form.get("placeholder", "off") == "on" else 0
        hidden = 1 if request.form.get("hidden", "off") == "on" else 0
    except (InvalidOperation, ValueError) as e:
        raise BadRequest(f"Invalid form parameter: {e}") from e

    with open_book(
        uri_conn=app.config.DB_URI(*get_db_credentials()),
        readonly=False,
        do_backup=False,
    ) as book:
        account = get_account(book, guid=guid)
        account.name = name
        account.code = code
        account.description = description
        account.type = account_type
        account.commodity = book.commodities.get(namespace='CURRENCY', mnemonic=commodity)
        account.placeholder = placeholder
        account.hidden = hidden

        # workaround for piecash book.accounts not including root
        account.parent = (
            book.root_account
            if parent == book.root_account.guid
            else get_account(book, guid=parent)
        )
        account.commodity_scu = (
            None # piecash use commodity default
            if commodity_scu == -1
            else commodity_scu
        )
        book.save()

        return redirect(account_url(account))
