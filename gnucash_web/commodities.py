from datetime import date, timedelta

from flask import (
    Blueprint,
    current_app as app,
)
import click
from babel import numbers
from piecash.core.commodity import Price

from .utils.gnucash import open_book

bp = Blueprint('commodities', __name__, url_prefix='/commodities')

def latest_price(commodity):
    return commodity.prices.order_by(Price.date.desc()).limit(1).first()

def format_price(price):
    return numbers.format_currency(price.value, price.currency.mnemonic);

@bp.cli.command('list')
@click.option('--namespace', help='Filter by namespace')
@click.pass_context
def list_commodities(ctx, namespace):
    """List Commodities"""
    opts = ctx.find_root().params

    with open_book(uri_conn=app.config.DB_URI(opts.get('username'), opts.get('password')),
                   readonly=True, open_if_lock=True) as book:
        if namespace:
            commodities = book.commodities(namespace=namespace)
        else:
            commodities = book.commodities

        for commodity in commodities:
            print(f'{commodity.namespace}:{commodity.mnemonic} ({commodity.cusip})')
            print(f'  Traded fraction: {1/commodity.fraction}')

            if commodity.quote_flag:
                print(f'  Quote Source: {commodity.quote_source} (ignored)')

            price = latest_price(commodity)
            if price:
                print(f'  Latest known price: {numbers.format_currency(price.value, price.currency.mnemonic)}'
                      f' ({price.source}@{price.date})')

@bp.cli.command('update_prices')
@click.pass_context
def update_prices(ctx):
    """Update prices for all commodities for which it is enabled"""
    opts = ctx.find_root().params

    with open_book(uri_conn=app.config.DB_URI(opts.get('username'), opts.get('password')),
                   readonly=False, do_backup=False, open_if_lock=False) as book:

        old_prices = {}
        for commodity in book.commodities:
            old_prices[commodity] = latest_price(commodity)
            if commodity.quote_flag and commodity != book.default_currency:
                commodity.update_prices()

        # Fetched prices are only visible after save, so we do it now and print the
        # changes later
        book.save()

        for commodity in book.commodities:
            old_price = old_prices[commodity]
            new_price = latest_price(commodity)
            if new_price:
                if old_price:
                    if new_price.date > old_price.date:
                        print(f'New price for {commodity.mnemonic}:'
                              f' {format_price(old_price)}@{old_price.date}'
                              f' -> {format_price(new_price)}@{new_price.date}')
                else:
                    print(f'Price for {commodity.namespace}:{commodity.menmonic}:'
                          f' {format_price(new_price)}@{new_price.dat}')


