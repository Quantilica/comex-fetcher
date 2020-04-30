import argparse
import os
import unittest
from unittest import mock

from comexdown import cli
from comexdown import download as d


class TestCliFunctions(unittest.TestCase):

    def test_set_parser(self):
        parser = cli.set_parser()
        self.assertIsInstance(parser, argparse.ArgumentParser)

    def test_expand_years(self):
        years = cli.expand_years(["2010:2019", "2000:2005"])
        self.assertListEqual(
            years,
            [y for y in range(2010, 2020)] + [y for y in range(2000, 2006)]
        )
        years = cli.expand_years(["2000:2005", "2010:2019"])
        self.assertListEqual(
            years,
            [y for y in range(2000, 2006)] + [y for y in range(2010, 2020)]
        )
        years = cli.expand_years(["2000:2005", "2010"])
        self.assertListEqual(
            years,
            [y for y in range(2000, 2006)] + [2010]
        )
        years = cli.expand_years(["2010", "2000:2005"])
        self.assertListEqual(
            years,
            [2010] + [y for y in range(2000, 2006)]
        )
        years = cli.expand_years(["2010", "2005:2000"])
        self.assertListEqual(
            years,
            [2010] + [2005, 2004, 2003, 2002, 2001, 2000]
        )

    @mock.patch("comexdown.cli.set_parser")
    def test_main(self, mock_set_parser):
        cli.main()
        mock_set_parser.assert_called()
        parser = mock_set_parser.return_value
        parser.parse_args.assert_called()
        args = parser.parse_args.return_value
        args.func.assert_called()


class TestCliDownloadTrade(unittest.TestCase):

    def setUp(self):
        self.parser = cli.set_parser()
        self.args = self.parser.parse_args(
            [
                "download",
                "trade",
                "2010",
                "-o",
                os.path.join(".", "DATA"),
            ]
        )

    @mock.patch("comexdown.cli.download.imp")
    @mock.patch("comexdown.cli.download.exp")
    def test_download_trade_mun(self, mock_exp, mock_imp):
        self.args.func(self.args)
        mock_exp.assert_called()
        mock_imp.assert_called()


class TestCliDownloadTradeMun(unittest.TestCase):

    def setUp(self):
        self.parser = cli.set_parser()
        self.args = self.parser.parse_args(
            [
                "download",
                "trade",
                "2010",
                "-o",
                os.path.join(".", "DATA"),
                "-mun"
            ]
        )

    @mock.patch("comexdown.cli.download.imp_mun")
    @mock.patch("comexdown.cli.download.exp_mun")
    def test_download_trade_mun(self, mock_exp_mun, mock_imp_mun):
        self.args.func(self.args)
        mock_exp_mun.assert_called()
        mock_imp_mun.assert_called()


class TestCliDownloadTradeNbm(unittest.TestCase):

    def setUp(self):
        self.parser = cli.set_parser()
        self.args = self.parser.parse_args(
            [
                "download",
                "trade",
                "1990",
                "-o",
                os.path.join(".", "DATA"),
                "-nbm",
            ]
        )

    @mock.patch("comexdown.cli.download.imp_nbm")
    @mock.patch("comexdown.cli.download.exp_nbm")
    def test_download_trade_nbm(self, mock_exp_nbm, mock_imp_nbm):
        self.args.func(self.args)
        mock_exp_nbm.assert_called()
        mock_imp_nbm.assert_called()


class TestCliDownloadCode(unittest.TestCase):

    def setUp(self):
        self.parser = cli.set_parser()
        self.args = self.parser.parse_args(
            [
                "download",
                "code",
                "all",
                "-o",
                os.path.join(".", "DATA"),
            ]
        )

    @mock.patch("comexdown.cli.download.code")
    def test_download_code(self, mock_code):
        self.args.func(self.args)
        mock_code.assert_called()
        self.assertEqual(mock_code.call_count, len(d.CODE_TABLES))


class TestCliDownloadNcm(unittest.TestCase):

    def setUp(self):
        self.parser = cli.set_parser()
        self.args = self.parser.parse_args(
            [
                "download",
                "ncm",
                "all",
                "-o",
                os.path.join(".", "DATA"),
            ]
        )

    @mock.patch("comexdown.cli.download.ncm")
    def test_download_ncm(self, mock_ncm):
        self.args.func(self.args)
        mock_ncm.assert_called()
        self.assertEqual(mock_ncm.call_count, len(d.NCM_TABLES))


class TestCliDownloadNbm(unittest.TestCase):

    def setUp(self):
        self.parser = cli.set_parser()
        self.args = self.parser.parse_args(
            [
                "download",
                "nbm",
                "all",
                "-o",
                os.path.join(".", "DATA"),
            ]
        )

    @mock.patch("comexdown.cli.download.nbm")
    def test_download_nbm(self, mock_nbm):
        self.args.func(self.args)
        mock_nbm.assert_called()
        self.assertEqual(mock_nbm.call_count, len(d.NBM_TABLES))


if __name__ == "__main__":
    unittest.main()
