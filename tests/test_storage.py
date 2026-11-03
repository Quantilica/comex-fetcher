import datetime as dt
import unittest
from pathlib import Path

from comex_fetcher.storage import DataRepository


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.root = Path("tmp").resolve()
        self.root.mkdir(exist_ok=True)
        self.repo = DataRepository(self.root)

    def test_path_aux(self):
        today = dt.date.today().strftime("%Y%m%d")
        path = self.repo.path_aux("ncm")
        self.assertEqual(path, self.root / "auxiliary-tables" / f"ncm@{today}.csv")

    def test_path_trade(self):
        today = dt.date.today().strftime("%Y%m%d")
        path = self.repo.path_trade("exp", 2020, mun=False)
        self.assertEqual(path, self.root / "exp" / f"exp_2020@{today}.csv")
        path = self.repo.path_trade("imp", 2020, mun=False)
        self.assertEqual(path, self.root / "imp" / f"imp_2020@{today}.csv")
        path = self.repo.path_trade("exp", 2020, mun=True)
        self.assertEqual(path, self.root / "exp-mun" / f"exp-mun_2020@{today}.csv")
        path = self.repo.path_trade("imp", 2020, mun=True)
        self.assertEqual(path, self.root / "imp-mun" / f"imp-mun_2020@{today}.csv")

    def test_path_trade_nbm(self):
        today = dt.date.today().strftime("%Y%m%d")
        path = self.repo.path_trade_nbm("exp", 1990)
        self.assertEqual(path, self.root / "exp-nbm" / f"exp-nbm_1990@{today}.csv")
        path = self.repo.path_trade_nbm("imp", 1990)
        self.assertEqual(path, self.root / "imp-nbm" / f"imp-nbm_1990@{today}.csv")

    def test_path_for_entry_fallback_timestamp(self):
        """Test that when last_modified is None, today's date is used as @YYYYMMDD."""
        today = dt.date.today()
        today_str = today.strftime("%Y%m%d")

        # Trade entry (exp)
        entry = {"is_trade": True, "direction": "exp", "year": 2023, "mun": False}
        path = self.repo.path_for_entry(entry, last_modified=None)
        expected = self.root / "exp" / f"exp_2023@{today_str}.csv"
        self.assertEqual(path, expected)

        # Trade entry with NBM
        entry = {"is_trade": True, "direction": "imp", "year": 1990, "nbm": True}
        path = self.repo.path_for_entry(entry, last_modified=None)
        expected = self.root / "imp-nbm" / f"imp-nbm_1990@{today_str}.csv"
        self.assertEqual(path, expected)

        # Auxiliary table entry
        entry = {"is_table": True, "table_group": "auxiliary", "id": "ncm"}
        path = self.repo.path_for_entry(entry, last_modified=None)
        expected = self.root / "auxiliary-tables" / f"ncm@{today_str}.csv"
        self.assertEqual(path, expected)


if __name__ == "__main__":
    unittest.main()
