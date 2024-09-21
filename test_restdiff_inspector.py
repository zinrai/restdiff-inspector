#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import json
from io import StringIO
import sys
import urllib.error

# Import the functions from your main script
from restdiff_inspector import fetch_data, extract_data, compare_data, main

class TestRestDiffInspector(unittest.TestCase):

    def test_fetch_data(self):
        mock_data = {"key": "value"}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_data).encode()

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.return_value.__enter__.return_value = mock_response
            result = fetch_data("http://example.com")

        self.assertEqual(result, mock_data)

    @patch('sys.stderr', new_callable=StringIO)
    def test_fetch_data_error(self, mock_stderr):
        with patch('urllib.request.urlopen', side_effect=urllib.error.URLError("Error")):
            with self.assertRaises(SystemExit):
                fetch_data("http://example.com")

        error_output = mock_stderr.getvalue()
        self.assertIn("Error fetching data from http://example.com", error_output)

    def test_extract_data(self):
        data = {
            "level1": {
                "level2": [
                    {"name": "item1"},
                    {"name": "item2"}
                ]
            }
        }
        keys = ["level1", "level2", "name"]
        result = extract_data(data, keys)
        self.assertEqual(result, ["item1", "item2"])

    def test_compare_data(self):
        data1 = ["item1", "item2", "item3"]
        data2 = ["item2", "item3", "item4"]
        result = compare_data(data1, data2)
        self.assertEqual(result, {
            "only_in_first": ["item1"],
            "only_in_second": ["item4"]
        })

    @patch('sys.stdout', new_callable=StringIO)
    def test_main_no_diff(self, mock_stdout):
        test_args = [
            'restdiff_inspector.py',
            '-u1', 'http://api1.com',
            '-u2', 'http://api2.com',
            '-k1', 'data,items',
            '-k2', 'data,items'
        ]
        with patch('sys.argv', test_args):
            with patch('restdiff_inspector.fetch_data', side_effect=[
                {"data": {"items": ["item1", "item2"]}},
                {"data": {"items": ["item1", "item2"]}}
            ]):
                main()

        self.assertIn("No differences found", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_main_with_diff(self, mock_stdout):
        test_args = [
            'restdiff_inspector.py',
            '-u1', 'http://api1.com',
            '-u2', 'http://api2.com',
            '-k1', 'data,items',
            '-k2', 'data,items'
        ]
        with patch('sys.argv', test_args):
            with patch('restdiff_inspector.fetch_data', side_effect=[
                {"data": {"items": ["item1", "item2"]}},
                {"data": {"items": ["item2", "item3"]}}
            ]):
                main()

        output = mock_stdout.getvalue()
        self.assertIn("Data only in http://api1.com:", output)
        self.assertIn("item1", output)
        self.assertIn("Data only in http://api2.com:", output)
        self.assertIn("item3", output)

if __name__ == '__main__':
    unittest.main()
