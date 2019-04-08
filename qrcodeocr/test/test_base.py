# -*- coding: utf8 -*-

from unittest import TestCase

from qrcodeocr.util.mongoutil import MongoUtil
from qrcodeocr.util.mysqlutil import MySQLUtil


class TestBase(TestCase):
    """
    These shared parameters will be used for all unit tests
    """

    start_date = '2017-01-15'
    as_of_date = '2017-01-31'
    end_date = '2017-04-30'
    howfund_id = 'howF1294'
    howidx_id ='howIAM1'
    risk_level = '5'
    model = 'BL'
    portfolio_id = '130'
    investment = 10000
    monthly_payment = 1000
    months = 12
    balance=15000

    def setUp(self):
        self.mysqlutil = MySQLUtil()
        self.mongoUtil = MongoUtil()

    def tearDown(self):
        pass