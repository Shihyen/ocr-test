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
from qrcodeocr.util.mysqlutil import MySQLUtil

import logging

logger = logging.getLogger(__name__)

def deprecated(func):
    pass
    return func

class Constituent(MongoUtil):
    """mongo utility"""

    def __init__(self):
        super(Constituent, self).__init__()
        self.fund_code_list = None

    def get_fund_constituent(self, howfund_id):
        try:
            # query mongodb
            self.setCollection("API_fundData")
            post = self.find_one({"howfundId": howfund_id}, {"howfundId": 1, "constituents": 1})

            df = pd.DataFrame(post['constituents'])

            df['howfundId'] = post['howfundId']

            df = df.set_index("howfundId")
            df['invRate'] = [float(utility.convert_float_to_percent(f)) for f in df['invRate']]

        except Exception as e:
            df = pd.DataFrame(list([]))
            logger.debug("Exception: %s " % str(e))

        finally:
            return df

    def list_fund_constituent(self, fund_list):
        try:
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

            # Pycone的資料表改為float，所以不能（不需要）這樣比較了
            # dfs.ix[dfs['invRate'] == ""] = 0

            dfs['invRate'] = [utility.convert_float_to_percent(float(f)) for f in dfs['invRate']]


        except Exception as e:
            dfs = pd.DataFrame(list([]))
            logger.debug("Exception: %s " % str(e))

        finally:
            return dfs

    # 條件查詢，輸入currency, country, industry即可查出基金
    def constituent_search(self, params):
        try:
            # query mongodb
            # query = { "$and": [{"$and": [{"constituents.type": "country"},  {"constituents.portfolioCategory": {"$in":  ["全球","亞洲"]} }]}, {"$and": [{"constituents.type": "industryRatio"},  {"constituents.portfolioCategory": "公用" }] }] ,"provide": True}
            query = {"provide": True}

            if 'currency' in params:
                query['currencyType'] = {"$in": params['currency']}

            condition = []
            if 'country' in params:
                condition.append({'$and': [{'constituents.type': 'country'},
                                           {'constituents.portfolioCategory': {'$in': params['country']}}]})
            if 'industry' in params:
                condition.append({'$and': [{'constituents.type': 'industryRatio'},
                                           {'constituents.portfolioCategory': {'$in': params['industry']}}]})
            if len(condition) > 0:
                query["$and"] = condition

            self.setCollection("API_fundData")
            projection = {"howfundId": 1}

            post = self.find(query=query, projection=projection)

            dfs = pd.DataFrame(list(post))

        except Exception as e:
            dfs = pd.DataFrame(list([]))
            logger.debug("Exception: %s " % str(e))

        finally:
            return dfs

    def constituent_search_engine(self, invratelimit=0):

        post = self.get_constituents(invratelimit)

        print(post)
        result = {}
        result2 = []
        drill_down = {}
        for typies in post:
            _type = typies['_id']['type']
            if _type == 'country':
                _type = '區域'

            if _type == 'industryRatio':
                _type = '產業'

            result[_type] = {}
            result_type = typies['typies'][0]['portfolioCategories']

            result2_type = {"value": typies['cnt'], "path": _type, "name": _type, "children": []}

            dw_type = {"$count": typies['cnt']}
            dw_category = {}
            for Categories in result_type:
                _category = Categories['portfolioCategory']
                if _category is None:
                    continue
                    _category = "未分類"
                result[_type][_category] = {}
                result_type_category = Categories['portfolioNames']

                result2_category = {"value": Categories['cnt'], "path": ("%s/%s" % (_type, _category)),
                                    "name": _category, "children": [], "funds": []}

                dw_category = {"$count": Categories['cnt']}

                for Names in result_type_category:
                    _name = Names['portfolioName']
                    if _name is None:
                        continue
                        _name = "未分類"
                    result[_type][_category][_name] = []
                    result_type_category_name = Names['howfundIds'][0]['howfundId']

                    # result2_name = {"value": Names['cnt'], "path": ("%s/%s/%s" % (_type, _category, _name)), "name": _name, "funds": []}
                    result2_name = {"value": Names['cnt'], "path": ("%s/%s/%s" % (_type, _category, _name)),
                                    "name": _name, "funds": []}

                    dw_name = {"$count": Names['cnt']}
                    for row in result_type_category_name:
                        _howfundId = row['howfundId']
                        result[_type][_category][_name].append({"value": row['invRate'], "name": _howfundId,
                                                                "path": ("%s/%s/%s" % (_type, _category, _name)),
                                                                "data": row})
                        result2_name['funds'].append(_howfundId)
                        # result2_category['funds'].append(_howfundId)
                        dw_name[_howfundId] = {"$count": 1}

                    result2_category["children"].append(result2_name)
                    dw_category[_name] = dw_name

                # result2_category.pop('children') #移除第三層的資料
                result2_type["children"].append(result2_category)
                dw_type[_category] = dw_category

            result2.append(result2_type)
            drill_down[_type] = dw_type

        print(result)
        return result2

    
    def get_constituents(self, invrate_limit=0, constituents_type=['country', 'industryRatio']):
        """

        取出API_FundData的constituents。

        :param invratelimit: 過濾掉invRate總和低於 invratelimit 的基金
        :type invratelimit: float

        :return constituents: mongodb 的 cursor
        :rtype constituents: cursor

        """

        # print("invratelimit:" + str(invrate_limit))

        self.setCollection("API_fundData")
        pipeline = [
            {
                "$match": {
                    # "howfundId": {"$in": ["howF2553","howF3403","howF317","howF13","howF1261","how1765","howF3863","howF3858","howF3854"]},
                    # "howfundId": {"$in": ["how1579"]},
                    # "howfundId": {"$in":["howF3374"]},
                    "provide": True
                }

            },
            {
                "$unwind": "$constituents"
            },
            {
                "$match": {
                    "constituents.type": {"$in": constituents_type},
                    # "constituents.portfolioCategory": {"$in": ["金融服務","科技","週期性消費","工業","其他","能源","基本物料","健康護理"]},
                    # "constituents.portfolioCategory": {"$nin": ["電訊服務", "防守性消費"]}
                    "constituents.portfolioCategory": {"$nin": [None, "", "未分類", "現金", "其他"]},

                }
            },
            {
                "$group": {
                    "_id": {
                        "howfundId": "$howfundId",
                        # "chineseFullName": "$chineseFullName",
                        # "fundShortName": "$fundShortName",
                        # "fundType": "$fundType",
                        # "date": "$constituents.date",
                        "type": "$constituents.type",
                        "portfolioCategory": "$constituents.portfolioCategory",
                        "portfolioName": "$constituents.portfolioName"
                    },
                    "value": {"$sum": "$constituents.invRate"}
                }
            },
            {
                "$match": {
                    "value": {"$gte": float(invrate_limit)},
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
                    "cnt": {"$sum": 1},
                    "value": {"$sum": "$value"},
                    "howfundId": {
                        "$push": {
                            # "chineseFullName": "$_id.chineseFullName",
                            # "fundShortName": "$_id.fundShortName",
                            # "fundType": "$_id.fundType",
                            # "date": "$_id.date",
                            "howfundId": "$_id.howfundId",
                            "invRate": "$value"
                        }
                    }
                }
            },
            # Stage 5
            {
                "$group": {
                    "_id": {
                        "type": "$_id.type",
                        "portfolioCategory": "$_id.portfolioCategory",
                        "portfolioName": "$_id.portfolioName"
                    },
                    "cnt": {"$sum": "$cnt"},
                    "value": {"$sum": "$value"},
                    "howfundIds": {
                        "$push": {
                            "value": {"$sum": "$value"},
                            "howfundId": "$howfundId"
                        }
                    }
                }
            },

            # Stage 6
            {
                "$group": {
                    "_id": {
                        "type": "$_id.type",
                        "portfolioCategory": "$_id.portfolioCategory",
                    },
                    "cnt": {"$sum": "$cnt"},
                    "value": {"$sum": "$value"},
                    "portfolioNames": {
                        "$push": {
                            "cnt": {"$sum": "$cnt"},
                            "value": {"$sum": "$value"},
                            "portfolioName": "$_id.portfolioName",
                            "howfundIds": "$howfundIds"
                        }
                    }
                }
            },

            # Stage 7
            {
                "$group": {
                    "_id": {
                        "type": "$_id.type",
                    },
                    "cnt": {"$sum": "$cnt"},
                    "value": {"$sum": "$value"},
                    "portfolioCategories": {
                        "$push": {
                            "cnt": {"$sum": "$cnt"},
                            "value": {"$sum": "$value"},
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
                    "cnt": {"$sum": "$cnt"},
                    "value": {"$sum": "$value"},
                    "typies": {
                        "$push": {
                            "cnt": {"$sum": "$cnt"},
                            "type": "$_id.type",
                            "value": {"$sum": "$value"},
                            "portfolioCategories": "$portfolioCategories"
                        }
                    }
                }
            }

        ]

        post = self.aggregate_pipeline(pipeline)

        return post


    def smart_select_cache(self, key, data=None, timeout=3600):
        """

        快取機制

        :param key: cache key
        :type key: str

        :param data:
        :type data: any

        :return data:
        :rtype data: any

        """
        if data is not None:
            cache_util.cache.set(key, data, timeout)
            logger.info('[SET] cache key:[%s] timeout:[%i]', key, timeout)
            return True

        data = cache_util.cache.get(key)
        # print(key)
        # print(data)
        if data is None:
            logger.info('[GET] cache key:[%s] None', key)
        else:
            logger.info('[GET] cache key:[%s]', key)

        return data


    def get_smart_select_category(self, fund_code, invrate_limit):
        """

        取得Smart Select Category

        :param fund_code: 資料來源代號，作為過濾條件
        :type fund_code: str

        :param invrate_limit: 關聯度底線
        :type invrate_limit: float

        :return smart_select_category:
        :rtype  smart_select_category: list
        """

        smt_portfolio_name = self.get_smt_portfolio_name()

        api_funddata = self.set_smart_select_fundlist_cache(fund_code=fund_code, invrate_limit=invrate_limit)

        for item in api_funddata:

            if item['name'] == '區域':
                typies = 'country'
            else:
                typies = 'industryRatio'

            if len(item['children']) > 0:
                for categories in item['children']:
                    category = categories['name']
                    if len(categories['children']) > 0:
                        for names in categories['children']:
                            if names['name'] in smt_portfolio_name[typies][category]:
                                # 若API_FundData的記錄存在於SMT_portfolioName
                                # 將SMT_portfolioName的value設為0，當成過濾條件
                                smt_portfolio_name[typies][category][names['name']] = 0

        # 針對smt_portfolio_name跑一次遞迴，把value不為0（不存在於api_fundData）的排除
        return self.get_return_list(smt_portfolio_name)

    def get_smt_portfolio_name(self):
        """

        取得SMT_portfolioName中的category順序

        :return:
        """

        self.setCollection("SMT_portfolioName")

        query = {'$and': [ {'categoryID': { '$exists': True }}, {'categoryID': { '$ne': '' }} ] }
        projection = {"_id": 0, "categoryID": 1, "portfolioType": 1, "portfolioCategory": 1, "portfolioName": 1}
        sort = [("categoryID",1)]

        post = self.find(query=query, projection=projection, sortExpression=sort, limitCount=99999)

        data = list(post)

        result = {}

        for item in data:

            if item["portfolioType"] not in result:
                result[item["portfolioType"]] = {}

            if item["portfolioCategory"] not in result[item["portfolioType"]]:
                result[item["portfolioType"]][item["portfolioCategory"]] = {}

            if item["portfolioName"] not in result[item["portfolioType"]][item["portfolioCategory"]]:
                result[item["portfolioType"]][item["portfolioCategory"]][item["portfolioName"]] = len(result[item["portfolioType"]][item["portfolioCategory"]])+1

        return result

    def get_return_list(self, data):
        """

        針對return list寫的遞迴，將資料格式化成前端需要的格式，並且過濾掉FRID不存在的資料

        :param data:
        :return:
        """
        result = []
        for key, item in data.items():
            if key == 'country':
                key = "區域"
            if key == 'industryRatio':
                key = "產業"

            if type(item) == int:
                if item == 0:
                    result.append( {"name": key})
            else:
                result.append( {"name": key, "children": self.get_return_list(item) } )

        return result


    def set_smart_select_fundlist_cache(self, invrate_limit=0.0, fund_code=None):
        """
        提供 Smart Select 選單，同時將基金清單寫入快取

        :param invrate_limit: 過濾掉invRate總和低於 invrate_limit 的基金
        :type invrate_limit: float

        :param fund_code: 資料來源代號，作為過濾條件
        :type fund_code: str

        :return constituents: 整理constituents成dict格式後輸出
        :rtype constituents: dict

        """
        country_data = []
        industry_data = []

        country = self.get_constituents(invrate_limit, constituents_type=['country'])
        if country is not None:
            country_data = self.sort_cache(constituents=country, fund_code=fund_code)

        industry = self.get_constituents(invrate_limit, constituents_type=['industryRatio'])
        if industry is not None:
            industry_data = self.sort_cache(constituents=industry, fund_code=fund_code)
        #
        # industry = self.get_constituents(invratelimit)
        # if industry is not None:
        #     industry_data = self.sort_cache(constituents=industry, fund_code=fund_code)


        return country_data + industry_data

    def sort_cache(self, constituents, fund_code):
        """

        將 get_constituents 的結果整理成前端易讀的格式，建立cache

        :param constituents: get_constituents 得到的結果
        :type constituents: list

        :param fund_code: 資料來源代號，作為過濾條件
        :type fund_code: str

        :return: 前端易讀的格式
        """
        result = []
        for data in constituents:
            for typies in data["typies"]:
                typeName = ""
                if typies["type"] == 'country':
                    typeName = '區域'

                if typies["type"] == 'industryRatio':
                    typeName = '產業'

                resultChildren = []
                for portfolioCategories in typies["portfolioCategories"]:
                    categoryChildren = []
                    categoryHowfundIds = []
                    for portfolioNames in portfolioCategories["portfolioNames"]:
                        categoryChildren.append({"name": portfolioNames["portfolioName"]})
                        nameHowfundIds = []
                        for howfundId in portfolioNames["howfundIds"]:
                            for howfund in howfundId["howfundId"]:
                                nameHowfundIds.append(howfund["howfundId"])
                                categoryHowfundIds.append(howfund["howfundId"])

                        key = "%s|%s|%s|%s" % ("SmartSelect", fund_code , "Name", portfolioNames["portfolioName"])
                        self.set_smart_select_cache(fund_code, key, list(set(nameHowfundIds)))

                    key = "%s|%s|%s|%s" % ("SmartSelect", fund_code, "Category", portfolioCategories["portfolioCategory"])
                    self.set_smart_select_cache(fund_code, key, list(set(categoryHowfundIds)))

                    resultChildren.append({
                        "name": portfolioCategories["portfolioCategory"],
                        "children": categoryChildren
                    })

                result.append({
                    "name": typeName,
                    "children": resultChildren
                })

        return result

    def set_smart_select_cache(self, fund_code, key, data):
        """

        進行設定get_constituent的基金清單快取設定時，將基金清單寫進快取

        :param fund_code: 合作夥伴的基金碼標籤
        :type fund_code: str

        :param key: 快取key
        :type key: str

        :param data: 要快取的fund list
        :type data: list

        """

        if self.fund_code_list is None:
            self.fund_code_list = self.get_fund_code_list(fund_code)


        fund_list = self.check_fund_code_list(data)

        if fund_list is None:
            self.smart_select_cache(key, data=[], timeout=0)
        else:
            # print(key + ":" + str(len(data)) +"/"+ str(len(list(set(fund_list)))))
            self.smart_select_cache(key, data=list(set(fund_list)), timeout=3600*24)


    def get_fund_code_list(self, fund_code):

        mysql = MySQLUtil()
        return mysql.get_fund_code_list(fund_code)

    def check_fund_code_list(self, data):

        fund_list = []
        for item in self.fund_code_list:

            fund_list.append(item['howfundId'])

        return list(set(data).intersection(fund_list))

    def list_fund_category(self, howfund_list):
        """

        :param howfund_list:
        :return:
        """
        # query mongodb
        self.setCollection("API_fundData")
        post = self.find({"howfundId": {"$in": howfund_list}},
                         {"_id": 0, "howfundId": 1, "algorithmCategory": 1, "majorHowfundId": 1})

        df = pd.DataFrame(list(post))
        df.set_index("howfundId", inplace=True)
        return df

    def get_fundlist_details(self, fund_id_list=None, fund_code=None):
        """

        取得SmartSelect第一層快取所需要的資料

        :param fund_id_list: howfundId list
        :type fund_id_list: list

        :param fund_code: 檢查該欄位是否為空
        :type fund_code: str

        :return fund_detail: 整合 mongodb 的資料 (fundCode, oneDayProfit,  currency_CN)
        :rtype fund_detail: dataframe

        """

        trade_date = utility.get_delta_date_str(datetime.now(), weeks=-2)

        fund_rich_df = self.get_ecallot_fundlist()
        if fund_rich_df is None:
            return None

        # query mongodb
        self.setCollection("API_fundData")
        projection = {"_id": 0, "howfundId": 1, "majorHowfundId": 1, "chineseFullName": 1, "currencyType": 1,
                      "fundShortName": 1, "generalIssuer": 1,
                      "adjCategory": 1, "tejCategory": 1, "CYCategory": 1, "constituents": 1, "warningMessage": 1}

        post = self.find({"howfundId": {"$in": list(set(fund_rich_df.index))}, "provide": True}, projection)

        df = pd.DataFrame(list(post))

        if df.empty:
            return None

        df.set_index("howfundId", inplace=True)

        df['fundTypeName'] = [CYCategoryCase(t) for t in df['CYCategory']]

        nav_df = self.get_one_day_profit(fund_list=list(set(df.index)), trade_date=trade_date)
        if not nav_df.empty:
            df = df.join(nav_df)

        currency_name = self.get_currency_name(currency_type_list=list(set(df["currencyType"])))

        df['currencyType'] = df.apply(lambda row: self.mapping_currency_name(row['currencyType'], currency_name), axis=1)

        df = df.join(fund_rich_df)

        return df

    def mapping_currency_name(self, currencyType, currency_name):

        for x, v in currency_name['name'].items():
            if currencyType in v:
                return currency_name['currency_CN'][x]

        return currencyType




    def get_ecallot_fundlist(self, fundlist = None):

        self.setCollection("ETL_FRFundInfo")
        pipeline = [
            # Stage 1
            {
                "$match": {
                    "EcAllot": "1"
                }
            },

            # Stage 2
            {
                "$group": {
                    "_id": {"IsinCode": "$IsinCode","Currency":"$Currency"},
                    "IsinCode": {"$last": "$IsinCode"},
                    "EcAllot": {"$last": "$EcAllot"},
                    "Currency": {"$last": "$Currency"},
                }
            },

            # Stage 3
            {
                "$lookup": {
                    "from" : "SMT_currencyType",
                    "localField" : "Currency",
                    "foreignField" : "name",
                    "as" : "CurrencyName"
                }
            },

            # Stage 4
            {
                "$unwind": {
                    "path" : "$CurrencyName",
                }
            },

            # Stage 5
            {
                "$lookup": {
                    "from" : "How_fundDetailN",
                    "localField": "IsinCode",
                    "foreignField": "isinCode",
                    "as" : "How_fundDetailN"
                }
            },

            # Stage 6
            {
                "$unwind": {
                    "path" : "$How_fundDetailN",
                }
            },

            # Stage 7
            {
                "$redact": {
                    "$cond":[
                            {"$eq":["$CurrencyName.currency", "$How_fundDetailN.currencyType"]},
                            "$$KEEP",
                            "$$PRUNE"
                    ]
                }
            },

            # Stage 8
            {
                "$project": {
                    "isinCode": "$IsinCode",
                    #"EcAllot": 1,
                    "currencyCode": "$CurrencyName.currency",
                    "howfundId": "$How_fundDetailN.howfundId",
                    #"How_fundDetailN_IsINCode": "$How_fundDetailN.isinCode",
                    #"How_fundDetailN_CurrencyType": "$How_fundDetailN.currencyType",
                }
            },

        ]
        if fundlist is not None:
            pipeline.insert(0, {"match": ""})

        post = self.aggregate_pipeline(pipeline)
        if not post:
            return pd.DataFrame(list([]))

        isincode_df = pd.DataFrame(list(post))

        if isincode_df.empty:
            return isincode_df

        isincode_df.set_index("howfundId", inplace=True)
        isincode_df = isincode_df.drop('_id', axis=1)

        return isincode_df




    @deprecated
    @cache_util.cached(timeout=3600)
    def get_fundlist_by_fundcode(self, fund_code, fund_id_list=None):
        """

        *Deprecated 依據fund code過濾可用的基金清單

        :param fund_code: check fund_code exists
        :type fund_code: str

        :param fund_id_list: howfundId list
        :type fund_id_list: list

        :return fund_id_list: fund_code 欄位不為空字串的 fund_id_list
        :rtype fund_id_list: str

        """
        self.setCollection("fundCode")
        projection = {"_id": 0, "howfundId": 1}
        if fund_id_list is None:
            post = self.find({fund_code: {"$ne":""}}, projection)
        else:
            post = self.find({fund_code: {"$ne": ""}, "howfundId": {"$in": list(set(fund_id_list)) }}, projection)

        df = pd.DataFrame(list(post))
        if df.empty:
            return None

        df.set_index("howfundId", inplace=True)

        return df

    def get_one_day_profit(self, fund_list=None, trade_date=None):
        """

        依據 fund_list, trade_date 取得 How_fundNavN 內最接近 trade_date 的 oneDayProfitRate 與 Nav

        :param fund_list: howfundId list
        :type fund_list: list

        :param trade_date: YYYYMMDD
        :type trade_date: str

        :return nav_df: columns["howfundId", "date", "nav", "oneDayProfitRate"]
        :rtype nav_df: dataframe

        """
        self.setCollection("How_fundNavN")
        if fund_list:
            match = {"$match": {"howfundId": {"$in": fund_list}, "date": {"$gte": trade_date}}}
        else:
            match = {"$match": { "date": {"$gte": trade_date}}}

        sort = {"$sort": {"date": 1}}
        group = {
            "$group": {
                "_id": {"howfundId": "$howfundId"},
                "howfundId": {"$last": "$howfundId"},
                "date": {"$last": "$date"},
                "nav": {"$last": "$nav"},
                "oneDayProfitRate": {"$last": "$oneDayProfitRate"}}
            }

        post = self.collection.aggregate([match, sort, group], allowDiskUse=True)
        nav_df = pd.DataFrame(list(post))

        if nav_df.empty:
            return nav_df

        nav_df.set_index("howfundId", inplace=True)
        nav_df = nav_df.drop('_id', axis=1)

        return nav_df

    def get_currency_name(self, currency_type_list):
        """

        根據 currency_type_list 到 SMT_currencyType 取得貨幣的中文名稱

        :param currency_type_list: 貨幣代號清單，例：["USD","NTD"]
        :type currency_type_list: list

        :return currency_name: 貨幣名稱物件，例：{"currency_CN": {"USD": "美元", "NTD": "新台幣"}}
        :rtype currency_name: dict

        """
        self.setCollection("SMT_currencyType")

        projection = {"_id": 0, "currency": 1, "currency_CN": 1, "name": 1}

        post = self.find({"name": {"$in": currency_type_list}}, projection)

        name_df = pd.DataFrame(list(post))

        # print(nav_df)
        if name_df.empty:
            return {}

        name_df.set_index("currency", inplace=True)

        return name_df.to_dict(orient='dict')


def CYCategoryCase(CYCategory):

    if CYCategory.find('股債混合') >= 0:
        return '平衡型'
    if CYCategory.find('貨幣市場') >= 0:
        return '貨幣型'
    if CYCategory.find('債') >= 0:
        return '債券型'
    if CYCategory.find('股') >= 0:
        return '股票型'

    return '其他'