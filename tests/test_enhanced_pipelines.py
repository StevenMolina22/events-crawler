"""
Comprehensive tests for enhanced pipeline functionality.

This module tests the enhanced JSON pipeline with metadata, statistics,
and validation capabilities.
"""

import unittest
import tempfile
import os
import shutil
import json
from unittest.mock import Mock, patch
from datetime import datetime

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from show_up.pipelines import EnhancedJsonPipeline
from show_up.items import EventItem


class TestEnhancedJsonPipeline(unittest.TestCase):
    """Test the EnhancedJsonPipeline class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory and file for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_enhanced_events.json")

        # Create pipeline instance
        self.pipeline = EnhancedJsonPipeline(output_file=self.test_file)

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
            "JSON_OUTPUT_FILE": "custom_enhanced_output.json",
            "JSON_INDENT": 4,
            "JSON_ENSURE_ASCII": True,
            "ENHANCED_JSON_VALIDATION": True,
            "ENHANCED_JSON_INCLUDE_METADATA": True,
            "ENHANCED_JSON_EXTRACTION_STATS": True,
        }

        # Mock the settings methods
        mock_crawler.settings.get = lambda key, default: mock_settings.get(key, default)
        mock_crawler.settings.getint = lambda key, default: mock_settings.get(
            key, default
        )
        mock_crawler.settings.getbool = lambda key, default: mock_settings.get(
            key, default
        )

        pipeline = EnhancedJsonPipeline.from_crawler(mock_crawler)

        self.assertEqual(pipeline.output_file, "custom_enhanced_output.json")
        self.assertEqual(pipeline.indent, 4)
        self.assertEqual(pipeline.ensure_ascii, True)
        self.assertIsInstance(pipeline.settings, dict)

    def test_from_crawler_with_default_settings(self):
        """Test that pipeline uses default settings when not specified."""
        mock_crawler = Mock()
        mock_crawler.settings.get = lambda key, default: default
        mock_crawler.settings.getint = lambda key, default: default
        mock_crawler.settings.getbool = lambda key, default: default

        pipeline = EnhancedJsonPipeline.from_crawler(mock_crawler)

        self.assertEqual(pipeline.output_file, "crypto_events.json")
        self.assertEqual(pipeline.indent, 2)
        self.assertEqual(pipeline.ensure_ascii, False)

    def test_open_spider_initializes_metadata(self):
        """Test that open_spider initializes metadata correctly."""
        self.pipeline.open_spider(self.spider)

        # Check metadata structure
        self.assertIn("spider_name", self.pipeline.metadata)
        self.assertIn("start_time", self.pipeline.metadata)
        self.assertIn("source", self.pipeline.metadata)
        self.assertIn("extraction_config", self.pipeline.metadata)

        # Check metadata values
        self.assertEqual(self.pipeline.metadata["spider_name"], "test_spider")
        self.assertEqual(self.pipeline.metadata["source"], "https://example.com/test")

        # Check extraction config
        config = self.pipeline.metadata["extraction_config"]
        self.assertIsInstance(config, dict)
        self.assertIn("json_extraction_enabled", config)
        self.assertIn("validation_enabled", config)
        self.assertIn("include_metadata", config)
        self.assertIn("extraction_stats", config)

    def test_process_item_with_complete_event_data(self):
        """Test processing item with complete event data."""
        item = EventItem()
        item["title"] = "Test Event"
        item["date"] = "2025-07-21T22:30:00.000Z"
        item["end_date"] = "2025-07-22T01:00:00.000Z"
        item["timezone"] = "America/Buenos_Aires"
        item["location"] = "Test Location"
        item["full_address"] = "Test Address 123, Buenos Aires, Argentina"
        item["city"] = "Buenos Aires"
        item["country"] = "Argentina"
        item["coordinates"] = {"latitude": -34.6037, "longitude": -58.3816}
        item["place_id"] = "ChIJ_test123"
        item["event_type"] = "independent"
        item["visibility"] = "public"
        item["api_id"] = "evt-test123"
        item["cover_url"] = "https://example.com/cover.jpg"
        item["organizer"] = "Test Organizer"
        item["guest_count"] = 42
        item["description"] = "Test event description"
        item["url"] = "https://lu.ma/test-event"
        item["extraction_method"] = "json"
        item["html_content"] = "<html><body>Test content</body></html>"
        item["raw_html"] = "<html><body>Raw test content</body></html>"

        self.pipeline.open_spider(self.spider)
        result = self.pipeline.process_item(item, self.spider)

        # Check that item was processed
        self.assertEqual(len(self.pipeline.items), 1)
        processed_item = self.pipeline.items[0]

        # Check that HTML fields were removed
        self.assertNotIn("html_content", processed_item)
        self.assertNotIn("raw_html", processed_item)

        # Check that other fields are preserved
        self.assertEqual(processed_item["title"], "Test Event")
        self.assertEqual(processed_item["date"], "2025-07-21T22:30:00.000Z")
        self.assertEqual(processed_item["location"], "Test Location")
        self.assertEqual(processed_item["extraction_method"], "json")

        # Check that original item is returned
        self.assertEqual(result, item)

        # Check extraction statistics
        self.assertEqual(self.pipeline.extraction_stats["total_processed"], 1)
        self.assertEqual(self.pipeline.extraction_stats["json_extraction"], 1)

    def test_process_item_with_minimal_data(self):
        """Test processing item with minimal data."""
        item = EventItem()
        item["title"] = "Minimal Event"
        item["url"] = "https://lu.ma/minimal-event"
        item["extraction_method"] = "fallback"

        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)

        self.assertEqual(len(self.pipeline.items), 1)
        processed_item = self.pipeline.items[0]

        # Check that required fields are present
        self.assertEqual(processed_item["title"], "Minimal Event")
        self.assertEqual(processed_item["url"], "https://lu.ma/minimal-event")

        # Check that missing fields are filled with None
        self.assertIsNone(processed_item["date"])
        self.assertIsNone(processed_item["location"])
        self.assertIsNone(processed_item["coordinates"])

        # Check extraction statistics
        self.assertEqual(self.pipeline.extraction_stats["fallback_extraction"], 1)

    def test_process_item_with_missing_required_fields(self):
        """Test processing item with missing required fields."""
        item = EventItem()
        item["date"] = "2025-07-21T22:30:00.000Z"
        item["location"] = "Test Location"
        # Missing title and url

        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)

        processed_item = self.pipeline.items[0]

        # Check that default values are provided
        self.assertIn("Untitled Event", processed_item["title"])
        self.assertEqual(processed_item["url"], "unknown_url")

    def test_process_item_with_validation_enabled(self):
        """Test processing item with validation enabled."""
        # Mock settings to enable validation
        # Mock settings to enable validation
        mock_settings = {
            "ENHANCED_JSON_VALIDATION": True,
            "ENHANCED_JSON_INCLUDE_METADATA": True,
        }
        self.pipeline.settings = mock_settings

        item = EventItem()
        item["title"] = "Test Event"
        item["url"] = "/test-event"  # Partial URL that needs validation
        item["date"] = "2025-07-21T22:30:00.000Z"
        item["extraction_method"] = "json"

        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)

        processed_item = self.pipeline.items[0]

        # Check that URL was normalized
        self.assertEqual(processed_item["url"], "https://lu.ma/test-event")

        # Check that metadata was added
        self.assertIn("_metadata", processed_item)
        metadata = processed_item["_metadata"]
        self.assertEqual(metadata["extraction_method"], "json")
        self.assertIn("completeness_score", metadata)
        self.assertIn("processed_at", metadata)

    def test_process_item_with_validation_disabled(self):
        """Test processing item with validation disabled."""
        # Mock settings to disable validation
        # Mock settings to disable validation
        mock_settings = {
            "ENHANCED_JSON_VALIDATION": False,
            "ENHANCED_JSON_INCLUDE_METADATA": False,
        }
        self.pipeline.settings = mock_settings

        item = EventItem()
        item["title"] = "Test Event"
        item["url"] = "/test-event"
        item["extraction_method"] = "json"

        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)

        processed_item = self.pipeline.items[0]

        # Check that URL was NOT normalized
        self.assertEqual(processed_item["url"], "/test-event")

        # Check that metadata was NOT added
        self.assertNotIn("_metadata", processed_item)

    def test_process_item_with_non_serializable_values(self):
        """Test processing item with non-serializable values."""

        class NonSerializable:
            def __str__(self):
                return "Non-serializable object"

        item = EventItem()
        item["title"] = "Test Event"
        item["url"] = "https://lu.ma/test"
        item["description"] = NonSerializable()  # Non-serializable value
        item["extraction_method"] = "json"

        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)

        processed_item = self.pipeline.items[0]

        # Check that non-serializable value was converted to string
        self.assertEqual(processed_item["description"], "Non-serializable object")

    def test_process_item_extraction_statistics(self):
        """Test extraction statistics tracking."""
        items = [
            {"title": "Event 1", "url": "https://lu.ma/1", "extraction_method": "json"},
            {
                "title": "Event 2",
                "url": "https://lu.ma/2",
                "extraction_method": "html_fallback",
            },
            {
                "title": "Event 3",
                "url": "https://lu.ma/3",
                "extraction_method": "fallback",
            },
            {"title": "Event 4", "url": "https://lu.ma/4", "extraction_method": "json"},
        ]

        self.pipeline.open_spider(self.spider)

        for item_data in items:
            item = EventItem()
            for key, value in item_data.items():
                item[key] = value
            self.pipeline.process_item(item, self.spider)

        # Check extraction statistics
        stats = self.pipeline.extraction_stats
        self.assertEqual(stats["total_processed"], 4)
        self.assertEqual(stats["json_extraction"], 2)
        self.assertEqual(stats["html_extraction"], 1)
        self.assertEqual(stats["fallback_extraction"], 1)

    def test_close_spider_writes_structured_json(self):
        """Test that close_spider writes properly structured JSON."""
        # Mock settings for extraction stats
        # Mock settings for extraction stats
        mock_settings = {"ENHANCED_JSON_EXTRACTION_STATS": True}
        self.pipeline.settings = mock_settings

        # Add some test items
        items = [
            {"title": "Event 1", "url": "https://lu.ma/1", "extraction_method": "json"},
            {"title": "Event 2", "url": "https://lu.ma/2", "extraction_method": "json"},
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

        # Check top-level structure
        self.assertIn("metadata", data)
        self.assertIn("events", data)
        self.assertIn("end_time", data)
        self.assertIn("event_count", data)

        # Check metadata
        metadata = data["metadata"]
        self.assertEqual(metadata["spider_name"], "test_spider")
        self.assertIn("start_time", metadata)
        self.assertIn("extraction_statistics", metadata)

        # Check extraction statistics
        stats = metadata["extraction_statistics"]
        self.assertEqual(stats["total_processed"], 2)
        self.assertEqual(stats["json_extraction"], 2)
        self.assertIn("success_rates", stats)

        # Check success rates
        success_rates = stats["success_rates"]
        self.assertEqual(success_rates["json_extraction_rate"], 1.0)
        self.assertEqual(success_rates["validation_success_rate"], 1.0)

        # Check events
        events = data["events"]
        self.assertEqual(len(events), 2)
        self.assertEqual(data["event_count"], 2)

    def test_close_spider_creates_directory_if_needed(self):
        """Test that close_spider creates output directory if it doesn't exist."""
        nested_dir = os.path.join(self.test_dir, "nested", "deep", "directory")
        nested_file = os.path.join(nested_dir, "test_events.json")

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

    def test_close_spider_handles_permission_errors(self):
        """Test that close_spider handles permission errors gracefully."""
        # Mock open to raise PermissionError
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            item = EventItem()
            item["title"] = "Test Event"
            item["url"] = "https://lu.ma/test"

            self.pipeline.open_spider(self.spider)
            self.pipeline.process_item(item, self.spider)

            # This should not raise an exception
            self.pipeline.close_spider(self.spider)

            # Check that error was logged
            self.spider.logger.error.assert_called()

    def test_close_spider_without_extraction_stats(self):
        """Test close_spider when extraction stats are disabled."""
        # Mock settings to disable extraction stats
        # Mock settings to disable extraction stats
        mock_settings = {"ENHANCED_JSON_EXTRACTION_STATS": False}
        self.pipeline.settings = mock_settings

        item = EventItem()
        item["title"] = "Test Event"
        item["url"] = "https://lu.ma/test"

        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)
        self.pipeline.close_spider(self.spider)

        # Read JSON file
        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check that extraction statistics are not included
        self.assertNotIn("extraction_statistics", data["metadata"])

    def test_extraction_stats_high_quality_tracking(self):
        """Test that high quality events are tracked correctly."""
        # Mock settings to enable validation
        # Mock settings to enable validation
        mock_settings = {
            "ENHANCED_JSON_VALIDATION": True,
            "ENHANCED_JSON_INCLUDE_METADATA": True,
        }
        self.pipeline.settings = mock_settings

        # High quality item (complete data)
        high_quality_item = EventItem()
        high_quality_item["title"] = "High Quality Event"
        high_quality_item["url"] = "https://lu.ma/high-quality"
        high_quality_item["date"] = "2025-07-21T22:30:00.000Z"
        high_quality_item["location"] = "Buenos Aires, Argentina"
        high_quality_item["full_address"] = "Test Address 123, Buenos Aires, Argentina"
        high_quality_item["city"] = "Buenos Aires"
        high_quality_item["country"] = "Argentina"
        high_quality_item["coordinates"] = {"latitude": -34.6037, "longitude": -58.3816}
        high_quality_item["organizer"] = "Test Organizer"
        high_quality_item["extraction_method"] = "json"

        # Low quality item (minimal data)
        low_quality_item = EventItem()
        low_quality_item["title"] = "Low Quality Event"
        low_quality_item["url"] = "https://lu.ma/low-quality"
        low_quality_item["extraction_method"] = "fallback"

        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(high_quality_item, self.spider)
        self.pipeline.process_item(low_quality_item, self.spider)

        # Check that high quality event was tracked
        self.assertEqual(self.pipeline.extraction_stats["high_quality_events"], 1)
        self.assertEqual(self.pipeline.extraction_stats["total_processed"], 2)

    def test_validation_error_handling(self):
        """Test handling of validation errors."""
        # Mock settings to enable validation
        # Mock settings to enable validation
        mock_settings = {"ENHANCED_JSON_VALIDATION": True}
        self.pipeline.settings = mock_settings

        # Create item that will cause validation error
        item = EventItem()
        item["title"] = ""  # Empty title should cause validation error
        item["url"] = "https://lu.ma/test"
        item["extraction_method"] = "json"

        self.pipeline.open_spider(self.spider)

        # Mock validate_event_data to raise an exception
        with patch(
            "show_up.pipelines.validate_event_data",
            side_effect=Exception("Validation error"),
        ):
            self.pipeline.process_item(item, self.spider)

        # Check that validation error was tracked
        self.assertEqual(self.pipeline.extraction_stats["validation_errors"], 1)

    def test_json_indent_and_ascii_settings(self):
        """Test that JSON formatting settings are applied correctly."""
        # Create pipeline with specific formatting settings
        pipeline = EnhancedJsonPipeline(
            output_file=self.test_file, indent=4, ensure_ascii=True
        )

        item = EventItem()
        item["title"] = "Test Event with émojis 🚀"
        item["url"] = "https://lu.ma/test"

        pipeline.open_spider(self.spider)
        pipeline.process_item(item, self.spider)
        pipeline.close_spider(self.spider)

        # Read the raw file content to check formatting
        with open(self.test_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that 4-space indentation is used
        self.assertIn('    "metadata":', content)
        self.assertIn('    "events":', content)

        # Check that non-ASCII characters are escaped (ensure_ascii=True)
        self.assertIn("\\u", content)  # Should contain unicode escapes


if __name__ == "__main__":
    unittest.main()
