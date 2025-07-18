import unittest
import tempfile
import os
import shutil
import sys
import json
from unittest.mock import Mock, patch


# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from show_up.pipelines import RawHtmlFilePipeline, EnhancedJsonPipeline
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

class TestEnhancedJsonPipeline(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory and file for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_events.json")
        self.pipeline = EnhancedJsonPipeline(output_file=self.test_file)

        # Create a mock spider
        self.spider = Mock()
        self.spider.name = "test_spider"
        self.spider.start_urls = ["https://example.com"]

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_from_crawler(self):
        # Test that the pipeline reads settings from crawler
        mock_crawler = Mock()
        mock_settings = {
            'JSON_OUTPUT_FILE': 'custom_output.json',
            'JSON_INDENT': 4,
            'JSON_ENSURE_ASCII': True
        }
        mock_crawler.settings.get = lambda key, default: mock_settings.get(key, default)
        mock_crawler.settings.getint = lambda key, default: mock_settings.get(key, default)
        mock_crawler.settings.getbool = lambda key, default: mock_settings.get(key, default)

        pipeline = EnhancedJsonPipeline.from_crawler(mock_crawler)

        self.assertEqual(pipeline.output_file, 'custom_output.json')
        self.assertEqual(pipeline.indent, 4)
        self.assertEqual(pipeline.ensure_ascii, True)

    def test_open_spider_initializes_metadata(self):
        # Test that open_spider initializes metadata correctly
        self.pipeline.open_spider(self.spider)

        self.assertIn('spider_name', self.pipeline.metadata)
        self.assertEqual(self.pipeline.metadata['spider_name'], 'test_spider')
        self.assertIn('start_time', self.pipeline.metadata)
        self.assertIn('source', self.pipeline.metadata)
        self.assertEqual(self.pipeline.metadata['source'], 'https://example.com')

    def test_process_item_adds_to_items_list(self):
        # Test that process_item adds items to the items list
        item = EventItem()
        item['title'] = "Test Event"
        item['date'] = "2025-08-01"
        item['location'] = "Test Location"
        item['url'] = "https://example.com/event"
        item['html_content'] = "<html><body>Test content</body></html>"
        item['raw_html'] = "<html><body>Raw test content</body></html>"

        self.pipeline.open_spider(self.spider)
        result = self.pipeline.process_item(item, self.spider)

        # Check that HTML fields are removed
        self.assertEqual(len(self.pipeline.items), 1)
        self.assertNotIn('html_content', self.pipeline.items[0])
        self.assertNotIn('raw_html', self.pipeline.items[0])

        # Check that other fields are preserved
        self.assertEqual(self.pipeline.items[0]['title'], "Test Event")
        self.assertEqual(self.pipeline.items[0]['date'], "2025-08-01T00:00:00")
        self.assertEqual(self.pipeline.items[0]['location'], "Test Location")
        self.assertEqual(self.pipeline.items[0]['url'], "https://example.com/event")

        # Check that the original item is returned unchanged
        self.assertEqual(result, item)

    def test_process_item_handles_missing_fields(self):
        # Test that process_item handles missing fields
        item = EventItem()
        item['url'] = "https://example.com/event"

        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)

        # Check that missing fields are added with default values
        self.assertEqual(len(self.pipeline.items), 1)
        self.assertIn('title', self.pipeline.items[0])
        self.assertIn('date', self.pipeline.items[0])
        self.assertIn('location', self.pipeline.items[0])
        self.assertEqual(self.pipeline.items[0]['url'], "https://example.com/event")

    def test_process_item_handles_non_serializable_values(self):
        # Test that process_item handles non-serializable values
        class NonSerializable:
            def __str__(self):
                return "Non-serializable object"

        item = EventItem()
        item['title'] = "Test Event"
        item['date'] = NonSerializable()
        item['url'] = "https://example.com/event"

        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)

        # Check that non-serializable values are converted to strings
        self.assertEqual(len(self.pipeline.items), 1)
        self.assertEqual(self.pipeline.items[0]['title'], "Test Event")
        self.assertEqual(self.pipeline.items[0]['date'], "Non-serializable object")
        self.assertEqual(self.pipeline.items[0]['url'], "https://example.com/event")

    def test_close_spider_writes_json_file(self):
        # Test that close_spider writes a properly formatted JSON file
        item1 = EventItem()
        item1['title'] = "Test Event 1"
        item1['date'] = "2025-08-01"
        item1['url'] = "https://example.com/event1"

        item2 = EventItem()
        item2['title'] = "Test Event 2"
        item2['date'] = "2025-08-02"
        item2['url'] = "https://example.com/event2"

        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item1, self.spider)
        self.pipeline.process_item(item2, self.spider)
        self.pipeline.close_spider(self.spider)

        # Check that the JSON file was created
        self.assertTrue(os.path.exists(self.test_file))

        # Check that the JSON file contains the expected structure
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertIn('metadata', data)
        self.assertIn('events', data)
        self.assertIn('end_time', data)
        self.assertIn('event_count', data)

        self.assertEqual(data['metadata']['spider_name'], 'test_spider')
        self.assertEqual(len(data['events']), 2)
        self.assertEqual(data['event_count'], 2)

        self.assertEqual(data['events'][0]['title'], "Test Event 1")
        self.assertEqual(data['events'][1]['title'], "Test Event 2")

    def test_close_spider_creates_directory_if_needed(self):
        # Test that close_spider creates the output directory if it doesn't exist
        nested_dir = os.path.join(self.test_dir, "nested", "dir")
        nested_file = os.path.join(nested_dir, "test_events.json")

        self.pipeline.output_file = nested_file

        item = EventItem()
        item['title'] = "Test Event"
        item['url'] = "https://example.com/event"

        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)
        self.pipeline.close_spider(self.spider)

        # Check that the directory and file were created
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.exists(nested_file))

    def test_close_spider_handles_file_write_errors(self):
        # Test that close_spider handles file write errors gracefully
        with patch('builtins.open') as mock_open:
            mock_open.side_effect = PermissionError("Permission denied")

            item = EventItem()
            item['title'] = "Test Event"
            item['url'] = "https://example.com/event"

            self.pipeline.open_spider(self.spider)
            self.pipeline.process_item(item, self.spider)

            # This should not raise an exception
            self.pipeline.close_spider(self.spider)
