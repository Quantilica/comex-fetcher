import unittest
from pathlib import Path

from comex_fetcher.storage import DataRepository


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.root = Path("tmp").resolve()
        self.root.mkdir(exist_ok=True)
        self.repo = DataRepository(self.root)

    def test_path_aux(self):
        path = self.repo.path_aux("ncm")
        self.assertEqual(path, self.root / "auxiliary-tables" / "ncm.csv")

    def test_path_trade(self):
        path = self.repo.path_trade("exp", 2020, mun=False)
        self.assertEqual(path, self.root / "exp" / "exp_2020.csv")
        path = self.repo.path_trade("imp", 2020, mun=False)
        self.assertEqual(path, self.root / "imp" / "imp_2020.csv")
        path = self.repo.path_trade("exp", 2020, mun=True)
        self.assertEqual(path, self.root / "exp-mun" / "exp-mun_2020.csv")
        path = self.repo.path_trade("imp", 2020, mun=True)
        self.assertEqual(path, self.root / "imp-mun" / "imp-mun_2020.csv")

    def test_path_trade_nbm(self):
        path = self.repo.path_trade_nbm("exp", 1990)
        self.assertEqual(path, self.root / "exp-nbm" / "exp-nbm_1990.csv")
        path = self.repo.path_trade_nbm("imp", 1990)
        self.assertEqual(path, self.root / "imp-nbm" / "imp-nbm_1990.csv")


if __name__ == "__main__":
    unittest.main()

