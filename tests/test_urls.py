import unittest

from comex_fetcher import urls


class TestUrls(unittest.TestCase):
    def test_trade_ncm_exp(self):
        url = urls.trade(direction="exp", year=2019)
        self.assertEqual(
            url,
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2019.csv",
        )

    def test_trade_ncm_imp(self):
        url = urls.trade(direction="imp", year=2019)
        self.assertEqual(
            url,
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2019.csv",
        )

    def test_trade_mun_exp(self):
        url = urls.trade(direction="exp", year=2019, mun=True)
        self.assertEqual(
            url,
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/mun/EXP_2019_MUN.csv",
        )

    def test_trade_mun_imp(self):
        url = urls.trade(direction="imp", year=2019, mun=True)
        self.assertEqual(
            url,
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/mun/IMP_2019_MUN.csv",
        )

    def test_trade_nbm_exp(self):
        url = urls.trade(direction="exp", year=1990, nbm=True)
        self.assertEqual(
            url,
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/nbm/EXP_1990_NBM.csv",
        )

    def test_trade_nbm_imp(self):
        url = urls.trade(direction="imp", year=1990, nbm=True)
        self.assertEqual(
            url,
            "https://balanca.economia.gov.br/balanca/bd/comexstat-bd/nbm/IMP_1990_NBM.csv",
        )

