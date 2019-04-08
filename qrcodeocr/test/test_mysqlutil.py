# -*- coding: utf8 -*-

from qrcodeocr.test.test_base import TestBase

class TestMySQLUtil(TestBase):

    def test_get_robo_portfolio(self):
        """
        test robo potfolios method
        :return:
        """
        res = self.mysqlutil.get_robo_portfolio(self.risk_level)
        self.assertIsNotNone(res)
        self.assertGreater(len(res), 0)

