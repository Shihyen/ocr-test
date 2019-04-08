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

class FundDetails(MongoUtil):
    """mongo utility"""

    def get_fund_details(self, howfund_id, gtedate = None):

        # query mongodb
        projection = {"_id": 0, "provide": 0, "constituents": 0, "dividends": 0, "dailyNav": 0}

        self.setCollection("API_fundData")
        if gtedate is None:
            post = self.find_one({"howfundId": howfund_id, "provide": True}, projection)
        else:
            post = self.find_one({"howfundId": howfund_id, "provide": True, "date": {"$gte": gtedate }}, projection)

        if post is None:
            return None

        if 'navStatistics' in post and 'Beta1Y' in post['navStatistics'] and (post['navStatistics']['Beta1Y'] == '' or post['navStatistics']['Beta1Y'] is None):
            post['navStatistics']['Beta1Y'] = ""
        if 'navStatistics' in post and 'Sharpe1Y' in post['navStatistics'] and (post['navStatistics']['Sharpe1Y'] == '' or post['navStatistics']['Sharpe1Y'] is None):
            post['navStatistics']['Sharpe1Y'] = ""

        # if (post['dividendFrequency'] == "" or post['dividendFrequency'] is None) and 'lastDivFrequency' in post:
        #     post['dividendFrequency'] = post['lastDivFrequency']

        post['lastDivYield'] = utility.convert_float_to_percent(post['lastDivYield'])

        for col in post['navStatistics']:
            if col in ['Rr1w', 'RrThisYear','Rr2Y','Rr1Y','Rr6M','lastOneDayProfitRate','Rr3M']:
                post['navStatistics'][col] = utility.convert_float_to_percent(post['navStatistics'][col])

        return post


    def get_fundlist_details(self, fund_id_list):

        # query mongodb
        projection = {"_id": 0, "algorithmCategory": 1,"howfundId": 1, "majorHowfundId": 1, "fundType": 1, "fundShortName": 1}

        self.setCollection("API_fundData")
        post = self.find({"howfundId": {"$in": fund_id_list }, "provide": True}, projection)
        if post is None:
            return None

        return post

    @cache_util.cached(timeout=86400)
    def get_fund_count(self):
        self.setCollection("API_fundData")
        return self.find({}).count()

    def list_fund_briefs(self, skip=0, limit=100000):

        # query mongodb
        projection = {"_id": 0, "howfundId": 1, "chineseFullName": 1, "fundShortName":1, "strategy": 1, "issuingAgency": 1,
                      "agentChineseName": 1, "englishFullName": 1, "currencyType": 1, "navStatistics.Rr1Y": 1, "isOverseaFund":1,
                      "maxNavDate":1, "provide":1, "generalAgent":1 , "generalIssuer":1, "fundType": 1, "algorithmCategory": 1, "isinCode": 1, "riskLevel": 1, "majorHowfundId": 1}

        self.setCollection("API_fundData")
        count = self.get_fund_count()
        post = self.find({}, projection).sort('howfundId', 1).skip(skip).limit(limit)

        df = pd.DataFrame(list(post))

        if df.empty:
            logger.info("empty record of fundbriefs %s", count )
            return df, count

        df.set_index('howfundId', inplace=True)

        #20171025 shawn change None to ""
        #df['Rr1Y'] = [utility.format_float(n['Rr1Y']) if type(n) == dict and n['Rr1Y'] is not None and n['Rr1Y'] != 'null' else "" for n in df['navStatistics']]
        df['Rr1Y'] = [utility.convert_float_to_percent(n['Rr1Y']) if type(n) == dict and n['Rr1Y'] is not None and n['Rr1Y'] != 'null' else "" for n in df['navStatistics']]
        df['riskLevel'] = [self.processRiskLevel(r) for r in df['riskLevel']]

        df.pop('navStatistics')

        # fillna for maxNavDate
        df['maxNavDate'] = df['maxNavDate'].fillna("")
        logger.debug("= set index ==")
        return df, count


    def processRiskLevel(self, rl):
        rl = str(rl).replace("R","")
        if rl == "" or int(float(rl)) == 0:
            return None

        return int(float(rl))


    @cache_util.cached(timeout=3600)
    def get_fund_related_fund(self, howfund_id, limit):

        self.setCollection("API_fundData")
        _post = self.find_one({"howfundId": howfund_id, "provide": True, "adjCategory": {"$ne": "" }},
                             {"_id": 0, "fundType": 1, "adjCategory": 1, "adjCategoryLevel2": 1})

        if (_post == None):
            return pd.DataFrame(list([]))

        df = self.list_fund_by_category(level1=_post.get('fundType'), level2=_post.get('adjCategoryLevel2'),
                                         level4=_post.get('adjCategory'))

        if df is None:
            return df
        # sorting and limit
        df = df.sort_values(['Rr1Y'], ascending=False).head(limit)
        # format float columns

        for c in df.columns:
            if c in ['lastOneDayProfitRate', 'Rr1w', 'Rr1M', 'Rr3M', 'Rr6M', 'Rr1Y', 'Rr2Y']:
                # df[c] = [utility.format_pct_float(r) for r in df[c]]
                df[c] = [r for r in df[c]]
            elif c in ['lastNav']:
                df[c] = [str(float(r)) for r in df[c]]
            else:
                df[c] = [utility.format_float(r) for r in df[c]]

        df.reset_index(inplace=True)
        df = df.replace(['NaN', 'nan', '', 'None', list([])], np.nan)
        df = df.fillna("")
        #df = df.replace(np.nan, '', regex=True)


        return df

    @cache_util.cached(timeout=86400)
    def get_tw_holiday(self, trade_date):

        self.setCollection("ETL_invHoliday")
        query = { 'data': {"$elemMatch":{'country': "臺灣"}}, 'date': {'$gt': trade_date}}

        post = self.find(query, {'date':1})

        res = []
        for item in post:
            res.append(item['date'])
        return res

    @cache_util.cached(timeout=3600)
    def get_agent_recommand_fund(self, fund_id, gtedate = None):

        self.setCollection("SMT_agentRecommendFund")
        query = {"howfundId": fund_id}
        if gtedate is not None:
            query.update({"recommendDate": {"$gte": gtedate}})

        _post = self.find(query,
                             {"_id": 0, "agentId": 1, "recommendDate": 1, "agentType": 1})

        df = pd.DataFrame(list(_post))
        if df.empty:
            return df

        df = df.sort_values(["recommendDate"], ascending=False).groupby(["agentId"]).first()

        self.setCollection("SMT_recommendFundAgency")
        _post = self.find({"fundCompanyId": {"$in": [r for r in df.index.values]}},
                             {"_id": 0, "fundCompanyId": 1, "fundCompanyName": 1})

        if _post is None:
            df['fundCompanyName'] = df['agentId']
            return df

        name_df = pd.DataFrame(list(_post))
        name_df = name_df.set_index("fundCompanyId")

        df = df.join(name_df, how='left')

        df['fundCompanyName'] = df['fundCompanyName'].fillna(df.index.to_series())

        return df

    def get_fund_expected_trade_date(self, howfund_list):
        # query mongodb
        self.setCollection("SMT_fundTradingDetail")
        _post = self.find({"howfundId": {"$in": howfund_list} },
                          {"_id": 0, "howfundId": 1,
                           "allowBaseDate": 1, "allowSettlementDate": 1, "redeemBaseDate": 1, "redeemSettlementDate": 1})

        _df = pd.DataFrame(list(_post))
        if _df.empty:
            return _df

        _df = _df.set_index(['howfundId'])


        return _df

    def get_majorfundid_by_tejCategory(self, tejCategory):
        self.setCollection("How_fundDetailN")

        _post = self.find({"tejCategory": tejCategory},
                          {"_id": 0, "majorHowfundId": 1})
        res = []
        for item in _post:
            res.append(item['majorHowfundId'])

        res = list(set(list(res)))
        return res

    def get_majorfundid_by_algorithmCategory(self, algorithmCategory):
        self.setCollection("How_fundDetailN")

        _post = self.find({"algorithmCategory": algorithmCategory},
                          {"_id": 0, "majorHowfundId": 1})
        res = []
        for item in _post:
            res.append(item['majorHowfundId'])

        res = list(set(list(res)))
        return res