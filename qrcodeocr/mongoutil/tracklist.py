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

class Tracklist(MongoUtil):
    """mongo utility"""

    # [1112] 新增追蹤列表_指數_績效api - 取得多筆 指數名稱  by Shihyen
    def get_index_name(self, howIdxId):
        # query mongodb
        self.setCollection("SMT_idxSource")
        post = self.find({
                            "howIdxId" : {
                                "$in" : howIdxId
                            }
                        }, {
                            "howIdxId": 1,
                            "howIdxName" : 1,
                            "englishName" : 1,
                            "shortName" : 1,
                            "englishShortName" : 1
                        })
        return post

    # [1111] 新增追蹤列表_基金_績效api - 取得多筆 基金名稱  by Shihyen
    def get_fund_name(self, howfundId):
        # query mongodb

        self.setCollection("API_fundData")
        post = self.find({
                            "howfundId" : {
                                "$in" : howfundId
                            }
                        }, {
                            "howfundId": 1,
                            "ratings": 1,
                            "chineseFullName" : 1,
                            "currencyType" : 1,
                            "dividend" : 1,
                            "dividendFrequency" : 1,
                            "englishFullName": 1,
                            "fundShortName": 1,
                            "riskLevel": 1,
                            "navStatistics.lastDayChange": 1,
                            "navStatistics.lastOneDayProfitRate": 1,
                            "navStatistics.lastNav": 1,
                            "navStatistics.Beta1Y": 1,
                            "navStatistics.Sharpe1Y": 1,
                            "maxNavDate": 1,
                            "lastDivFrequency": 1
            })


        return post


	# [1112] 新增追蹤列表_指數_績效api - 取得多筆 指數名稱  by Shihyen
    def get_multi_index_hs_return_0(self, howIdxId, start_date, end_date):
        # query mongodb
        self.setCollection("HOW_index_hs")

        post = self.find({"howIdxId": {'$in': howIdxId}, 'tradeDate': {'$gte': start_date, '$lte': end_date}},
                         {'_id':0, "tradeDate": 1, "quote": 1, "howIdxId": 1, "change": 1, "changePercent": 1})


        df = pd.DataFrame(list(post))
        df = df.rename({"tradeDate": "date", "quote": "price"}, axis="columns")

        if df.empty:
            return df

        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        df = df.set_index("date").sort_index()
        df = df[start_date:end_date]

        # remove this after the datatype is fixed in mongo
        df['price'] = [float(p) for p in df['price']]

        return df

