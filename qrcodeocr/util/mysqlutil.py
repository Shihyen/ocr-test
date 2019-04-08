# -*- coding: utf-8 -*-
import json
import logging
import time

import pandas as pd
import sqlalchemy
from qrcodeocr.common import configure
from pandas import DataFrame
from qrcodeocr.util import utility
from qrcodeocr.util import cache_util

logger = logging.getLogger(__name__)

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        #print("know type: %s" % x)
        return x.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(x, datetime.date):
        #print("know type: %s" % x)
        return x.strftime('%Y-%m-%d')

class MySQLUtil:
    def __init__(self):
        try:
            # print(configure.mysql_url)
            self.engine = sqlalchemy.create_engine(configure.mysql_url)
            self.logEnabled = configure.db_logEnabled


        except Exception as e:
            print(e)

    def connect(self):
        self.connection = self.engine.connect()

    def close(self):
        self.connection.close()

    def log(self, st, sqlstr, params=()):

        if (self.logEnabled):
            timediff = int((time.time() - st) * 1000)

            logger.info('[MySQLLOG] Time(ms):[%s] SQL:[%s] Parameter:[%s]', timediff, sqlstr, params)

    def fetchone(self, sql, params=()):
        st = time.time()
        result = None
        try:
            self.connect()
            result = self.connection.execute(sql, params).fetchone()

        finally:
            self.close()

        self.log(st, sql, params)

        return result

    def fetchmany(self, sql, params=(), size=1):
        st = time.time()

        try:
            self.connect()
            result = self.connection.execute(sql, params).fetchmany(size)

        finally:
            self.close()

        self.log(st, sql, params)

        return result

    def fetchall(self, sql, params=()):
        st = time.time()
        try:
            self.connect()
            result = self.connection.execute(sql, params).fetchall()

        finally:
            self.close()

        self.log(st, sql, params)
        return result

    def insert(self, sql, params=()):
        st = time.time()

        try:
            self.connect()
            res = self.connection.execute(sql, params)
            return res.lastrowid
        finally:
            self.close()

        self.log(st, sql, params)

    def update(self, sql, params=()):
        return self.insert(sql, params)

    def read_sql(self, sqlstr, params=(), index_col=None):
        st = time.time()
        result = None
        try:
            result = pd.read_sql(sqlstr, self.engine, params=params, index_col=index_col)
        except Exception as e:
            print(str(e))
            logger.error("read_sql exception: " + str(e))

        self.log(st, sqlstr, params)
        return result

    #################################################################################
    #                                                                               #
    #       Functions below are application specified functions                     #
    #                                                                               #
    #       Use prefix: "get_" for single item lookup                               #
    #       Use prefix: "list_" for multiple items lookup                           #
    #                                                                               #
    #       By default, the result will be a DataFrame                              #
    #                                                                               #
    #################################################################################

    # smart select
    def _convert_value(self, row):
        """
        convert the value based on the datatype
        :param row:
        :return:
        """

        if row['datatype'] == 'int':
            row['value'] = int(row['value'])
        elif row['datatype'] == 'float':
            row['value'] = float(row['value'])
        elif row['datatype'] == 'bool':
            row['value'] = utility.str2bool(row['value'])

        return row

    @cache_util.cached(timeout=86400)
    def get_fund_categories(self, enabled_only=False, index_col='category'):
        """
        get all fund categories dataframe

        optional: filtering by "enabled" flag

        :param enabled_only:
        :return: dataframe
        """
        sqlstr = "SELECT category, fund_type, enabled, benchmark_id, riskfree_idx_id, query, algorithmCategory " \
                 "FROM fund_categories "
        if enabled_only:
            sqlstr += "WHERE enabled = 1"

        df = self.read_sql(sqlstr, index_col=[index_col])

        return df

    @cache_util.cached(timeout=3600)
    def get_fund_scores(self, fund_list, gtedate=None, ltedate=None):
        """
        從 mysql的 fund_score取出符合條件的清單，若有帶起訖日，則會加入查詢條件，查詢某段期間內最新一筆fund_score

        :param fund_list: howfundId list
        :type fund_list: list

        :param gtedate: 起始日 YYYYMMDD
        :type gtedate: str

        :param ltedate: 迄日 YYYYMMDD
        :type ltedate: str

        :return fund_score: columns :[category, majorHowfundId, adWeightedScore, date,
                 weighted_score, ad_weight, fund_scale_score, fund_years_score, manager_tenure_score,
                 agent_score, std_score, mdd_score, sortino_score, momemtum_score, ir_score, upr_score ]
        :rtype fund_score: dataframe

        """
        date_str = " 1=1 "
        param = ["1"]
        if gtedate is not None:
            date_str = date_str + " AND date >= %s"
            param.append(gtedate)

        if ltedate is not None:
            date_str = date_str + " AND date <= %s"
            param.append(ltedate)


        param.append(fund_list)


        sqlstr = "select category, howfundId as majorHowfundId, ad_weighted_score as adWeightedScore, date, " \
                 " weighted_score, ad_weight, fund_scale_score, fund_years_score, manager_tenure_score, " \
                 " agent_score, std_score, mdd_score, sortino_score, momemtum_score, ir_score, upr_score " \
                 " from algorithm.fund_rankings_details where 1=%s " \
                 " AND date = (select max(date) from algorithm.fund_rankings_details " \
                 " where " + date_str + ") AND howfundId IN %s "

        df = self.read_sql(sqlstr, index_col=['majorHowfundId'], params=param)
        return df

    def get_algo_configuration(self, type):
        """
        get the algo configuration by type
        :param type:
        :return:
        """

        sqlstr = "select type, name, datatype, value " \
                 "from algo_configuration " \
                 "where type = %s"

        df = self.read_sql(sqlstr, params=[type], index_col=['name'])
        df.apply(self._convert_value, axis=1)

        return df

    def list_full_fund_rankings_by_date(self, date):
        """
        list all fund ranking data by date
        :param date:
        :return: dataframe
        """
        sqlstr = "select date, category, fund_type, group_size, rankings, ad_rankings, rankings_ma, ad_rankings_ma " \
                 "from fund_rankings_v2 " \
                 "where date = " \
                 "(select max(date) from fund_rankings_v2 where rankings_ma is not null and date <= %s)"

        df = self.read_sql(sqlstr, params=[date], index_col=['category'])

        return df

    def list_fund_power_promote(self, date):
        """
        retrieve agent recommendations fund list from mysql
        :return:
        """
        sqlstr = "select start_date as startdate, end_date as enddate, fund_id as howfundId, category, " \
                 "ranking as power_ranking " \
                 "from fund_power_promote " \
                 "where enabled = 1 " \
                 "and start_date <= %s " \
                 "and end_date >= %s " \
                 "order by category, ranking"

        df = self.read_sql(sqlstr, params=[date, date], index_col=['category', 'howfundId'])

        return df

    def list_optimizer_constraints(self):
        """
        list all optimizer constraints for all risk level
        :return:
        """
        sqlstr = "select risk_level, category, fund_type, fund_count, lower, upper, equal, ind_lower, ind_upper " \
                 "from algorithm.optimizer_constraints "

        df = self.read_sql(sqlstr, index_col=['risk_level', 'category'])

        return df

    def get_fund_by_pool(self, pool_id):
        """

        :param pool_id:
        :param date:
        :return:
        """
        sqlstr = "select pool_id, start_date as startdate, end_date as enddate, fund_id as howfundId " \
                 "from fund_pool " \
                 "where enabled=1 " \
                 "and pool_id = %s "

        df = self.read_sql(sqlstr, params=[pool_id], index_col=['howfundId'])

        return df

    def get_smart_select_cache(self, fund_list, cached_date, general_issuer=None, currency_type=None, fund_type=None):
        """

        取得SmartSelect 第一層Cache

        :param fund_list: howfundId list
        :type fund_list: list

        :param cached_date: 快取日期
        :type cached_date: str

        :param general_issuer: 過濾 generalIssuer 欄位的條件
        :type general_issuer: list

        :param currency_type: 過濾 currencyType 欄位的條件
        :type: currency_type: list

        :param currency_type: 過濾 fundTypeName 欄位的條件
        :type: currency_type: list

        :return df: columns: [howfundId, chineseFullName, constituents, currencyType, fundShortName, generalIssuer,
                    fundCategory, majorHowfundId, fundTypeName, date, nav, oneDayProfitRate, correlation, fundScore]
        :rtype : dataframe

        """

        params = [1]

        if general_issuer is not None and len(general_issuer) > 0:
            query_str = " AND generalIssuer IN %s "
            params.append(general_issuer)
        else:
            query_str = ""

        if currency_type is not None and len(currency_type) > 0:
            query_str += " AND currencyType IN %s "
            params.append(currency_type)
        else:
            query_str += ""

        if fund_type is not None and len(fund_type) > 0:
            query_str += " AND fundTypeName IN %s "
            params.append(fund_type)
        else:
            query_str += ""

        params.append(fund_list)
        params.append(cached_date)

        sqlstr = " SELECT howfundId, chineseFullName, constituents, currencyType, " \
                 " fundShortName, generalIssuer, fundCategory, majorHowfundId, fundTypeName, date, nav, oneDayProfitRate, " \
                 " correlation, fundScore, isinCode, currencyCode, warningMessage " \
                 " FROM smart_select_cache " \
                 " WHERE 1=%s " \
                 + query_str + \
                 " AND howfundId IN %s AND cached_date = (select max(cached_date) from smart_select_cache where cached_date <= %s) "

        df = self.read_sql(sqlstr, params=params, index_col=['howfundId'])


        return df

    def smart_select_fund_cache(self, fundlist, cached_date=None):
        """

        將SmartSelect整理好的第一層快取寫入Mysql

        :param fundlist: 寫入db的清單
        :type fundlist: list

        :param cached_date: 快取日期，一天一次，所以設定快取日期
        :type cached_date: str

        :return db_insert_id: db 最後更新的流水號
        :rtype db_insert_id: int

        """
        fund_data = []
        for key, item in fundlist.iterrows():

            item['constituents'] = json.dumps([dict(r) for r in item['constituents']], default=datetime_handler)
            item['cached_date'] = cached_date
            fund_data.append(item)

        key = ('howfundId', 'CYCategory', 'fundCategory', 'chineseFullName', 'constituents', 'currencyType',
               'fundShortName', 'generalIssuer', 'majorHowfundId', 'tejCategory', 'warningMessage', 'fundTypeName', 'date', 'nav',
               'oneDayProfitRate', 'CurrencyCode', 'IsinCode', 'correlation', 'fundScore', 'cached_date')


        sqlstr = "INSERT INTO smart_select_cache(" + ",".join(key) + ") VALUES(" + ",".join(['%s' for i in key]) + ")"

        self.update("TRUNCATE smart_select_cache")
        id = self.insert(sqlstr, fund_data)

        return id

    @cache_util.cached(timeout=3600*24)
    def get_smart_select_column(self, fund_list, date, column):
        """

        根據條件查詢SmartSelectCache欄位清單，快取一天

        :param fund_list: 基金清單
        :param date: cache 的日期
        :param column: 要dintinct的欄位
        :return: 按照筆畫順序回傳清單
        :rtype: dataframe
        """
        params = [1, fund_list, date]

        sqlstr = " SELECT DISTINCT " + column + " as name " \
                 " FROM smart_select_cache " \
                 " WHERE 1=%s AND " + column + " != '' "  \
                 " AND howfundId IN %s AND cached_date = %s " \
                 " ORDER BY CAST(CONVERT(" + column + " using big5) AS BINARY) ASC "

        df = self.read_sql(sqlstr, params=params)

        return df

    @cache_util.cached(timeout=3600)
    def get_smart_select_cache_info(self):

        sqlstr = "SELECT cached_date as date, count(*) AS transactionCount FROM smart_select_cache " \
                " GROUP BY cached_date "

        res = self.fetchone(sqlstr)
        if res is None:
            return None

        return {'date': res[0], 'transactionCount': res[1]}

    # @cache_util.cached(timeout=3600)
    def get_fund_code_list(self, fund_code):
        """
        取得 fund_code 對應的fund_list
        :param func_code:
        :return:
        """

        sqlstr = " SELECT howfundId, isinCode, currencyCode FROM smart_select_cache WHERE  " \
                 " cached_date = (SELECT MAX(cached_date) FROM smart_select_cache) "

        return self.fetchall(sqlstr)

    def save_smart_select_sharing(self, sharing_code, data):

        if self.get_smart_select_sharing(sharing_code):
            return False

        data = json.dumps(data, default=datetime_handler)

        sqlstr = "INSERT INTO smart_select_sharing(sharing_code, params) VALUES(%s, %s)"

        id = self.insert(sqlstr, [sharing_code, data])

        return id

    def get_smart_select_sharing(self, sharing_code):

        sqlstr = " SELECT params FROM smart_select_sharing WHERE sharing_code = %s "

        res = self.fetchone(sqlstr, [sharing_code])
        if res is None:
            return None
        # print(res[0])

        sqlstr = "UPDATE smart_select_sharing SET sharing_count = sharing_count + 1 WHERE sharing_code = %s "
        self.update(sqlstr, params=sharing_code)

        return res[0]

    def save_smart_select_nav_cache(self, nav):

        data = []
        for howfundId, item in nav.items():
            data.append(howfundId)
            data.append(item['nav'])
            data.append(utility.format_date_api(item['date'], '%Y%m%d', '%Y-%m-%d'))
            data.append(item['oneDayProfitRate'])

        self.update("TRUNCATE smart_select_cache_tmp")

        sqlstr = "INSERT INTO smart_select_cache_tmp(howfundId, nav, date, oneDayProfitRate) VALUES " \
                 + ",".join(['(%s,%s,%s,%s)' for i in nav])
        self.insert(sqlstr, data)

        sqlstr = "UPDATE smart_select_cache a INNER JOIN smart_select_cache_tmp b ON a.howfundId = b.howfundId " \
                 "SET a.nav = b.nav, a.date = b.date, a.oneDayProfitRate = b.oneDayProfitRate"
        return self.update(sqlstr)


    def get_smart_select_fund_detail(self, howfundId, fields=None):

        if fields:
            sqlstr = "SELECT " + ",".join(fields) + " FROM smart_select_cache WHERE howfundId = %s "
            res = self.fetchone(sqlstr, [howfundId])

            if res is None:
                return None

            return res
        else:

            return None