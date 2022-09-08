"""Manage commodities in the GnuCash database."""
from flask import (
    Blueprint,
    current_app as app,
)
import click
from babel import numbers
from piecash.core.commodity import Price

from .utils.gnucash import open_book

bp = Blueprint("commodities", __name__, url_prefix="/commodities")


def latest_price(commodity):
    """Get latest known price for commodity.

    :param commodity: The commodity in question. Must be different from the books
      default currency

    :returns: Latest known price of the commodity in the books default currency

    """
    return commodity.prices.order_by(Price.date.desc()).limit(1).first()


def format_price(price):
    """Format price with currency according to current locale.

    :param price: The price in question
    :returns: Human-readable string

    """
    return numbers.format_currency(price.value, price.currency.mnemonic)


@bp.cli.command("list")
@click.option("--namespace", help="Filter by namespace")
@click.pass_context
def list_commodities(ctx, namespace):
    """List all used commodities.

    :param ctx: Click application context
    :param namespace: Filter by namespace

    """
    opts = ctx.find_root().params

    with open_book(
        uri_conn=app.config.DB_URI(opts.get("username"), opts.get("password")),
        readonly=True,
        open_if_lock=True,
    ) as book:
        if namespace:
            commodities = book.commodities(namespace=namespace)
        else:
            commodities = book.commodities

        for commodity in commodities:
            print(f"{commodity.namespace}:{commodity.mnemonic} ({commodity.cusip})")
            print(f"  Traded fraction: {1/commodity.fraction}")

            if commodity.quote_flag:
                print(f"  Quote Source: {commodity.quote_source} (ignored)")

            price = latest_price(commodity)
            if price:
                print(
                    f"  Latest known price: {format_price(price)}"
                    f" ({price.source}@{price.date})"
                )


@bp.cli.command("update_prices")
@click.pass_context
def update_prices(ctx):
    """Update prices for all commodities for which it is enabled.

    :param ctx: Click application context

    """
    opts = ctx.find_root().params

    with open_book(
        uri_conn=app.config.DB_URI(opts.get("username"), opts.get("password")),
        readonly=False,
        do_backup=False,
        open_if_lock=False,
    ) as book:

        old_prices = {}

        # Update prices (relative to book.default_currency) of all relevant
        # commodities
        for commodity in book.commodities:
            old_prices[commodity] = latest_price(commodity)
            if commodity.quote_flag and commodity != book.default_currency:
                commodity.update_prices()

        # Fetched prices are only visible after save, so we do it now and print the
        # changes later
        book.save()

        # Print price changes
        for commodity in book.commodities:
            old_price = old_prices[commodity]
            new_price = latest_price(commodity)
            if new_price:
                if old_price and new_price.date > old_price.date:
                    print(
                        f"New price for {commodity.mnemonic}:"
                        f" {format_price(old_price)}@{old_price.date}"
                        f" -> {format_price(new_price)}@{new_price.date}"
                    )
                else:
                    print(
                        f"Price for {commodity.menmonic}:"
                        f" {format_price(new_price)}@{new_price.dat}"
                    )
