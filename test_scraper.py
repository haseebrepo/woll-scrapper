import unittest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
from scraper import WollplatzScraper

class TestWollplatzScraper(unittest.TestCase):
    def setUp(self):
        self.wollplatz_scraper = WollplatzScraper(
            excel_file_path='test_data.xlsx',
            json_file_path='test_data.json',
            log_file_path='test_log.log'
        )

    def test_extract_price(self):
        # Mock the BeautifulSoup object
        soup = MagicMock()
        soup.find.return_value = MagicMock(get_text=lambda strip: '7,38')
        price = self.wollplatz_scraper.extract_price(soup)
        self.assertEqual(price, '7,38')

    def test_extract_price_missing_value(self):
        # Mock the BeautifulSoup object
        soup = MagicMock()
        soup.find.return_value = MagicMock(get_text=lambda strip: '')
        price = self.wollplatz_scraper.extract_price(soup)
        self.assertNotEqual(price, '7,38')

    def test_extract_availability(self):
        # Mock the BeautifulSoup object
        soup = MagicMock()
        soup.find.return_value = MagicMock()
        availability = self.wollplatz_scraper.extract_availability(soup)
        self.assertIsNotNone(availability)

    def test_extract_specs(self):
        # Mock the BeautifulSoup object
        soup = MagicMock()
        soup.find.return_value = MagicMock()
        specs = self.wollplatz_scraper.extract_specs(soup)
        self.assertEqual(specs, {})


if __name__ == '__main__':
    unittest.main()
