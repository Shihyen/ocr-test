# -*- coding: utf8 -*-

from qrcodeocr.app import api_goalbase

from qrcodeocr.test.test_base import TestBase


class TestApiGoalBase(TestBase):

    def test_ApiGoalBase(self):
        """
        test goal base api
        :return:
        """

        res = api_goalbase.get_initial_goalbase(risk_level=self.risk_level,
                                                start_date=self.start_date,
                                                investment=self.investment,
                                                monthly_payment=self.monthly_payment,
                                                months=self.months)


        self.assertIsNotNone(res)
        self.assertGreater(len(res), 0)

    def test_ApiGoalBaseAsOf(self):
        """
        test goal base api for as of date
        :return:
        """

        res = api_goalbase.get_asofdate_goalbase(risk_level=self.risk_level,
                                                 start_date=self.start_date,
                                                 as_of_date=self.as_of_date,
                                                 investment=self.investment,
                                                 monthly_payment=self.monthly_payment,
                                                 months=self.months,
                                                 balance=self.balance)


        self.assertIsNotNone(res)
        self.assertGreater(len(res), 0)