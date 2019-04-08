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

#from hoppdataapi.util.logger import logger
#logger = logger()
import logging
logger = logging.getLogger(__name__)

class MongoUtil(object):
    """mongo utility"""

    def __init__(self):
        mongo_url = 'mongodb://{}:{}@{}:{}/{}'.format(configure.mongo_user, configure.mongo_pw, configure.mongo_host,
                                                      configure.mongo_port, configure.mongo_auth_db)
        self.client = MongoClient(mongo_url, minPoolSize=10)
        self.db = self.client[configure.mongo_db]
        self.logEnabled = configure.mongo_logEnabled

    def __del__(self):
        self.client.close()

    def setCollection(self, collection):
        try:
            self.collection = self.db[collection]
            if (self.logEnabled):
                message = '[MONGOLOG] set collection to: [%s]' % (collection)
                logger.info(message)
            return ""
        except Exception as e:
            logger.error('set Collection(%s) unexpected error: %s.' % (collection, str(e)))

    def log(self, st, query, projection=None):
        if (self.logEnabled):
            timediff = int((time.time() - st) * 1000)
            message = '[MONGOLOG] Time(ms):[%s] Query:[%s] Projection:[%s]' % (timediff, query, projection)
            logger.info(message)

    def find(self, query={}):
        st = time.time()
        try:
            result = self.collection.find(query)

        except Exception as e:
            logger.error('some fields name are wrong in ' + query + "," + str(e))
            return None

        self.log(st, query)
        return result

    def find(self, query={}, projection=None, sortExpression=None, limitCount=1):
        st = time.time()
        try:
            if sortExpression == None:
                if projection == None:
                    result = self.collection.find(query)
                else:
                    result = self.collection.find(query, projection)
            else:
                if projection == None:
                    result = self.collection.find(query).sort(sortExpression).limit(limitCount)
                else:
                    result = self.collection.find(query, projection).sort(sortExpression).limit(limitCount)

        except Exception as e:
            logger.error('some fields name are wrong in ' + str(query) + "," + str(e))
            return None

        self.log(st, query, projection)
        return result

    def aggregate_simple(self, query):  # 查詢
        st = time.time()
        try:
            result = self.collection.aggregate(query)

        except Exception as e:
            logger.error('some fields name are wrong in ' + query + "," + str(e))
            return None

        self.log(st, query)
        return list(result)

    def aggregate(self, unwindField, query={}, projection={}, sortExpression=None, limitCount=1):
        st = time.time()
        try:
            if projection == {}:
                result = self.collection.aggregate(
                    pipeline=[{"$unwind": unwindField}, {"$match": query}, {"$sort": sortExpression},
                              {"$limit": limitCount}])
            else:
                result = self.collection.aggregate(
                    pipeline=[{"$unwind": unwindField}, {"$match": query}, {"$project": projection},
                              {"$sort": sortExpression}, {"$limit": limitCount}])

        except Exception as e:
            logger.error('some fields name are wrong in aggregate,' + str(e))
            return None

        self.log(st, query)
        return list(result)

    def aggregate_pipeline(self, pipeline):
        st = time.time()
        try:
            result = self.collection.aggregate(pipeline=pipeline)
        except Exception as e:
            logger.error('some fields name are wrong in pipeline,' + str(e))
            return None
        self.log(st, pipeline)
        return list(result)

    def find_one(self, query={}, projection=None, sortExpression=None, limitCount=1):
        st = time.time()
        try:
            if sortExpression == None:
                result = self.collection.find_one(query, projection)
            else:
                result = self.collection.find_one(query, projection, sort=sortExpression, limit=limitCount)

        except Exception as e:
            logger.error('some fields name are wrong in ' + str(query) + "," + str(e))
            return None

        self.log(st, query, projection)
        return result

    def insert(self, data):
        try:
            if type(data) is not dict:
                if self.PrintErrorMessage:
                    print('the type of INSERT data isn\'t dict')
                self.ErrorMessage = 'the type of INSERT data isn\'t dict'
                return -1

            # insert會返回新插入數據的_id
            result = self.collection.insert(data)
            return result  # python use result.modified_count
        except Exception as e:
            if self.PrintErrorMessage:
                print("INSERT unexpected error: " + str(e))
            self.ErrorMessage = "INSERT unexpected error: " + str(e)
            return -1

    def remove(self, data):  # 刪除
        try:
            if type(data) is not dict:
                if self.PrintErrorMessage:
                    print('the type of REMOVE data isn\'t dict')
                self.ErrorMessage = 'the type of REMOVE data isn\'t dict'
                return -1

            result = self.collection.remove(data)
            return result['n']  # python use result.modified_count
        except Exception as e:
            if self.PrintErrorMessage:
                print("REMOVE unexpected error: " + str(e))
            self.ErrorMessage = "REMOVE unexpected error: " + str(e)
            return -1

    def update_simple(self, data, setdata):  # 修改
        try:
            if type(data) is not dict or type(setdata) is not dict:
                if self.PrintErrorMessage:
                    print('the type of UPDATE data isn\'t dict')
                self.ErrorMessage = 'the type of UPDATE data isn\'t dict'
                return -1

            result = self.collection.update(data, setdata)
            return result['n']  # python use result.modified_count
        except Exception as e:
            if self.PrintErrorMessage:
                print("UPDATE unexpected error: " + str(e))
            self.ErrorMessage = "UPDATE unexpected error: " + str(e)
            return -1

    def update(self, data, setdata, operation):  # 修改
        try:
            if type(data) is not dict or type(setdata) is not dict:
                if self.PrintErrorMessage:
                    print('the type of UPDATE data isn\'t dict')
                self.ErrorMessage = 'the type of UPDATE data isn\'t dict'
                return -1

            result = self.collection.update(data, {'$' + operation: setdata})
            return result['n']  # python use result.modified_count
        except Exception as e:
            if self.PrintErrorMessage:
                print("UPDATE unexpected error: " + str(e))
            self.ErrorMessage = "UPDATE unexpected error: " + str(e)
            return -1

    def replace(self, data, setdata):  # 修改
        try:
            if type(data) is not dict or type(setdata) is not dict:
                if self.PrintErrorMessage:
                    print('the type of REPLACE data isn\'t dict')
                self.ErrorMessage = 'the type of REPLACE data isn\'t dict'
                return -1

            result = self.collection.replace_one(data, setdata, True)
            # return result.raw_result['n'] # python use result.modified_count
            return result['n']  # python use result.modified_count
        except Exception as e:
            if self.PrintErrorMessage:
                print("REPLACE unexpected error: " + str(e))
            self.ErrorMessage = "REPLACE unexpected error: " + str(e)
            return -1

    ###########################################################################
    #                                                                         #
    #       Functions below are application specified functions               #
    #                                                                         #
    #       Use prefix: "get_" for single item lookup                         #
    #       Use prefix: "list_" for multiple items lookup                     #
    #                                                                         #
    #       By default, the result will be a DataFrame                        #
    #                                                                         #
    ###########################################################################
    #
    # def get_fund_price(self, howfund_id, start_date, end_date):
    #
    #     # query mongodb
    #     self.setCollection("API_fundData")
    #     data = self.find_one({"howfundId": howfund_id}, {"howfundId": 1, "currencyType": 1, "dailyNav": 1})
    #
    #     date_list = []
    #     price_list = []
    #     # currency_list.append(p['currencyType'])
    #
    #     for d in data['dailyNav']:
    #         date_list.append(d['date'])
    #         price_list.append(d['nav'])
    #
    #     # create price dataframe
    #     price = DataFrame(price_list, index=date_list, columns=['price'])
    #
    #     price.index.names = ['date']
    #     price.index = pd.to_datetime(price.index)
    #
    #     # apply date range
    #     price = price[start_date:end_date]
    #     price = price.fillna(method=configure.dataframe_fillna_method)
    #
    #     price['daily_return'] = price['price'].diff(1).fillna(0)
    #     price['daily_return_cum'] = price['daily_return'].cumsum()
    #     price['daily_return_pct'] = price['price'].pct_change(1).fillna(0)
    #     price['daily_return_pct_cum'] = price['daily_return_pct'].cumsum()
    #
    #     return price

    # 0411

    # def get_fund_return(self, howfund_id, start_date, end_date):
    #     # query mongodb
    #     self.setCollection("API_fundData")
    #     _post = self.find_one({"howfundId": howfund_id},
    #                          {"howfundId": 1, "currencyType": 1, "dailyNav.date": 1, "dailyNav.nav": 1})
    #
    #     _df = pd.DataFrame(_post['dailyNav'])
    #     _df = _df.set_index("date")
    #     _df.index = pd.to_datetime(_df.index)
    #     _df = _df.rename_axis({"nav": "price"}, axis="columns")
    #     _df = _df[start_date:end_date]
    #     _df = _df.fillna(method=configure.dataframe_fillna_method)
    #     _df['daily_return'] = _df['price'].diff(1).fillna(0)
    #     _df['daily_return_cum'] = _df['daily_return'].cumsum()
    #     _df['daily_return_pct'] = _df['price'].pct_change(1).fillna(0)
    #     _df['daily_return_pct_cum'] = _df['daily_return_pct'].cumsum()
    #
    #     return _df

    @cache_util.cached(timeout=3600)
    def list_fund_price_by_date(self, howfund_list, start_date, end_date):

        df = self.list_fund_price(howfund_list)

        df = df[start_date:end_date]

        return df

    @cache_util.cached(timeout=3600)
    def list_fund_price(self, howfund_list):
        # query mongodb
        self.setCollection("API_fundData")
        post = self.find({"howfundId": {"$in": howfund_list}},
                             {"howfundId": 1, "currencyType": 1, "dailyNav.date": 1, "dailyNav.nav": 1})

        df_list = []

        for p in post:
            df = pd.DataFrame(p['dailyNav'])
            df = df.set_index("date")
            df.index = pd.to_datetime(df.index)
            df = df.rename_axis({"nav": p['howfundId']}, axis="columns")

            df_list.append(df)

        dfs = pd.concat(df_list, axis=1, join='outer')
        dfs = dfs.fillna(method=configure.dataframe_fillna_method)

        return dfs

    def list_fund_return(self, howfund_list, start_date, end_date):
        # query mongodb
        self.setCollection("API_fundData")
        _post = self.find({"howfundId": {"$in": howfund_list}},
                             {"howfundId": 1, "currencyType": 1, "dailyNav.date": 1, "dailyNav.nav": 1})

        _df_list = []

        for _p in _post:
            _df = pd.DataFrame(_p['dailyNav'])
            _df = _df.set_index("date")
            _df.index = pd.to_datetime(_df.index)
            _df = _df.rename_axis({"nav": _p['howfundId']}, axis="columns")
            _df = _df[start_date:end_date]
            _df_list.append(_df)

        _dfs = pd.concat(_df_list, axis=1, join='outer')
        _dfs = _dfs.fillna(method=configure.dataframe_fillna_method)

        return _dfs

    def list_fund_price_df(self, howfund_list, start_date, end_date):
        # query mongodb
        self.setCollection("API_fundData")
        _post = self.find({"howfundId": {"$in": howfund_list}},
                             {"howfundId": 1, "currencyType": 1, "dailyNav.date": 1, "dailyNav.nav": 1})

        _df_list = []
        for _p in _post:
            _df = pd.DataFrame(_p['dailyNav'])
            _df['howfundId'] = _p['howfundId']
            _df['date'] = pd.to_datetime(_df['date'])
            _df.set_index("date", inplace=True)
            _df = _df[start_date:end_date]
            _df = _df.rename_axis({"nav": "price"}, axis="columns")
            _df_list.append(_df)

        _dfs = pd.concat(_df_list)
        _dfs = _dfs.reset_index()
        _dfs = _dfs.set_index(["date", "howfundId"])
        _dfs = _dfs.fillna(method=configure.dataframe_fillna_method)
        return _dfs

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

    def get_index_hs_list_return_0(self, howIdxId_list, start_date, end_date):
        # query mongodb
        self.setCollection("HOW_index_hs")
        post = self.find({"howIdxId": { "$in": howIdxId_list}, 'tradeDate': {'$gte': start_date, '$lte': end_date}},
                         {'_id':0, "howIdxId": 1, "tradeDate": 1, "quote": 1})

        df = pd.DataFrame(list(post))
        if df.empty:
            return df

        df = df.rename_axis({"tradeDate": "date", "quote": "price"}, axis="columns")

        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        df = df.set_index("date").sort_index()
        df = df[start_date:end_date]

        # remove this after the datatype is fixed in mongo
        df['price'] = [float(p) for p in df['price']]
        #print(df)
        return df

    def get_pricedf_by_fund(self, howfund_id, start_date, end_date, date_format='%Y-%m-%d'):

        start_date = datetime.strptime(start_date, date_format).strftime('%Y%m%d')
        end_date = datetime.strptime(end_date, date_format).strftime('%Y%m%d')

        price = self.get_fundlist_price2([howfund_id], start_date, end_date)

        return price

    def find_price_by_fundlist(self, howfund_list, start_date, end_date, date_format='%Y-%m-%d'):

        # query mongodb

        # start_date = datetime.strptime(start_date, '%Y-%m-%d')
        # end_date = datetime.strptime(end_date, '%Y-%m-%d')

        start_date = datetime.strptime(start_date, date_format).strftime('%Y%m%d')
        end_date = datetime.strptime(end_date, date_format).strftime('%Y%m%d')

        # query mongodb
        # self.setCollection("How_fundNav")
        # data_list = self.find({"howfundId": {"$in": fundlist}},
        #                       {"howfundId": 1, "dateData.date": 1, "dateData.nav": 1})


        self.setCollection("How_fundNavN")
        data_list = self.find({"howfundId": {"$in": howfund_list}, "date": {"$gte": start_date, "$lte": end_date}}, {"_id":0, "howfundId": 1, "date": 1, "nav": 1})

        res_list = {}
        for data in data_list:
            if data['howfundId'] not in res_list:
                res_list[data['howfundId']] = {'date': [], 'price': []}

            res_list[data['howfundId']]['date'].append(data['date'])
            res_list[data['howfundId']]['price'].append(data['nav'])

        return res_list

    def find_pricedf_by_fundlist(self, fundlist, start_date, end_date, date_format='%Y-%m-%d'):

        start_date = datetime.strptime(start_date, date_format).strftime('%Y%m%d')
        end_date = datetime.strptime(end_date, date_format).strftime('%Y%m%d')

        price = self.get_fundlist_price2(fundlist, start_date, end_date)

        return price





    def get_fund_info(self, fund_list):

        # query mongodb
        self.setCollection("API_fundData")
        post = self.find({"howfundId": {"$in": fund_list}},
                         {"howfundId": 1, "currencyType": 1, "fundType": 1, "marketType": 1,
                          "regionType": 1, "riskLevel": 1, "chineseFullName": 1})
        # compose price list
        fundId_list = []
        fund_type_list = []
        currency_list = []
        market_type_list = []
        region_type_list = []
        risk_level_list = []
        chinese_name_list = []
        for p in post:
            fundId_list.append(p['howfundId'])
            currency_list.append(p['currencyType'])
            fund_type_list.append(p['fundType'])
            market_type_list.append(p['marketType'])
            region_type_list.append(p['regionType'])
            risk_level_list.append(p['riskLevel'])
            chinese_name_list.append(p['chineseFullName'])

        # compose reference_df
        info_pf = DataFrame(np.column_stack(
            [currency_list, fund_type_list, market_type_list, region_type_list, risk_level_list, chinese_name_list]),
            index=fundId_list,
            columns=['currency', 'fundType', 'marketType', 'regionType', 'riskLevel',
                     'chineseFullName'])
        return info_pf

    def get_agent_list(self):

        # query mongodb

        self.setCollection("SMT_recommendFundAgency")
        query = {"type": "1"}
        projection = {"_id": 0, "fundCompanyName": 1, "fundCompanyId": 1}
        post = self.collection.find(query, projection).sort('fundCompanyId', 1)

        if post.count() == 0 :
            return pd.DataFrame([])

        df = pd.DataFrame(list(post))
        df = df.set_index(['fundCompanyId'])

        return df


    def get_currency_rates(self):
        # query mongodb
        self.setCollection("How_currencyNTD")
        post = self.find({}, {"currency": 1, "data.quote": 1, "data.date": 1, "data": {"$slice": -1}})
        _df = pd.DataFrame(list(post))

        _df['date'] = [d[0]['date'] for d in _df['data']]
        _df['quote'] = [d[0]['quote'] for d in _df['data']]
        del _df['_id']
        del _df['data']

        _df = _df.set_index(['currency']).sort_index()

        return _df

    def list_currency_rates(self):
        # query mongodb
        self.setCollection("How_currencyNTD")
        post = self.find({}, {"currency": 1, "data.quote": 1, "data.date": 1, "data": {"$slice": -1}})
        _df = pd.DataFrame(list(post))

        _df['date'] = [d[0]['date'] for d in _df['data']]
        _df['quote'] = [d[0]['quote'] for d in _df['data']]
        del _df['_id']
        del _df['data']

        _df = _df.set_index(['currency']).sort_index()

        return _df

    @cache_util.cached(timeout=3600)
    def list_currency_index(self):
        self.setCollection("SMT_idxSource")
        _post = self.find({'howIdxType1': '全球主要匯率', 'englishName': {"$regex": ".*USD.*"}},
                          {"_id": 0, "howIdxId": 1, "englishName": 1})

        _df = pd.DataFrame(list(_post))
        _df = _df.set_index(['howIdxId'])

        return _df

    def list_fund_details(self, howfundid_list):
        # query mongodb
        self.setCollection("API_fundData")
        post = self.find({"howfundId": {"$in": howfundid_list}},
                         {"howfundId": 1, "currencyType": 1, "fundType": 1, "startDate": 1,
                          "fundCode": 1, "marketType": 1, "regionType": 1, "riskLevel": 1,
                          "chineseFullName": 1, "fundScaleDate": 1, "fundScaleThous": 1,
                          "fundScaleCurrencyType": 1, 'algorithmBenchmark': 1, "algorithmRf": 1})

        _df = pd.DataFrame(list(post))
        del _df['_id']

        _df = _df.set_index(['howfundId'])
        return _df

    def get_fund_constituent(self, howfund_id):
        # query mongodb
        self.setCollection("API_fundData")
        post = self.find_one({"howfundId": howfund_id}, {"howfundId": 1, "constituents": 1})

        if not 'constituents' in post.keys() or not post['constituents']:
            logger.info("get_fund_constituent Warning !! " + "There is not constituents found for howfund_id = " + post['howfundId'])
            return None

        df = pd.DataFrame(post['constituents'])
        df['howfundId'] = post['howfundId']

        df = df.set_index("howfundId")
        df['invRate'] = [float(utility.convert_float_to_percent(f)) for f in df['invRate']]

        return df

    def list_fund_constituent(self, fund_list):
        # query mongodb
        self.setCollection("API_fundData")
        post = self.find({"howfundId": {"$in": fund_list}}, {"howfundId": 1, "constituents": 1})

        df_list = []

        for p in post:

            if not 'constituents' in p.keys():
                print("Warning !! " + "There is not portfolio found for howfundId = " + p['howfundId'])
                continue

            df = pd.DataFrame(p['constituents'])
            df['howfundId'] = p['howfundId']

            df_list.append(df)

        dfs = pd.concat(df_list)
        dfs = dfs.set_index("howfundId")

        #Pycone的資料表改為float，所以不能（不需要）這樣比較了
        #dfs.ix[dfs['invRate'] == ""] = 0

        dfs['invRate'] = [utility.convert_float_to_percent(float(f)) for f in dfs['invRate']]
        return dfs

    def get_fund_dividend1(self, fund_id):
        # query mongodb
        self.setCollection("How_fundDiv")
        post = self.find_one({"howfundId": fund_id}, {"howfundId": 1, "dateData": 1})

        if post is None:
            return pd.DataFrame([])

        df = pd.DataFrame(post['dateData'])
        df['howfundId'] = post['howfundId']

        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')

        df = df.set_index("date")

        return df


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

    def list_fund_dividend1(self, fund_list):
        # query mongodb
        self.setCollection("How_fundDiv")
        post = self.find({"howfundId": {"$in": fund_list}}, {"howfundId": 1, "dateData": 1})
        df_list = []

        for p in post:
            if not 'dateData' in p.keys():
                print("Warning !! " + "There is not dateData found for howfundId = " + p['howfundId'])
                continue

            df = pd.DataFrame(p['dateData'])
            df['howfundId'] = p['howfundId']
            df_list.append(df)

        if df_list == []:
            return None

        dfs = pd.concat(df_list)
        dfs['date'] = pd.to_datetime(dfs['date'], format='%Y%m%d')
        dfs = dfs.set_index("date").sort_index()

        return dfs

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

    #20171018 shawn 若爬蟲沒有每五分鐘的資料 後續會用捕的
    def get_index_rt_price_0(self, howIdx_id):
        # get the latest tradeDate
        tradeDate = self.get_index_latest_price(howIdx_id)

        if tradeDate is None:
            return pd.DataFrame(list([])), None
        # get prev_close
        prev_close = self.get_index_prev_close(howIdx_id, tradeDate)
        if prev_close is None:
            return pd.DataFrame(list([])), Nonehoppdataapi/util/mongoutil.py

        # query mongodb
        self.setCollection("HOW_index_rt")
        post = self.find({'tradeDate': tradeDate, 'howIdxId': howIdx_id}, {"_id": 0})
        df = pd.DataFrame(list(post))
        df = df.rename_axis({"quote": "price"}, axis="columns")

        # remove date format "/"
        df = df[df.local.str.contains("/") == False]
        df['datetime'] = df['tradeDate'] + " " + df['local']
        df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d %H:%M')
        df = df.set_index("datetime").sort_index()
        df = df[~df.index.duplicated(keep='last')]
        df['change'] = df['price'] - prev_close
        df['changePercent'] = df['change'] / prev_close
        df = df[['price', 'change', 'changePercent']]

        return df, prev_close

    def get_index_latest_price(self, howIdxId):
        # query mongodb
        self.setCollection("HOW_index_rt")

        post = self.find_one({'howIdxId': howIdxId}, {"_id": 0}, sortExpression=[('tradeDate', -1)], limitCount=1)
        if post is None:
            return None

        tradeDate = post.get('tradeDate')
        return tradeDate

    @cache_util.cached(timeout=3600)
    def get_index_prev_close(self, howIdxId, tradeDate):
        # query mongodb
        self.setCollection("HOW_index_hs")

        post = self.find_one({'howIdxId': howIdxId, 'tradeDate':{'$lt':tradeDate}}, {"_id": 0}, sortExpression=[('tradeDate', -1)], limitCount=1)
        if post is None:
            return None
        prev_close = post.get('quote')
        return prev_close

    def get_taipeiDate(self, row):
        try:
            systemTime = row['systemDate'][9:14]
            systemDate = row['systemDate'][:8]
            if row['taipeiTime'] <= systemTime:
                return systemDate
            else:
                prevDate = utility.get_delta_date_bystr(systemDate, days=-1, format='%Y%m%d')
                return prevDate.strftime("%Y%m%d")
        except Exception as e:
            return None

    @cache_util.cached(timeout=3600)
    def get_index_openclose(self, howIdx_id):
        # query mongodb
        self.setCollection("SMT_idxSource")
        post = self.find_one({"howIdxId": howIdx_id},
                         {"_id": 0, "howIdxId": 1, "timeZone": 1, "openTime": 1, "closeTime": 1})

        return post

    @cache_util.cached(timeout=3600)
    def list_index_openclose(self, howIdx_list):
        # query mongodb
        self.setCollection("SMT_idxSource")
        post = self.find({"howIdxId": {"$in": howIdx_list}},
                         {"_id": 0, "howIdxId": 1, "timeZone": 1, "openTime": 1, "closeTime": 1})

        df = pd.DataFrame(list(post))
        df = df.set_index(['howIdxId'])

        return df

    #20171024 shawn 特殊邏輯 先取日期 若取不到 再取最後時間
    def list_latest_index_rt_price_0(self, howidx_list):
        tradeDate = utility.get_delta_date_str(datetime.now(), weeks=-2)
        self.setCollection("HOW_index_rt")
        match = {"$match": {"howIdxId": {"$in": howidx_list}, "tradeDate": {"$gte": tradeDate}}}
        sort = {"$sort": {"howIdxId": 1, "createdAt": 1, "tradeDate": 1, "local": 1}}
        group = {
            "$group": {
                "_id": {"howIdxId": "$howIdxId"},
                "howIdxId": {"$last": "$howIdxId"},
                "tradeDate": {"$last": "$tradeDate"},
                "local": {"$last": "$local"},
                "taipeiTime": {"$last": "$taipeiTime"},
                "quote": {"$last": "$quote"},
                "change": {"$last": "$change"},
                "changePercent": {"$last": "$changePercent"}}
            }
        post = self.collection.aggregate([match, sort, group],allowDiskUse=True)
        #print(list(post))
        df = pd.DataFrame(list(post))
        if df.empty:
            logger.debug("Empty record of query how_index_rt: %s, %s" % (howidx_list, tradeDate))
            return df


        df.pop("_id")

        df.set_index("howIdxId", inplace=True)

        for howIdxId in df.index.values:
            # if howIdxId == 'howIGE72':
            #     a=1
            if "/" in df.get_value(howIdxId, 'local'): continue
            tradeDate = df.get_value(howIdxId, 'tradeDate')
            self.setCollection("HOW_index_rt")
            match = {"$match": {"howIdxId": howIdxId, "tradeDate": {"$gte": tradeDate}}}
            sort = {"$sort": {"howIdxId": 1, "tradeDate": 1, "local": 1}}
            group = {
                "$group": {
                    "_id": {"howIdxId": "$howIdxId"},
                    "howIdxId": {"$last": "$howIdxId"},
                    "tradeDate": {"$last": "$tradeDate"},
                    "local": {"$last": "$local"},
                    "taipeiTime": {"$last": "$taipeiTime"},
                    "quote": {"$last": "$quote"},
                    "change": {"$last": "$change"},
                    "changePercent": {"$last": "$changePercent"}}
            }
            post = self.collection.aggregate([match, sort, group], allowDiskUse=True)
            _df = pd.DataFrame(list(post))
            _df.pop("_id")
            _df.set_index("howIdxId", inplace=True)
            df.loc[_df.index[0]] = _df.iloc[0]

        ytd_df = self.list_index_ytd_price(howidx_list)
        #ytd_df = self.list_index_ytd_price_during_newyear(howidx_list)

        df = df.join(ytd_df, how='left')
        df['YTDROI'] = (df['quote'] - df['YTD']) / df['YTD']
        df['YTDROI'] = [utility.round_float(f) for f in df['YTDROI']]

        return df

    def list_latest_index_rt_price_simple(self, howidx_list):
        self.setCollection("HOW_index_rt")
        match = {"$match": {"howIdxId": {"$in": howidx_list}}}
        sort = {"$sort": {"howIdxId": 1, "tradeDate": 1, "local": 1}}
        group = {"$group": {"_id": {"howIdxId": "$howIdxId"},"howIdxId": {"$last": "$howIdxId"}, "tradeDate": {"$last": "$tradeDate"}, "quote": {"$last": "$quote"}}}

        post = self.collection.aggregate([match, sort, group])
        df = pd.DataFrame(list(post))
        df.pop("_id")
        df.set_index("howIdxId", inplace=True)

        return df

    def list_latest_currency_rate(self):
        # for USDTWD convertion
        currency_list = self.list_currency_index()
        # print(currency_list)
        df = self.list_latest_index_rt_price_simple(list(currency_list.index))
        df = df.join(currency_list, how='inner')
        # print(df)
        rateUSD = df.loc['howIGE2']['quote']

        df['rate'] = df.apply(lambda row: self.get_ratio(row['englishName'], row['quote'], rateUSD), axis=1)
        df['currency'] = ['USD' if n == 'USDTWD' else n.replace('USD', '') for n in df['englishName']]

        df.reset_index(inplace=True)
        df = df[['currency', 'tradeDate', 'rate']]
        df.sort_values(['currency'], inplace=True)
        df.set_index('currency', inplace=True)
        df.columns = ['date', 'quote']

        return df

    def get_ratio(self, code, quote, rateTWD):
        if (code == 'USDTWD'):
            return quote
        elif code.startswith("USD"):
            return rateTWD / quote
        else:
            return rateTWD * quote

    @cache_util.cached(timeout=3600)
    def list_latest_economic_hs(self, howIdxId_list):
        self.setCollection("HOW_economic_hs")
        sort = {"$sort": {"howIdxId": 1, "tradeDate": 1}}
        match = {"$match": {"howIdxId": {"$in": howIdxId_list}}}
        group = {"$group": {"_id": {"howIdxId": "$howIdxId"},"howIdxId": {"$last": "$howIdxId"}, "tradeDate": {"$last": "$tradeDate"},
                            "local": {"$last": "$local"}, "quote": {"$last": "$quote"}, "previous": {"$last": "$previous"},
                            "baseDate": {"$last": "$baseDate"}, "category": {"$last": "$category"}, "forecast": {"$last": "$forecast"}
                            }}

        post = self.collection.aggregate([sort, match, group])
        df = pd.DataFrame(list(post))
        df.pop("_id")
        df.set_index("howIdxId", inplace=True)

        return df

    # @cache_util.cached(timeout=1800)
    def list_index_ytd_price(self, howIdxId_list, offset_year=0):
        ytd = utility.get_ytd(datetime.now(), offset_year=offset_year)
        delta_ytd_2w = utility.get_formatterd_delta_date_bystr(ytd, weeks=-2, from_format='%Y%m%d')
        self.setCollection("HOW_index_hs")
        pipeline = [
            {"$match": {
                'howIdxId': {'$in': howIdxId_list},
                'tradeDate': {'$lt': ytd, '$gt': delta_ytd_2w},
                }
            },
            {"$sort": {'howIdxId': 1, 'tradeDate': -1}},
            {'$group': {
                '_id': "$howIdxId",
                'howIdxId': {'$first': "$howIdxId"},
                'quote': {'$first': "$quote"}}}

        ]
        data_list = self.aggregate_pipeline(pipeline)

        df = pd.DataFrame(data_list)
        df.set_index('howIdxId', inplace=True)
        temp_quotes = []
        for i, quote in enumerate(df['quote']):
            if not isinstance(quote, float) and not isinstance(quote, str):
                logger.info('==========QUOTE NAN==========')
                log = {
                    'query_collectoin': 'HOW_index_hs',
                    'howIdxId': df.iloc[i]['_id'],
                    'ytd': ytd,
                    'quote': quote
                }
                logger.info(log)
                logger.info('==========QUOTE NAN==========')
            temp_quotes.append(utility.round_float(quote))
        df['quote'] = temp_quotes
        df.pop('_id')
        # df['quote'] = [utility.round_float(f) for f in df['quote']]
        df.rename({"quote": "YTD"}, axis="columns", inplace=True)
        #df['ytd'] = ytd
        return df

    def list_index_ytd_price_during_newyear(self, howIdxId_list):

        # todo
        # this function should only be run during new year period
        last_year_df = self.list_index_ytd_price(howIdxId_list, -1)

        this_year_df = self.list_index_ytd_price(howIdxId_list)

        df = pd.concat([last_year_df, this_year_df])
        df = df.sort_values(['ytd'])
        df = df[~df.index.duplicated(keep='last')]
        df = df.drop('ytd', axis=1)
        return df

    def get_index_prevprice(self, howIdxId, date, collection):
        self.setCollection("HOW_index_hs")
        query = {"howIdxId": howIdxId, "tradeDate": {"$lt": date}}
        projection = {"_id": 0, "howIdxId": 1, "tradeDate": 1, "quote": 1}
        post = self.collection.find(query, projection).sort('tradeDate', -1).limit(1)

        df = pd.DataFrame(list(post))
        df = df.rename_axis({"tradeDate": "prevdate", "quote": "prevQuote"}, axis="columns")
        df['tradeDate'] = date

        return df

    def list_latest_index_hs_price_0(self, howidx_list, tradeDate):
        # query mongodb
        self.setCollection("HOW_index_hs")

        sort = {"$sort": {"howIdxId": 1, "tradeDate": 1, "local": 1}}

        match = {"$match": {"howIdxId": {"$in": howidx_list}, "tradeDate": {"$gte": tradeDate}}}
        # match = {"$match": {"howIdxId": {"$in": howidx_list}}}

        group = {"$group": {"_id": {"howIdxId": "$howIdxId"}, "howIdxId": {"$last": "$howIdxId"},
                            "tradeDate": {"$last": "$tradeDate"}, "changePercent": {"$last": "$changePercent"},
                            "monthROI": {"$last": "$monthROI"}, "month6ROI": {"$last": "$month6ROI"},
                            "YTDROI": {"$last": "$YTDROI"}}}

        post = self.collection.aggregate([match, sort, group])
        df = pd.DataFrame(list(post))
        df.pop("_id")
        df = df.set_index(['howIdxId'])

        return df

    @cache_util.cached(timeout=3600)
    def get_index_source(self, howidx_id):

        self.setCollection("SMT_idxSource")
        post = self.find_one({"howIdxId": howidx_id, "order": {"$gte": 1}},
                         {"_id": 0, "order": 1, "howIdxId": 1, "howIdxType": 1, "howIdxType1":1, "howIdxName": 1,
                          "englishName":1, "timeZone": 1, "openTime": 1, "closeTime": 1, "summary": 1,
                          "relatedFund":1})

        return post

    @cache_util.cached(timeout=3600)
    def list_index_source(self):
        self.setCollection("SMT_idxSource")
        post = self.find({"order": {"$gte": 1}},
                         {"_id": 0, "order": 1, "howIdxId": 1, "howIdxType": 1, "howIdxType1": 1, "howIdxName": 1,
                          "englishName": 1, "shortName": 1, "englishShortName": 1,
                          "timeZone": 1, "openTime": 1, "closeTime": 1, "summary": 1})

        df = DataFrame(list(post))
        df.set_index('howIdxId', inplace=True)

        # update the howIdxType name
        howIdxType_names = utility.get_howidxtype_names()
        df = df.join(howIdxType_names, on='howIdxType')
        df['isFuture'] = [1 if "期貨" in t else 0 for t in df['howIdxType1']]
        return df

    @cache_util.cached(timeout=3600)
    def list_index_source_by_type(self, howIdx_type):
        self.setCollection("SMT_idxSource")
        post = self.find({"howIdxType": {"$in": howIdx_type}, "order": {"$gte": 1}},
                         {"_id": 0, "order": 1, "howIdxId": 1, "howIdxType": 1, "howIdxType1": 1, "howIdxName": 1,
                          "englishName": 1, "shortName": 1, "englishShortName": 1,
                          "timeZone": 1, "openTime": 1, "closeTime": 1, "summary": 1})

        df = DataFrame(list(post))
        df.set_index('howIdxId', inplace=True)

        # update the howIdxType name
        howIdxType_names = utility.get_howidxtype_names()
        df = df.join(howIdxType_names, on='howIdxType')
        df['isFuture'] = [1 if "期貨" in t else 0 for t in df['howIdxType1']]
        return df

    @cache_util.cached(timeout=3600)
    def get_index_source_by_type(self, howIdx_type):

        typeDf = pd.DataFrame(howIdx_type, columns=['howIdxType'])
        typeDf['howIdxType_order'] = typeDf.index + 1
        typeDf.set_index('howIdxType', inplace=True)

        self.setCollection("SMT_idxSource")
        post = self.find({"howIdxType": {"$in": howIdx_type}, "order": {"$gte": 1}},
                         {"_id": 0, "order": 1, "howIdxId": 1, "howIdxType": 1, "howIdxName": 1})

        df = DataFrame(list(post))
        df = df.join(typeDf, on=['howIdxType'], how='inner')
        df.set_index('howIdxId', inplace=True)
        df.sort_values(['howIdxType_order', 'order'], inplace=True)
        return df

    @cache_util.cached(timeout=3600)
    def list_holiday(self, start_date, end_date):

        self.setCollection("ETL_invHoliday")
        _post = self.find({"date": {"$gte": start_date, "$lte": end_date}}, {"_id": 0})

        _df_list = []

        for _p in _post:
            _df = pd.DataFrame(_p['data'])
            _df['date'] = pd.to_datetime(_p['date'])
            # _df = _df.set_index(["date","country"])

            _df_list.append(_df)

        if (len(_df_list) == 0):
            return None

        _dfs = pd.concat(_df_list, axis=0, join='outer')
        _dfs = _dfs.set_index(["date", "country"])

        return _dfs

    @cache_util.cached(timeout=3600)
    def get_index_related_fund(self, howidx_id):

        self.setCollection("SMT_idxSource")
        post = self.find_one({"howIdxId": howidx_id, "relatedFund": {"$exists": "true"}},
                             {"_id": 0, "relatedFund": 1})
        if (post == None):
            return DataFrame([])

        _df_list = []
        if len(post['relatedFund']) > 0:
            for data in post['relatedFund']:
                _df = self.list_fund_by_category(data.get('level1'), data.get('level2'), data.get('level3'), data.get('level4'))
                _df_list.append(_df)

            _dfs = pd.concat(_df_list)
            _dfs = _dfs.fillna(method=configure.dataframe_fillna_method)

            return _dfs

        else:
            return DataFrame([])


    @cache_util.cached(timeout=3600)
    def list_fund_by_category(self, level1, level2, level3=None, level4=None):
        self.setCollection("API_fundData")
        projection = {"_id": 0, "howfundId": 1, "fundShortName": 1, "chineseFullName": 1, "englishFullName": 1,
                      "dividend": 1, "dividendFrequency": 1, "riskLevel": 1, "currencyType": 1, "navStatistics": 1,
                      "maxNavDate": 1, "ratings": 1, "lastDivFrequency": 1}
        query = {"provide": True, "fundType": level1}
        #20171026 shawn 若是基金的相關基金 邏輯為 取fundType adjCategory redmind issue #287

        if level3 is None:
            if level4 is None or level4.replace(" ","").strip() == '':
                return None
            else:
                query["adjCategory"] = level4
        # 20171026 shawn 若是指數的相關基金 邏輯為 redmind issue #257
        else:
            # marketType
            if (level2 == '區域'):
                query["marketTypeLevel3"] = level3
                if (level4 != None):
                    query["marketType"] = level4

            # currencyType
            if (level2 == '幣別'):
                query["currencyTypeLevel3"] = level3
                if (level4 != None):
                    query["currencyType"] = level4

            # adjCategory
            if (level2 in ['產業', '債種']):
                if (level3 != None):
                    query["adjCategoryLevel3"] = level3
                if (level4 != None):
                    query["adjCategory"] = level4

        query["navStatistics.lastNav"] = {"$exists": True}
        post = self.find(query, projection)
        df = utility.get_dataframe_from_post(post)

        if df.size == 0:
            return df

        df.set_index("howfundId", inplace=True)

        # join navStatistics data
        nav_df = DataFrame(list(df['navStatistics']))
        nav_df = nav_df.replace(['nan', '', 'None'], np.nan)

        nav_df.set_index(df.index, inplace=True)
        df = df.join(nav_df)
        df['fundType'] = level1
        df['maxNavDate'] = [utility.format_date(d) for d in df['maxNavDate']]
        df.pop('navStatistics')
        df['howRating'] = utility.format_float(uniform(0, 5))
        df['dividendFrequency'] = np.where(df['dividendFrequency'] == "", df['lastDivFrequency'], df['dividendFrequency'])

        # print('------------------------')
        # print(df)

        return df

    def if_else(self, a, b):
        if a == "" or a is None:
            return b
        else:
            return a

    @cache_util.cached(timeout=3600)
    def get_index_bullbear_market(self, howidx_id):
        self.setCollection("SMT_idxSource")
        _post = self.find_one({"howIdxId": howidx_id, "marketType": {"$exists": "true"}},
                             {"_id": 0, "howIdxId":1, "marketType": 1})

        _df = pd.DataFrame(_post['marketType'])
        return _df


    @cache_util.cached(timeout=300)
    def get_symbol_rt_quote(self, sdf):
        # query mongodb

        howIdxId_list = list(sdf['howIdxId'])
        # GET YTD
        ytd = utility.get_ytd(datetime.now(), offset_year=0)
        delta_ytd_2w = utility.get_formatterd_delta_date_bystr(ytd, weeks=-2, from_format='%Y%m%d')

        match ={"$match": {
                'howIdxId': {'$in': howIdxId_list},
                'date': {'$lt': ytd, '$gt': delta_ytd_2w},

                #"taipeiTime": {"$regex": ".*:.*:.*"}
                }}
        sort = {"$sort": {"howIdxId": 1,  "date": -1, "taipeiTime": -1, "createdAt": -1}}
        group = {"$group": {"_id": {"howIdxId": "$howIdxId"}, "howIdxId": {"$first": "$howIdxId"}, "_ytd": {"$first": "$quote"}}}

        self.setCollection("ETL_invGlobeStock")
        post = self.aggregate_pipeline([match, sort, group])
        ytd_df = pd.DataFrame(list(post))
        logger.info('get_stock_realtime a1')
        sdf = pd.merge(sdf, ytd_df, how="left", on="howIdxId")

        sdf['ytd'] = [utility.format_currency(f) for f in sdf['_ytd']]
        # END GET YTD

        # GET CURRENT QUOTE
        tradeDate = utility.get_delta_date_str(datetime.now(), weeks=-1)

        sort = {"$sort": {"howIdxId": 1, "createdAt": 1, "date": 1, "taipeiTime": 1}}

        #match = {"$match": {"howIdxId": {"$in": howIdxId_list}, "date": {"$gte": tradeDate}, "taipeiTime": {"$regex": ".*:.*:.*"}}}
        match = {"$match": {"howIdxId": {"$in": howIdxId_list}, "date": {"$gte": tradeDate}} }

        group = {"$group": {"_id": {"howIdxId": "$howIdxId"}, "howIdxId": {"$last": "$howIdxId"},
                            "date": {"$last": "$date"}, "taipeiTime": {"$last": "$taipeiTime"},
                            "changePercent": {"$last": "$changePercent"}, "quote": {"$last": "$quote"}}}
        limit = {"$limit": 1 }
        logger.info('get_stock_realtime a2')
        for i in range(5):

            self.setCollection("ETL_invGlobeStock")
            post = self.aggregate_pipeline([match, sort, group])
            df = pd.DataFrame(list(post))
            logger.info("========================= GET CURRENT QUOTE =========================")
            logger.info(df)
            if df.empty:
                logger.info('get_stock_realtime a2.2')
                continue;
            else:
                logger.info('get_stock_realtime a2.3')
                break;
        df.pop("_id")
        df = df.sort_values('howIdxId')

        sdf = pd.merge(sdf, df, how="left", on="howIdxId")
        sdf['tradeDate'] = [utility.format_date(d, '%Y%m%d') for d in sdf['date']]
        sdf['local'] = [utility.format_24time(d, '%H:%M:%S') for d in sdf['taipeiTime']]
        sdf['quote'] = [utility.format_currency(f) for f in sdf['quote']]
        sdf['changePercent'] = [utility.convert_percent_to_float(f) for f in sdf['changePercent']]

        sdf.pop('taipeiTime')
        sdf.pop('date')
        sdf.pop('_ytd')
        sdf.pop('_id')

        sdf.reset_index(inplace=True)
        sdf.set_index('howIdxId', inplace=True)
        # END OF GET CURRENT QUOTE

        # GET PRE CLOSE QUOTE
        logger.info('get_stock_realtime a3')
        for howIdxId in howIdxId_list:
            tradeDate = utility.get_formatterd_delta_date_bystr(sdf.get_value(howIdxId, 'tradeDate'), days=-1, from_format='%Y-%m-%d')
            logger.info(howIdxId + ' - get_stock_realtime b1')
            # match = {"$match": {"howIdxId": howIdxId, "date": {"$lte": tradeDate}, "taipeiTime": {"$regex" : ".*:.*:.*"}}}
            # group = {"$group": {"_id": "$howIdxId", "howIdxId": {"$last": "$howIdxId"},
            #                     "date": {"$last": "$date"}, "taipeiTime": {"$last": "$taipeiTime"},
            #                     "quote": {"$last": "$quote"}}}
            # sort = {"$sort": {"howIdxId": 1, "date": 1, "taipeiTime": 1}}
            # post = self.aggregate_pipeline([match, sort, group])
            # query = {"howIdxId": howIdxId, "date": {"$lte": tradeDate}}
            # projection = {"_id": 0, "howIdxId": 1, "date": 1, "quote": 1, "taipeiTime": 1}
            # post = self.collection.find(query, projection).sort('date', -1).limit(300)
            if str(tradeDate) != "nan":
                for i in range(5):
                    self.setCollection("ETL_invGlobeStock")
                    #post = self.find({'howIdxId': howIdxId, 'date': {'$lte': tradeDate}, "taipeiTime": {"$regex": ".*:.*:.*"}}, {"_id": 0, "howIdxId": 1, "date": 1, "taipeiTime": 1,"quote": 1}, sortExpression=[('createdAt', -1), ('date', -1), ('taipeiTime', -1)], limitCount=1)
                    post = self.find({'howIdxId': howIdxId, 'date': {'$lte': tradeDate} }, {"_id": 0, "howIdxId": 1, "date": 1, "taipeiTime": 1,"quote": 1},
                                     sortExpression=[('createdAt', -1), ('date', -1), ('taipeiTime', -1)], limitCount=1)
                    _df = pd.DataFrame(list(post))
                    logger.info('get_stock_realtime b2')
                    if _df.empty:
                        logger.info('get_stock_realtime b2.1')
                        continue;
                    else:
                        logger.info('get_stock_realtime b2.2')
                        break;
                logger.info(_df)
                _df = _df.rename_axis({"date": "prevDate", "quote": "prevClose"}, axis="columns")
                logger.info('get_stock_realtime b2.5')
                _df.reset_index(inplace=True)
                logger.info(_df)
                _df.set_index('howIdxId', inplace=True)
                logger.info('get_stock_realtime b3')
                sdf.set_value(howIdxId, 'prevClose', float(_df.get_value(howIdxId, 'prevClose').replace(',', '')))
                logger.info('get_stock_realtime b4')
        # END OF GET PRE CLOSE QUOTE
        sdf.reset_index(inplace=True)
        sdf['change'] = [utility.format_float(f) for f in (sdf['quote'] - sdf['prevClose'])]
        sdf['YTDROI'] = [utility.format_float(f) for f in ((sdf['quote'] - sdf['ytd']) / sdf['ytd'])]
        sdf = sdf.replace(['nan', 'None'], np.nan)
        sdf = sdf.where((pd.notnull(sdf)), None)
        #print(sdf)
        return sdf

    def get_fund_latest_price_day(self, howfundId):
        # query mongodb
        self.setCollection("How_fundNavN")
        query = {'howfundId': {'$in': [howfundId]}}
        projection = {'_id': 0, 'howfundId': 1, 'date': 1, 'nav': 1}
        sort = [('date', -1)]
        _p = self.find_one(query, projection, sort)
        if _p is None:
            return _p

        return _p['date']


    """
    def get_fund_latest_price(self, howfund_list):
        # query mongodb
        self.setCollection("API_fundData")


        _post = self.find({"howfundId": {"$in": howfund_list}},
                          {"_id": 0, "howfundId": 1,
                           "navStatistics.RrThisYear": 1})

        if _post is None:
            return pd.DataFrame([])

        _df = pd.DataFrame(list(_post))
        #_df.set_index("howfundId", inplace=True)
        _df['YTDROI'] = [r['RrThisYear'] for r in _df['navStatistics']]
        _df.pop('navStatistics')


        self.setCollection("How_fundNavN")
        match = {"$match": {"howfundId": {"$in": howfund_list}}}
        sort = {"$sort": {"date": 1}}
        group = {"$group": {"_id": {"howfundId": "$howfundId"}, "howfundId": {"$last": "$howfundId"},
                            "date": {"$last": "$date"},"dayChange": {"$last": "$dayChange"},"oneDayProfitRate": {"$last": "$oneDayProfitRate"},
                            "nav": {"$last": "$nav"}}}

        nav_post = self.collection.aggregate([match, sort, group],allowDiskUse=True)

        nav_df = pd.DataFrame(list(nav_post))

        _dfs = pd.merge(nav_df, _df, on="howfundId", how="outer")
        _dfs = _dfs.rename({"date": "tradeDate", "dayChange": "change","oneDayProfitRate": "changePercent"}, axis="columns")
        _dfs = _dfs.set_index(['howfundId']).sort_index()
        _dfs.pop('_id')

        return _dfs"""

    def get_fund_latest_30_price(self, howfund_id):
        # query mongodb
        self.setCollection("How_fundNavN")
        post = self.find({"howfundId": howfund_id},
                         {"_id":0, "date": 1, "nav": 1, "dayChange": 1, "oneDayProfitRate": 1},
                         sortExpression=[('date', -1)], limitCount=31)
        df = pd.DataFrame(list(post))
        if df.empty:
            return None
        df.set_index("date", inplace=True)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        df = df.fillna(method=configure.dataframe_fillna_method)
        df = df.rename(columns={'nav': 'price', 'dayChange': 'daily_return', 'oneDayProfitRate': 'daily_return_pct'} )
        return df


    def get_index_latest_30_price(self, howIdxId):
        # query mongodb
        self.setCollection("HOW_index_hs")
        post = self.find({"howIdxId": howIdxId},
                         {'_id': 0, "tradeDate": 1, "quote": 1},
                         sortExpression=[('tradeDate', -1)], limitCount=31)

        df = pd.DataFrame(list(post))
        df = df.rename_axis({"tradeDate": "date", "quote": "price"}, axis="columns")
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        df = df.set_index("date").sort_index()

        # remove this after the datatype is fixed in mongo
        df['price'] = [float(p) for p in df['price']]

        return df


    def get_FundRich_fundId(self):
        self.setCollection("fundCode")
        query = {"FRId": {"$gt": ""}}
        projection = {"_id": 0, "howfundId": 1, "FRId": 1}
        post = self.find(query, projection)
        df = pd.DataFrame(list(post))
        df = df.set_index(['howfundId'])
        return df

    def get_fund_by_category(self, query_str, start_date, fundScaleThous):
        self.setCollection("API_fundData")

        projection = {"_id": 0, "howfundId": 1, "isOverseaFund": 1, "startDate": 1, "minNavDate": 1, "maxNavDate": 1,
                      "fundScaleThous": 1, "fundScaleCurrencyType": 1}
        query = dict(pd.json.loads(query_str))
        start_date_constraint = {"startDate": {"$lt": start_date}, "minNavDate": {"$lt": start_date}}
        query.update(start_date_constraint)
        post = self.find(query, projection)

        df = pd.DataFrame(list(post))
        df = df.set_index(['howfundId'])

        df['fundScaleThous'] = [utility.round_float(f) for f in df['fundScaleThous']]
        df = df[df['fundScaleThous'] > fundScaleThous]
        return df

    # def get_fund_price(self, howfund_id, start_date, end_date):
    #     self.setCollection("API_fundData")
    #     post = self.find_one({"howfundId": howfund_id},
    #                          {"dailyNav.date": 1, "dailyNav.nav": 1})
    #
    #     df = pd.DataFrame(post['dailyNav'])
    #     df = df.set_index("date")
    #     df.index = pd.to_datetime(df.index)
    #     df = df.rename_axis({"nav": "price"}, axis="columns")
    #
    #     df = df[start_date:end_date]
    #     df['price'] = [utility.round_float(p) for p in df['price']]
    #
    #     return df
    #
    # def get_fundlist_price(self, howfund_list, start_date, end_date):
    #     self.setCollection("API_fundData")
    #     post_list = self.find({"howfundId": {"$in": howfund_list}},
    #                           {"howfundId": 1, "dailyNav.date": 1, "dailyNav.nav": 1})
    #
    #     df_list = []
    #
    #     for post in post_list:
    #         df = pd.DataFrame(post['dailyNav'])
    #         df = df.set_index("date")
    #         df.index = pd.to_datetime(df.index)
    #         df = df.rename_axis({"nav": post['howfundId']}, axis="columns")
    #
    #         df = df[start_date:end_date]
    #
    #         df_list.append(df)
    #
    #     dfs = pd.concat(df_list, axis=1, join='outer')
    #     dfs = dfs.fillna(method="ffill")
    #
    #     return dfs

    def get_fundlist_marketcap(self, howfund_list):
        self.setCollection("API_fundData")
        post = self.find({"howfundId": {"$in": howfund_list}},
                         {"_id": 0, "howfundId": 1, "fundScaleThous": 1, "fundScaleCurrencyType": 1})

        df = pd.DataFrame(list(post))
        df = df.set_index("howfundId")
        df = df.rename_axis({"fundScaleThous": "marketcap", "fundScaleCurrencyType": "currency"}, axis="columns")

        return df

    def get_index_price(self, howidx_id, start_date, end_date):
        # query mongodb
        self.setCollection("HOW_index_hs")
        post = self.find({"howIdxId": howidx_id, 'tradeDate': {'$gte': start_date, '$lte': end_date}},
                         {'_id': 0, "tradeDate": 1, "quote": 1})

        df = pd.DataFrame(list(post))

        df = df.rename_axis({"tradeDate": "date", "quote": "benchmark"}, axis="columns")
        df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        df = df.set_index("date").sort_index()

        df = df[start_date:end_date]

        df['benchmark'] = [utility.round_float(p) for p in df['benchmark']]

        return df

    def list_currency_index(self):
        """
        List all the currency howIdxId/name
        :return:
        """
        self.setCollection("SMT_idxSource")
        post = self.find({'howIdxType1': '全球主要匯率', 'englishName': {"$regex": ".*USD.*"}},
                         {"_id": 0, "howIdxId": 1, "englishName": 1})

        df = pd.DataFrame(list(post))
        df = df.set_index(['howIdxId'])

        return df

    def list_latest_index_rt_price_simple(self, howidx_list):
        """
        generic function to retrieve latest price in HOW_index_rt table
        :param howidx_list:
        :return:
        """
        self.setCollection("HOW_index_rt")

        match = {"$match": {"howIdxId": {"$in": howidx_list}}}

        sort = {"$sort": {"howIdxId": 1, "tradeDate": 1, "local": 1}}

        group = {"$group": {"_id": {"howIdxId": "$howIdxId"}, "howIdxId": {"$last": "$howIdxId"},
                            "tradeDate": {"$last": "$tradeDate"},
                            "quote": {"$last": "$quote"}}}

        post = self.collection.aggregate([match, sort, group],allowDiskUse=True)
        df = pd.DataFrame(list(post))
        df.pop("_id")

        df.set_index("howIdxId", inplace=True)

        return df

    def get_latest_currency_rate(self):
        """
        Get the latest currency rate in NTD
        :return:
        """

        currency_list = self.list_currency_index()

        price_df = self.list_latest_index_rt_price_simple(list(currency_list.index))
        price_df = price_df.join(currency_list, how='inner')

        rateUSD = price_df.loc['howIGE2']['quote']

        price_df['rate'] = price_df.apply(lambda row: self.get_ratio(row['englishName'], row['quote'], rateUSD), axis=1)
        price_df['currency'] = ['USD' if n == 'USDTWD' else n.replace('USD', '') for n in price_df['englishName']]

        price_df.reset_index(inplace=True)
        price_df = price_df[['currency', 'rate']]
        price_df.sort_values(['currency'], inplace=True)
        price_df.set_index('currency', inplace=True)

        price_df.loc['NTD'] = 1

        return price_df

    def get_ratio(self, code, quote, rateTWD):

        if (code == 'USDTWD'):
            return quote
        elif code.startswith("USD"):
            return rateTWD / quote
        else:
            return rateTWD * quote

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


    @cache_util.cached(timeout=3600)
    def get_popular_stocks(self):

        self.setCollection("SMT_idxSource")
        post = self.find(
                        {
                            "howIdxType": "熱門個股",
                            "order": { "$gt": 0 }
                        },
                        projection = {
                            "_id": 0,
                            "order": 1,
                            "ticker":1,
                            "exchange":1,
                            "howIdxName":1,
                            "shortName":1,
                            "howIdxId": 1
                        }
        )

        sdf = pd.DataFrame(list(post))
        sdf['symbol'] = sdf['ticker'] + ":" + sdf['exchange']
        sdf.set_index(['ticker'], inplace=True)
        return sdf

    def constituent_search(self, invratelimit=0):

        self.setCollection("API_fundData")
        pipeline = [
            {
                "$match": {
                    #"howfundId": {"$in": ["howF13"]},
                    "constituents.type": {"$in": ["assertAllocation","country","industryRatio"]},
                    "provide": True
                }

            },
            {
                "$unwind": "$constituents"
            },
            {
                "$group": {
                    "_id": {
                        "howfundId": "$howfundId",
                        "chineseFullName": "$chineseFullName",
                        "fundShortName": "$fundShortName",
                        "fundType": "$fundType",
                        "date": "$constituents.date",
                        "type": "$constituents.type",
                        "portfolioCategory": "$constituents.portfolioCategory",
                        "portfolioName": "$constituents.portfolioName"
                    },
                    "value": {"$sum": "$constituents.invRate"}
                }
            },
            {
                "$match": {
                    "value": { "$gte": float(invratelimit)}
                }
            },
            {
                "$group": {
                    "_id": {
                        "howfundId": "$howfundId",
                        "type": "$_id.type",
                        "portfolioCategory": "$_id.portfolioCategory",
                        "portfolioName": "$_id.portfolioName"

                    },
                    "howfundId": {
                        "$push": {
                            "chineseFullName": "$_id.chineseFullName",
                            "fundShortName": "$_id.fundShortName",
                            "fundType": "$_id.fundType",
                            "date": "$_id.date",
                            "howfundId": "$_id.howfundId",
                            "invRate": "$value"
                        }
                    }
                }
            },
            #Stage 5
            {
                "$group": {
                    "_id": {
                        "type": "$_id.type",
                        "portfolioCategory": "$_id.portfolioCategory",
                        "portfolioName": "$_id.portfolioName"
                    },
                    "howfundIds": {
                        "$push": {

                            "howfundId": "$howfundId"
                        }
                    }
                }
            },

            #Stage 6
            {
                "$group": {
                    "_id": {
                        "type": "$_id.type",
                        "portfolioCategory": "$_id.portfolioCategory",
                    },
                    "portfolioNames": {
                        "$push": {
                            "portfolioName": "$_id.portfolioName",
                            "howfundIds": "$howfundIds"
                        }
                    }
                }
            },

            #Stage 7
            {
                "$group": {
                    "_id": {
                        "type": "$_id.type",
                    },
                    "portfolioCategories": {
                        "$push": {
                            "portfolioCategory": "$_id.portfolioCategory",
                            "portfolioNames": "$portfolioNames"
                        }
                    }
                }
            },

            # Stage 8
            {
                "$group": {
                    "_id": {
                        "type": "$_id.type",
                    },
                    "typies": {
                        "$push": {
                            "type": "$_id.type",
                            "portfolioCategories": "$portfolioCategories"
                        }
                    }
                }
            }


        ]

        post = self.aggregate_pipeline(pipeline)

        result = {}
        for typies in post:
            _type = typies['_id']['type']
            result[_type] = {}
            result_type = typies['typies'][0]['portfolioCategories']
            for Categories in result_type:
                _category = Categories['portfolioCategory']
                if _category is None:
                    _category = "未分類"
                result[_type][_category] = {}
                result_type_category = Categories['portfolioNames']
                for Names in result_type_category:
                    _name = Names['portfolioName']
                    if _name is None:
                        _name = "未分類"
                    result[_type][_category][_name] = {}
                    result_type_category_name = Names['howfundIds'][0]['howfundId']
                    for row in result_type_category_name:
                        _howfundId = row['howfundId']
                        row.pop('howfundId')
                        result[_type][_category][_name][_howfundId] = row


        return result

    def get_fundlist_price2(self, howfund_list, start_date, end_date):

        self.setCollection("How_fundNavN")
        post = self.find({"howfundId": {"$in": howfund_list}, "date": {"$gte": start_date, "$lte": end_date}}, {"_id":0, "howfundId": 1, "date": 1, "nav": 1})

        df = pd.DataFrame(list(post))
        if df.empty:
            return df
        df = pd.pivot_table(df, index=["date"], columns="howfundId")["nav"]
        df.index = pd.to_datetime(df.index)
        df = df.fillna(method=configure.dataframe_fillna_method)

        return df

    def get_fundlist_day_change(self, howfund_list, start_date, end_date):

        self.setCollection("How_fundNavN")
        post = self.find({"howfundId": {"$in": howfund_list}, "date": {"$gte": start_date, "$lte": end_date}}, {"_id":0, "howfundId": 1, "date": 1, "nav": 1, "dayChange": 1, "oneDayProfitRate": 1})

        df = pd.DataFrame(list(post))
        df = df.rename(columns={'nav':'price', 'dayChange': 'daily_return', 'oneDayProfitRate': 'daily_return_pct'})
        if df.empty:
            return df


        #df.index = pd.to_datetime(df.index)
        df = df.fillna(method=configure.dataframe_fillna_method)

        return df