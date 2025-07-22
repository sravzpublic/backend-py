#!/usr/bin/env python
import datetime
from src.services import mdb
from src.util import logger, settings, helper, aws_cache
from bson.objectid import ObjectId

class Util(object):
    """Updates portfolio PNL"""

    def __init__(self):
        self.logger = logger.RotatingLogger(__name__).getLogger()
        self.mdb_engine = mdb.engine()

    def get_portfolio_assets(self, name, user_id):
        '''
            returns list of portfolio assets
        '''
        self.logger.info(
            "Finding portfolio by name {0} and user ID {1}".format(name, user_id))
        portfolios = self.mdb_engine.get_collection_items(self.mdb_engine.PORTFOLIOS_COLLECTION,
                                                          find_clause={"user": ObjectId(user_id), "name": name}, iterator=True)
        for portfolio in portfolios:
            portfolio_assets = self.mdb_engine.get_collection_items(self.mdb_engine.PORTFOLIO_ASSETS_COLLECTION,
                                                                    find_clause={"_id": {"$in": [id for id in portfolio["portfolioassets"]]}}, iterator=True)
            return [portfolio_asset["SravzId"] for portfolio_asset in portfolio_assets]

    def get_portfolio_assets_weights(self, name, user_id):
        '''
            returns list of portfolio assets
        '''
        self.logger.info(
            "Finding portfolio by name {0} and user ID {1}".format(name, user_id))
        portfolios = self.mdb_engine.get_collection_items(self.mdb_engine.PORTFOLIOS_COLLECTION,
                                                          find_clause={"user": ObjectId(user_id), "name": name}, iterator=True)
        for portfolio in portfolios:
            portfolio_assets = self.mdb_engine.get_collection_items(self.mdb_engine.PORTFOLIO_ASSETS_COLLECTION,
                                                                    find_clause={"_id": {"$in": [id for id in portfolio["portfolioassets"]]}}, iterator=True)
            return [(portfolio_asset["SravzId"],portfolio_asset["weight"]) for portfolio_asset in portfolio_assets]