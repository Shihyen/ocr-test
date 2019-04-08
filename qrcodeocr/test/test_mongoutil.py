from qrcodeocr.test.test_base import TestBase
from qrcodeocr.util.mysqlutil import MySQLUtil

mysqlutil = MySQLUtil()

class TestMongoUtil(TestBase):


    def test_fund_list_price(self):
        """
        test find method
        :return:
        """
        df = self.mongoUtil.get_fund_latest_price(['how1','how2','how3'])
        portfolio = self.mysqlutil.get_weights_by_risklevl(1)
        portfolio_df = self.mysqlutil.get_weightdf_by_risklevl(1)
        print(portfolio_df)
        portfolio_df['total_value'] = 10000 * portfolio_df['weight']
        print(portfolio_df)

        print(list(portfolio.keys()))
        flp_df = self.mongoUtil.get_fund_latest_price(list(portfolio.keys()))
        portfolio_df['unit'] = portfolio_df['total_value'] / flp_df['nav']
        print(flp_df)
        self.assertIsNotNone(df)
        self.assertGreater(df.size, 0)

    def test_ytd_price(self):
        """
        test find method
        :return:
        """
        df = self.mongoUtil.list_latest_index_rt_price_0(['howIEU11','howIEU12','howIEU31'])
        print(df)
        self.assertIsNotNone(df)
        self.assertGreater(df.size, 0)


    def test_find(self):
        """
        test find method
        :return:
        """
        df = self.mongoUtil.get_fund_price(self.howfund_id, self.start_date, self.end_date)
        print(df)
        self.assertIsNotNone(df)
        self.assertGreater(df.size, 0)


