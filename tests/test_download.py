import http.client
import unittest
from pathlib import Path
from unittest import mock

from comexdown import download


class TestDownloadFile(unittest.TestCase):
    @mock.patch("comexdown.download.sys")
    @mock.patch("urllib.request.urlopen")
    @mock.patch("urllib.request.Request")
    @mock.patch("os.rename")
    @mock.patch("os.utime")
    @mock.patch("os.remove")
    @mock.patch("comexdown.download.remote_is_more_recent")
    def test_download_file(self, mock_recent, mock_remove, mock_utime, mock_rename, mock_request, mock_urlopen, mock_sys):
        # Setup mock for HEAD request response
        mock_head_resp = mock.MagicMock()
        mock_head_resp.headers = http.client.HTTPMessage()
        mock_head_resp.headers["Content-Length"] = "9"
        mock_head_resp.__enter__.return_value = mock_head_resp

        # Setup mock for GET request response
        mock_get_resp = mock.MagicMock()
        mock_get_resp.headers = http.client.HTTPMessage()
        mock_get_resp.headers["Content-Length"] = "9"
        mock_get_resp.read.side_effect = [b"some data", b""]
        mock_get_resp.__enter__.return_value = mock_get_resp

        # urlopen is called twice: once for HEAD, once for GET
        mock_urlopen.side_effect = [mock_head_resp, mock_get_resp]
        mock_recent.return_value = True

        # Use mock_open for the file operations
        with mock.patch("builtins.open", mock.mock_open()) as mock_open:
            download.download_file(
                "http://www.example.com/file.csv", Path("data/file.csv"))

        # Check if urlopen was called
        self.assertEqual(mock_urlopen.call_count, 2)
        mock_rename.assert_called()


if __name__ == "__main__":
    unittest.main()
