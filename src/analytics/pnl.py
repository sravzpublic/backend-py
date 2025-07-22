#!/usr/bin/env python
import datetime
from src.services import mdb
from src.util import logger, settings, helper
import traceback


class engine(object):
    """Updates portfolio PNL"""

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()

    def update(self):
        _logger = logger.RotatingLogger(__name__).getLogger()
        mdb_engine = mdb.engine()
        portfolio_collection = mdb_engine.get_collection('portfolios')
        portfolioassets_collection = mdb_engine.get_collection(
            'portfolioassets')
        portfolio_collection_items = mdb_engine.get_collection_items(
            'portfolios', iterator=True)
        quotes_dict = {}
        for quote_type in ['currency', 'rates', 'crypto', 'stocks', 'index', 'futures']:
            quotes = mdb_engine.get_collection_items(
                'quotes_{0}'.format(quote_type), iterator=False, cache=False)
            [quotes_dict.update({quote["SravzId"].lower(): quote})
             for quote in quotes if quote.get("SravzId").lower()]
        for portfolio in portfolio_collection_items:
            try:
                current_portfolio_value = 0
                current_portfolio_pnl = 0
                weighted_current_portfolio_pnl_percent = 0
                portfolioAssets = portfolio["portfolioassets"]
                portfolioassets_collection_items = mdb_engine.get_collection_items('portfolioassets', find_clause={"_id": {"$in": [id for id
                                                                                                                                   in portfolioAssets]}}, iterator=True)
                for portfolio_asset in portfolioassets_collection_items:
                    asset_sravz_id = portfolio_asset["SravzId"]
                    asset_quote = quotes_dict.get(
                        helper.get_generic_sravz_id(asset_sravz_id))
                    if not asset_quote:
                        _logger.warn("Could not get quote for sravz_id %s generic_id %s" % (
                            asset_sravz_id, helper.get_generic_sravz_id(asset_sravz_id)))
                        continue
                    # Take absolute value of quantity
                    current_asset_price = helper.util.getfloat(helper.util.translate_string_to_number(
                        asset_quote.get("Last"))) * abs(portfolio_asset.get("quantity")) * helper.util.getfloat(portfolio_asset.get("weight")) / 100
                    purchase_asset_price = helper.util.getfloat(helper.util.translate_string_to_number(portfolio_asset.get(
                        "purchaseprice"))) * abs(portfolio_asset.get("quantity")) * helper.util.getfloat(portfolio_asset.get("weight")) / 100
                    # Value == Current Price
                    portfolio_asset["currentprice"] = helper.util.getfloat(
                        helper.util.translate_string_to_number(asset_quote.get("Last")))
                    portfolio_asset["purchasevalue"] = purchase_asset_price
                    portfolio_asset["currentvalue"] = current_asset_price
                    portfolio_asset["pnl"] = current_asset_price - purchase_asset_price
                    portfolio_asset["pnlpercent"] = (
                        current_asset_price - purchase_asset_price)/purchase_asset_price * 100 * abs(portfolio_asset.get("weight"))/portfolio_asset.get("weight")
                    portfolio_asset["pnlcalculationdt"] = asset_quote.get(
                        "pricecapturetime")
                    current_portfolio_value = current_asset_price + current_portfolio_value
                    current_portfolio_pnl = portfolio_asset["pnl"] + \
                        current_portfolio_pnl
                    weighted_current_portfolio_pnl_percent = weighted_current_portfolio_pnl_percent + (portfolio_asset["pnlpercent"] * abs(portfolio_asset.get("weight"))/100)
                    portfolioassets_collection.replace_one(
                        {"_id": portfolio_asset["_id"]}, portfolio_asset)
                    print(f"Current price {current_asset_price} | purchase price {purchase_asset_price} | quantity {abs(portfolio_asset.get('quantity'))} | weight {portfolio_asset.get('weight')} | pnl {portfolio_asset.get('pnl')}")
                portfolio["value"] = current_portfolio_value
                # Add pnl direction to match the weight sign long/short
                portfolio["pnl"] = current_portfolio_pnl
                portfolio["pnlpercent"] = weighted_current_portfolio_pnl_percent
                portfolio["pnlcalculationdt"] = datetime.datetime.now(datetime.UTC)
                portfolio_collection.replace_one(
                    {"_id": portfolio["_id"]}, portfolio)
                self.logger.info("Processed portfolio id: %s name: %s PNL" % (
                    portfolio.get("_id"), portfolio.get("name")), exc_info=True)
            except:
                self.logger.error("Could not process portfolio id: %s name: %s" % (
                    portfolio.get("_id"), portfolio.get("name")), exc_info=True)
