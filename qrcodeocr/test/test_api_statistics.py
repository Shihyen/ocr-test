# -*- coding: utf8 -*-

from qrcodeocr.app import api_statistics

from qrcodeocr.test.test_base import TestBase


class TestApiStatistics(TestBase):


    def test_ApiFundStats(self):
        """
        test fund statistics api
        :return:
        """

        res = api_statistics.get_fund_stats(howfund_id=self.howfund_id,
                                            start_date=self.start_date,
                                            end_date=self.end_date)

        self.assertIsNotNone(res)
        self.assertGreater(len(res), 0)


    def test_ApiPortfolioStats(self):
        """
        test potfolio statistics api
        :return:
        """

        portfolio_df = self.mysqlutil.get_portfolio_df(self.portfolio_id)

        res = api_statistics.get_portfolio_stats(portfolio_df=portfolio_df,
                                                 start_date=self.start_date,
                                                 end_date=self.end_date)


        self.assertIsNotNone(res)
        self.assertGreater(len(res), 0)