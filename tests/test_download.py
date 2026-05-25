import unittest
from pathlib import Path
from unittest import mock

from comex_fetcher import download


class TestDownloadFile(unittest.TestCase):
    @mock.patch("comex_fetcher.download.client.download_with_manifest")
    def test_download_file(self, mock_download):
        # Setup mock return value
        mock_path = Path("data/file.csv")
        mock_download.return_value = mock_path

        url = "http://www.example.com/file.csv"
        output = Path("data/file.csv")

        result = download.download_file(url, output)

        # Check if download_with_manifest was called with correct arguments
        mock_download.assert_called_once_with(
            url,
            output,
            source_id="comexstat",
            dataset_id="data",
            producer="comex-fetcher",
        )
        self.assertEqual(result, mock_path)


if __name__ == "__main__":
    unittest.main()
