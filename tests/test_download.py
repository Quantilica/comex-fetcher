import unittest
from unittest import mock

from comexdown import download


class TestDownload(unittest.TestCase):
    @mock.patch("comexdown.download.download")
    def test_exp(self, mock_download):
        download.exp(2019, ".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/ncm/EXP_2019.csv",
            ".\\DATA\\exp",
        )

    @mock.patch("comexdown.download.download")
    def test_imp(self, mock_download):
        download.imp(2019, ".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/ncm/IMP_2019.csv",
            ".\\DATA\\imp",
        )

    @mock.patch("comexdown.download.download")
    def test_exp_mun(self, mock_download):
        download.exp_mun(2019, ".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/mun/EXP_2019_MUN.csv",
            ".\\DATA\\exp_mun",
        )

    @mock.patch("comexdown.download.download")
    def test_imp_mun(self, mock_download):
        download.imp_mun(2019, ".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/mun/IMP_2019_MUN.csv",
            ".\\DATA\\imp_mun",
        )

    @mock.patch("comexdown.download.download")
    def test_exp_nbm(self, mock_download):
        download.exp_nbm(1990, ".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/nbm/EXP_1990_NBM.csv",
            ".\\DATA\\exp_nbm",
        )

    @mock.patch("comexdown.download.download")
    def test_imp_nbm(self, mock_download):
        download.imp_nbm(1990, ".\\DATA")
        mock_download.assert_called_with(
            "http://www.mdic.gov.br/balanca/bd/comexstat-bd/nbm/IMP_1990_NBM.csv",
            ".\\DATA\\imp_nbm",
        )


if __name__ == "__main__":
    unittest.main()
