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

class APPService(MongoUtil):
    """mongo utility"""

    def get_agentId_list(self, howfund_id, gtedate = None):

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

        if post['dividendFrequency'] != "" and 'lastDivFrequency' in post:
            post['dividendFrequency'] = post['lastDivFrequency']

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



    def get_agent_recommend_list(self, agentId='', gtedate = None):



        self.setCollection("SMT_agentRecommendFund")
        if agentId != '':
            pipeline = [
                {
                    "$match": {
                        "agentId": agentId
                    }
                }
            ]
        else:
            pipeline = []


        pipeline.extend([
            {
                "$sort": {
                    "agentId": -1
                }
            }
        ])

        if gtedate is not None:
            pipeline.extend([
                {
                    "$match": {
                        "recommendDate": {"$gte": gtedate}
                    }
                }
            ])

        pipeline.extend([
            {
                "$group": {
                    "_id":{
                        "agentId": "$agentId",
                    },
                    "LastRecommendDate": {
                            "$last": "$recommendDate"
                    },
                    "agentType": {
                        "$last": "$agentType"
                    },
                    "howFundId":{
                        "$push":{
                            "howfundId": "$howfundId",
                            "recommendDate": "$recommendDate",
                        }
                    }
                }

            },
            {
                "$project": {
                    "_id": 0,
                    "agentId": "$_id.agentId",
                    "LastRecommendDate":"$LastRecommendDate",
                    "agentType": "$agentType",
                    "howFundId":{
                      "$filter":{
                        "input": "$howFundId",
                        "as": "howFundId",
                        "cond": {
                          "$eq":["$$howFundId.recommendDate", "$LastRecommendDate"]
                        }
                      }
                    }
                }
            }
        ])

        post = self.aggregate_pipeline(pipeline)

        return post


    def get_agent_name(self, agentlist):

        projection = {"_id": 0, "fundCompanyName": 1,"fundCompanyId": 1}

        self.setCollection("SMT_recommendFundAgency")
        post = self.find({"fundCompanyId": {"$in": agentlist }}, projection)
        if post is None:
            return None

        return list(post)


    def get_majorHowFundId(self, fund_list):

        projection = {"_id": 0, "majorHowfundId": 1,"howfundId": 1}

        self.setCollection("How_fundDetailN")
        post = self.find({"howfundId": {"$in": fund_list }, "majorHowfundId": { "$ne": "" } }, projection)
        if post is None:
            return None
        majorFundList = {}
        for item in post:
            majorFundList[item['howfundId']] = item['majorHowfundId']

        return majorFundList

    def get_daily_created_price(self, trade_date):

        nextday = utility.get_formatterd_delta_date_bystr(trade_date, days=1)
        trade_date_last_month = utility.get_formatterd_delta_date_bystr(trade_date, days=-30)
        # query mongodb
        self.setCollection("How_fundNavN")
        post = self.find({"$and": [ {"createdAt": { "$gte": trade_date }}, {"createdAt": { "$lt": nextday }}, {"date": {"$gt": trade_date_last_month }}] },
                         {"_id":0, "howfundId": 1, "date": 1, "nav": 1} )


        df = pd.DataFrame(list(post))

        return df

    def list_currency_index(self):
        self.setCollection("SMT_idxSource")
        _post = self.find({'howIdxType1': '全球主要匯率', 'englishName': {"$regex": ".*USD.*"}},
                          {"_id": 0, "howIdxId": 1, "englishName": 1})

        _df = pd.DataFrame(list(_post))
        _df = _df.set_index(['howIdxId'])

        return _df

