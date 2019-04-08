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

class Statistics(MongoUtil):
    """mongo utility"""

    def get_fund_latest_price_day(self, howfundId):

        self.setCollection("How_fundNavN")
        query = {'howfundId': {'$in': [howfundId]}}
        projection = {'_id': 0, 'howfundId': 1, 'date': 1, 'nav': 1}
        sort = [('date', -1)]
        _p = self.find_one(query, projection, sort)
        if _p is None:
            return _p

        return _p['date']



    #20171017 shawn  start day end day這樣取如果當下沒資料 不會剛好一整年 計算時要用有取道的天數
    def get_index_hs_return_0(self, howIdxId, start_date, end_date):
        # query mongodb
        self.setCollection("HOW_index_hs")
        post = self.find({"howIdxId": howIdxId, 'tradeDate': {'$gte': start_date, '$lte': end_date}},
                         {'_id':0, "tradeDate": 1, "quote": 1})

        df = pd.DataFrame(list(post))
        if df.empty:
            return df

        df = df.rename_axis({"tradeDate": "date", "quote": "price"}, axis="columns")

        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        df = df.set_index("date").sort_index()
        df = df[start_date:end_date]

        # remove this after the datatype is fixed in mongo
        df['price'] = [float(p) for p in df['price']]

        return df




