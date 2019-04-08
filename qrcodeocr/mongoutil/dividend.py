# -*- coding: utf-8 -*-
# import configparser

import math
import time
from datetime import datetime
from random import uniform
import os

import numpy as np
import pandas as pd
from qrcodeocr.common import configure
from pandas import DataFrame
from pymongo import MongoClient
from qrcodeocr.util import cache_util
from qrcodeocr.util import utility
from qrcodeocr.mongoutil.mongoutil import MongoUtil

import logging

logger = logging.getLogger(__name__)

class Dividend(MongoUtil):

    # 指定日淨值：依api的end_date配How_fundNavN.date,取得How_fundNavN.date<=指定日的最近一筆How_fundNavN.nav
    def get_fund_nav(self, fund_id, date, direction='$lte'):

        if direction == "$lte":
            sort = -1
        else:
            sort = 1

        self.setCollection("How_fundNavN")
        post = self.find_one({"howfundId": fund_id, "date": { direction: date } },
                         {"_id":0, "date": 1, "nav": 1},
                         sortExpression=[('date', sort)], limitCount=1)

        if post is None:
            return None, None
        else:
            return post['nav'], post['date']


    def get_fund_dividend(self, fund_id, start_date, end_date):
        # query mongodb

        self.setCollection("How_fundDivN")
        post = self.find({"howfundId": {"$in": [fund_id]}, "date": {"$gte": start_date, "$lte": end_date}} )

        df = pd.DataFrame(list(post))
        if df.empty:
            return df

        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        df = df.set_index("date")

        return df



    def list_fund_dividend(self, fund_list, start_date, end_date):
        # query mongodb
        self.setCollection("How_fundDivN")
        post = self.find({"howfundId": {"$in": fund_list}, "date": {"$gte": start_date, "$lte": end_date}} )

        dfs = pd.DataFrame(list(post))
        if dfs.empty:
            return dfs

        dfs['date'] = pd.to_datetime(dfs['date'], format='%Y%m%d')
        dfs = dfs.set_index("date").sort_index()
        dfs.pop('_id')
        return dfs


    def get_fund_dividendFrequency(self, howfund_id):

        # query mongodb
        projection = {"_id": 0, "dividendFrequency": 1}

        self.setCollection("How_fundDetailN")
        post = self.find_one({"howfundId": howfund_id}, projection)
        if post is None:
            return None
        else:
            return post['dividendFrequency']


    def get_fund_lastDivFrequency(self, howfund_id):

        # query mongodb
        projection = {"_id": 0, "lastDivFrequency": 1}

        self.setCollection("API_fundData")
        post = self.find_one({"howfundId": howfund_id}, projection)
        if post is None:
            return None
        else:
            return post['lastDivFrequency']