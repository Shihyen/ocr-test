# -*- coding: utf-8 -*-
import json

import pandas as pd
import pymysql
from qrcodeocr.common import configure
from pandas import DataFrame
from sqlalchemy import create_engine


class MySQLUtil:
    def __init__(self):
        pass

    def connect(self):
        # Connect to the database
        self.connection = pymysql.connect(host=configure.db_host,
                                          user=configure.db_user,
                                          password=configure.db_pw,
                                          db=configure.db_name,
                                          charset='utf8')

    def close(self):
        self.connection.close()

    def fetchone(self, sql, parameters=()):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                cursor.execute(sql, parameters)
                result = cursor.fetchone()
                return result
        finally:
            self.close()

    def fetchall(self, sql, parameters=()):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                cursor.execute(sql, parameters)
                result = cursor.fetchall()
                return result
        finally:
            self.close()

    def insert(self, sql, parameters=()):
        try:
            self.connect()
            with self.connection.cursor() as cursor:
                cursor.execute(sql, parameters)
                self.connection.commit()
        finally:
            self.close()

    def get_robo_portfolio(self, risklevel):

        sqlstr = "SELECT a.id, a.date, a.name, a.risk_level, a.return, a.std, a.sharp, a.stock_ratio, a.weights " \
                 "FROM robo_portfolios a " \
                 "JOIN " \
                 "(SELECT max(id) as id FROM robo_portfolios WHERE risk_level = %s) b " \
                 "ON (a.id = b.id)"

        rs = self.fetchone(sqlstr, risklevel)

        return rs

    def list_robo_portfolio(self):

        sqlstr = "SELECT a.id, a.date, a.name, a.risk_level, a.return, a.std, a.sharp, a.stock_ratio, a.weights " \
                 "FROM robo_portfolios a " \
                 "JOIN " \
                 "(SELECT max(id) as id FROM robo_portfolios GROUP BY risk_level) b " \
                 "ON (a.id = b.id)"

        rs = self.fetchall(sqlstr)

        return rs

    def get_rtn_std(self, risklevel):

        rs = self.get_robo_portfolio(risklevel)

        rtn = rs[4]
        std = rs[5]

        return rtn, std

    def get_weights_by_risklevl(self, risklevel):

        rs = self.get_robo_portfolio(risklevel)
        weights = json.loads(rs[8])

        return weights

    def get_weightdf_by_risklevl(self, risklevel):

        rs = self.get_robo_portfolio(risklevel)
        weights = json.loads(rs[8])

        fund_list = []
        weight_list = []
        # currency_list = []
        for k, v in weights.iteritems():
            fund_list.append(k)
            weight_list.append(float(v))

        weights_df = DataFrame(weight_list, index=fund_list, columns=['weight'])

        return weights_df


    def get_portfolio_ingredient(self, portfolio_id):
        sqlstr = "SELECT a.portfolio_id, a.trade_date, a.fund_id, a.unit, a.cost, a.unit_price, a.cost_unit_price, a.weight " \
                 "FROM howfintech.portfolio_ingredients a " \
                 "where a.portfolio_id = %s "
        rs = self.fetchall(sqlstr, portfolio_id)

        return rs
if __name__ == '__main__':
    test = MySQLUtil()
    # sql = "INSERT INTO `test` (`email`, `password`) VALUES (%s, %s)"
    # args = ('ericlee@howfintech.com', '1234')
    # rs = test.insert(sql, args)

    # rs = test.fetchone("SELECT * FROM  optimized_portfolio WHERE id = 20")
    # rs = test.fetchone("SELECT * FROM  optimized_portfolio WHERE id = 20")

    # print(rs)
    # rs = test.fetchone("SELECT * FROM  optimized_portfolio WHERE id = %s", "20")
    #
    # print(rs)
    #
    # rs = test.fetchone("SELECT expected_return, std, risk_level from optimized_portfolio where risk_level = %s", "5")
    # print(rs)

    # rs = test.list_robo_portfolio()
    # for r in rs:
    #     print(r)



    engine = create_engine('mysql://howdev:Howfintech@192.168.10.204/algorithm', pool_size=10)
    df = pd.read_sql(
        'SELECT a.portfolio_id, a.trade_date, a.fund_id, a.unit FROM howfintech.portfolio_ingredients a where a.portfolio_id = %s',
        engine, params="29", index_col=['fund_id'])
    print(df)
    print(df.unit)
    # db_host = '192.168.10.204'
    # db_user = 'howdev'
    # db_pw = 'Howfintech'
    # db_name = 'algorithm'
