import unittest
from unittest import mock

import comexdown


@mock.patch("comexdown.download")
class TestFunctions(unittest.TestCase):

    def test_get_year(self, mock_download):
        comexdown.get_year(year=2000, exp=True, imp=True)
        mock_download.exp.assert_called()
        mock_download.imp.assert_called()
        comexdown.get_year(year=2000, exp=True, imp=True, mun=True)
        mock_download.exp_mun.assert_called()
        mock_download.imp_mun.assert_called()

    def test_get_year_nbm(self, mock_download):
        comexdown.get_year_nbm(2000, exp=True, imp=True)
        mock_download.exp_nbm.assert_called()
        mock_download.imp_nbm.assert_called()

    def test_get_complete(self, mock_download):
        comexdown.get_complete(exp=True, imp=True)
        mock_download.exp_complete.assert_called()
        mock_download.imp_complete.assert_called()
        comexdown.get_complete(exp=True, imp=True, mun=True)
        mock_download.exp_mun_complete.assert_called()
        mock_download.imp_mun_complete.assert_called()

    def test_get_table(self, mock_download):
        comexdown.get_table("ncm")
        mock_download.table.assert_called()


if __name__ == "__main__":
    unittest.main()
