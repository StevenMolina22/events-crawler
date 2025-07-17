import unittest
import tempfile
import os
import shutil
import sys
from unittest.mock import Mock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from show_up.pipelines import RawHtmlFilePipeline
from show_up.items import EventItem


class TestRawHtmlFilePipeline(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.pipeline = RawHtmlFilePipeline()
        self.pipeline.output_dir = self.test_dir

        # Create a mock spider
        self.spider = Mock()
        self.spider.name = "test_spider"

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_open_spider_creates_directory(self):
        # Test that the pipeline creates the output directory
        self.pipeline.open_spider(self.spider)
        self.assertTrue(os.path.exists(self.test_dir))

    def test_process_item_saves_raw_html(self):
        # Arrange
        item = EventItem()
        item['title'] = "Test Event"
        item['raw_html'] = "<html><head><title>Test</title></head><body><h1>Test Event</h1></body></html>"

        self.pipeline.open_spider(self.spider)

        # Act
        result = self.pipeline.process_item(item, self.spider)

        # Assert
        expected_filename = "Test_Event_raw.html"
        expected_filepath = os.path.join(self.test_dir, expected_filename)

        self.assertTrue(os.path.exists(expected_filepath))

        with open(expected_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertEqual(content, item['raw_html'])
        self.assertEqual(result, item)

    def test_process_item_sanitizes_filename(self):
        # Test that special characters in title are sanitized
        item = EventItem()
        item['title'] = "Test Event! @#$%^&*()+=[]{}|;:',.<>?/~`"
        item['raw_html'] = "<html><body>Test content</body></html>"

        self.pipeline.open_spider(self.spider)
        result = self.pipeline.process_item(item, self.spider)

        # Should sanitize to only alphanumeric, spaces, and hyphens
        expected_filename = "Test_Event_raw.html"
        expected_filepath = os.path.join(self.test_dir, expected_filename)

        self.assertTrue(os.path.exists(expected_filepath))

    def test_process_item_without_title_or_raw_html(self):
        # Test that items without title or raw_html are handled gracefully
        item = EventItem()
        item['url'] = "https://example.com"

        self.pipeline.open_spider(self.spider)
        result = self.pipeline.process_item(item, self.spider)

        # Should return the item unchanged and not create any files
        self.assertEqual(result, item)
        self.assertEqual(len(os.listdir(self.test_dir)), 0)

    def test_process_item_with_empty_title(self):
        # Test handling of empty title
        item = EventItem()
        item['title'] = ""
        item['raw_html'] = "<html><body>Content</body></html>"

        self.pipeline.open_spider(self.spider)
        result = self.pipeline.process_item(item, self.spider)

        # Should create a file with sanitized empty name
        expected_filename = "_raw.html"
        expected_filepath = os.path.join(self.test_dir, expected_filename)

        self.assertTrue(os.path.exists(expected_filepath))


if __name__ == '__main__':
    unittest.main()
