import unittest
import tempfile
import os
import shutil
import json
from unittest.mock import Mock
from show_up.pipelines import JsonPipeline
from show_up.items import EventItem


class TestJsonPipeline(unittest.TestCase):
    """Test the simplified JsonPipeline class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory and file for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_events.json")

        # Create pipeline instance
        self.pipeline = JsonPipeline(output_file=self.test_file)

        # Create mock spider
        self.spider = Mock()
        self.spider.name = "test_spider"
        self.spider.start_urls = ["https://example.com/test"]
        self.spider.logger = Mock()

    def tearDown(self):
        """Clean up the temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_from_crawler_with_custom_settings(self):
        """Test that pipeline reads custom settings from crawler."""
        mock_crawler = Mock()
        mock_settings = {
            "JSON_OUTPUT_FILE": "custom_output.json",
        }

        # Mock the settings methods
        mock_crawler.settings.get = lambda key, default: mock_settings.get(key, default)

        pipeline = JsonPipeline.from_crawler(mock_crawler)

        self.assertEqual(pipeline.output_file, "custom_output.json")

    def test_from_crawler_with_default_settings(self):
        """Test that pipeline uses default settings when not specified."""
        mock_crawler = Mock()
        mock_crawler.settings.get = lambda key, default: default

        pipeline = JsonPipeline.from_crawler(mock_crawler)

        self.assertEqual(pipeline.output_file, "output/events.json")

    def test_process_item_stores_data(self):
        """Test that process_item stores event data."""
        item = EventItem()
        item["title"] = "Test Event"
        item["url"] = "https://lu.ma/test-event"
        item["description"] = "Test event description"

        result = self.pipeline.process_item(item, self.spider)

        # Check that item was stored
        self.assertEqual(len(self.pipeline.items), 1)
        stored_item = self.pipeline.items[0]
        self.assertEqual(stored_item["title"], "Test Event")
        self.assertEqual(stored_item["url"], "https://lu.ma/test-event")
        self.assertEqual(stored_item["description"], "Test event description")

        # Check that original item is returned
        self.assertEqual(result, item)

    def test_close_spider_writes_json(self):
        """Test that close_spider writes JSON file correctly."""
        # Add test items
        items = [
            {"title": "Event 1", "url": "https://lu.ma/1"},
            {"title": "Event 2", "url": "https://lu.ma/2"},
        ]

        self.pipeline.open_spider(self.spider)

        for item_data in items:
            item = EventItem()
            for key, value in item_data.items():
                item[key] = value
            self.pipeline.process_item(item, self.spider)

        self.pipeline.close_spider(self.spider)

        # Check that JSON file was created
        self.assertTrue(os.path.exists(self.test_file))

        # Read and verify JSON structure
        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check structure
        self.assertIn("events", data)
        self.assertIn("count", data)
        self.assertIn("scraped_at", data)

        # Check events
        events = data["events"]
        self.assertEqual(len(events), 2)
        self.assertEqual(data["count"], 2)
        self.assertEqual(events[0]["title"], "Event 1")
        self.assertEqual(events[1]["title"], "Event 2")

    def test_creates_output_directory(self):
        """Test that output directory is created if it doesn't exist."""
        nested_dir = os.path.join(self.test_dir, "nested", "directory")
        nested_file = os.path.join(nested_dir, "events.json")

        self.pipeline.output_file = nested_file

        item = EventItem()
        item["title"] = "Test Event"
        item["url"] = "https://lu.ma/test"

        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)
        self.pipeline.close_spider(self.spider)

        # Check that directory and file were created
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.exists(nested_file))


if __name__ == "__main__":
    unittest.main()
