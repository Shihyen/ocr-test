# -*- coding: utf8 -*-

from qrcodeocr.app import api_constituent

from qrcodeocr.test.test_base import TestBase


class TestApiConstituent(TestBase):

    def test_ApiFundConstituent(self):
        """
        test fund constituent
        :return:
        """

        res = api_constituent.get_fund_constituent(howfund_id=self.howfund_id)

        self.assertIsNotNone(res)
        self.assertGreater(len(res), 0)

    def test_ApiRoboConstituent(self):
        """
        test robo portfolio constituent
        :return:
        """

        portfolio_df = self.mysqlutil.get_weightdf_by_risklevl(self.risk_level)

        res = api_constituent.get_portfolio_constituent(portfolio_df)

        self.assertIsNotNone(res)
        self.assertGreater(len(res), 0)
