# -*- coding: utf8 -*-

from qrcodeocr.app import api_histprice

from qrcodeocr.test.test_base import TestBase


class TestApiFundHistPrice(TestBase):

    def test_ApiFundHistPrice(self):
        """
        test fund historical price api
        :return:
        """
        res = api_histprice.get_fund_price(howfund_id=self.howfund_id,
                                           start_date=self.start_date,
                                           end_date=self.end_date)

        self.assertIsNotNone(res)

    def test_ApiRoboHistPrice(self):
        """
        test robo portfolio historical price api
        :return:
        """

        portfolio_df = self.mysqlutil.get_weightdf_by_risklevl(self.risk_level)

        self.assertIsNotNone(portfolio_df)

        res = api_histprice.get_portfolio_price(portfolio_df=portfolio_df,
                                                start_date=self.start_date,
                                                end_date=self.end_date)

        self.assertIsNotNone(res)
        self.assertGreater(len(res), 0)


    def test_ApiPortfolioHistPrice(self):
        """
        test user defined portfolio historical price api
        :return:
        """

        portfolio_df = self.mysqlutil.get_portfolio_df(self.portfolio_id)

        self.assertIsNotNone(portfolio_df)

        res = api_histprice.get_portfolio_price(portfolio_df=portfolio_df,
                                                start_date=self.start_date,
                                                end_date=self.end_date)
        self.assertIsNotNone(res)

