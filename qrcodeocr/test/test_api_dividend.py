# -*- coding: utf8 -*-

from unittest import TestCase

from qrcodeocr.app import api_dividend
from qrcodeocr.util.mysqlutil import MySQLUtil


class TestApiDividend(TestCase):

    start_date = '2017-01-15'
    end_date = '2017-04-30'
    howfund_id = 'howF1294'
    risk_level = '5'
    portfolio_id = '29'
    mysqlutil = MySQLUtil()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ApiFundDividend(self):
        """
        test fund dividend
        :return:
        """

        res = api_dividend.get_fund_dividend(fund_id=self.howfund_id,
                                             start_date=self.start_date,
                                             end_date=self.end_date)

        self.assertIsNotNone(res)
        self.assertGreater(len(res), 0)
