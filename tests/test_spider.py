"""
Comprehensive tests for enhanced spider functionality.

This module tests the enhanced LumaSpider with JSON extraction,
validation, and fallback mechanisms.
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch
from scrapy.http import HtmlResponse, Request
from scrapy.utils.project import get_project_settings

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from show_up.spiders.luma import LumaSpider
from show_up.items import EventItem
from show_up.extractors.json_extractor import JsonExtractor


class TestLumaSpider(unittest.TestCase):
    """Test the enhanced LumaSpider class."""

    def setUp(self):
        """Set up test fixtures."""
        self.spider = LumaSpider()
        self.spider.settings = get_project_settings()

    def test_spider_initialization(self):
        """Test spider initialization."""
        self.assertEqual(self.spider.name, "luma")
        self.assertEqual(self.spider.allowed_domains, ["lu.ma"])
        self.assertEqual(self.spider.start_urls, ["https://lu.ma/crypto"])
        self.assertIsInstance(self.spider.json_extractor, JsonExtractor)

    def test_spider_initialization_with_custom_patterns(self):
        """Test spider initialization with custom JSON patterns."""
        # Mock settings with custom patterns
        mock_settings = Mock()
        mock_settings.getlist.return_value = [
            r"customPattern:\s*({.*?})",
            r"specialData\s*=\s*({.*?});",
        ]

        spider = LumaSpider()
        spider.settings = mock_settings
        spider.__init__()

        # Check that custom patterns were passed to extractor
        mock_settings.getlist.assert_called_with("JSON_EXTRACTION_PATTERNS", [])

    def test_parse_with_event_links(self):
        """Test parse method when event links are found."""
        # Create mock response with event links
        html_content = """
        <html>
            <body>
                <div class="timeline">
                    <a class="event-link" href="/event1">Event 1</a>
                    <a class="event-link" href="/event2">Event 2</a>
                    <a class="event-link" href="/event3">Event 3</a>
                </div>
            </body>
        </html>
        """

        request = Request("https://lu.ma/crypto")
        response = HtmlResponse(
            url="https://lu.ma/crypto",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Mock the CSS selector to return event links
        with patch.object(response, "css") as mock_css:
            mock_css.return_value.getall.return_value = [
                "/event1",
                "/event2",
                "/event3",
            ]

            # Mock response.follow to track calls
            with patch.object(response, "follow") as mock_follow:
                mock_follow.return_value = Mock()

                # Call parse method
                list(self.spider.parse(response))

                # Check that follow was called for each event link
                self.assertEqual(mock_follow.call_count, 3)

                # Check that parse_event was passed as callback
                for call in mock_follow.call_args_list:
                    args, kwargs = call
                    self.assertEqual(args[1], self.spider.parse_event)

    def test_parse_with_no_event_links(self):
        """Test parse method when no event links are found."""
        html_content = """
        <html>
            <body>
                <div class="timeline">
                    <p>No events found</p>
                </div>
            </body>
        </html>
        """

        request = Request("https://lu.ma/crypto")
        response = HtmlResponse(
            url="https://lu.ma/crypto",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Mock the CSS selector to return no event links
        with patch.object(response, "css") as mock_css:
            mock_css.return_value.getall.return_value = []

            # Call parse method
            result = list(self.spider.parse(response))

            # Should return empty list
            self.assertEqual(len(result), 0)

    def test_parse_event_with_json_extraction_success(self):
        """Test parse_event when JSON extraction succeeds."""
        # Sample JSON data that would be extracted
        sample_event_data = {
            "title": "Test Event",
            "date": "2025-07-21T22:30:00.000Z",
            "location": "Test Location",
            "url": "https://lu.ma/test-event",
            "extraction_method": "json",
        }

        html_content = """
        <html>
            <body>
                <h1>Test Event</h1>
                <script>
                    var data = {"event": {"name": "Test Event", "start_at": "2025-07-21T22:30:00.000Z"}};
                </script>
            </body>
        </html>
        """

        request = Request("https://lu.ma/test-event")
        response = HtmlResponse(
            url="https://lu.ma/test-event",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Mock JSON extraction to return sample data
        with patch.object(self.spider, "_extract_with_json") as mock_json_extract:
            mock_json_extract.return_value = sample_event_data

            # Mock validation
            with patch("show_up.spiders.luma.validate_event_data") as mock_validate:
                mock_validate.return_value = sample_event_data

                # Call parse_event
                result = list(self.spider.parse_event(response))

                # Should yield one dict
                self.assertEqual(len(result), 1)
                item = result[0]
                self.assertIsInstance(item, dict)
                self.assertIn("title", item)
                self.assertIn("url", item)

                # Check item fields
                self.assertEqual(item["title"], "Test Event")
                self.assertEqual(item["date"], "2025-07-21T22:30:00.000Z")
                self.assertEqual(item["location"], "Test Location")
                self.assertEqual(item["url"], "https://lu.ma/test-event")
                self.assertEqual(item["extraction_method"], "json")

                # Check that JSON extraction was attempted
                mock_json_extract.assert_called_once()

    def test_parse_event_with_json_extraction_failure_html_fallback(self):
        """Test parse_event when JSON extraction fails but HTML fallback succeeds."""
        html_content = """
        <html>
            <body>
                <h1>Test Event</h1>
                <div class="event-date">2025-07-21</div>
                <div class="event-location">Test Location</div>
            </body>
        </html>
        """

        request = Request("https://lu.ma/test-event")
        response = HtmlResponse(
            url="https://lu.ma/test-event",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Mock settings to enable fallback
        self.spider.settings = Mock()
        self.spider.settings.getbool.return_value = True

        # Mock JSON extraction to fail
        with patch.object(self.spider, "_extract_with_json") as mock_json_extract:
            mock_json_extract.return_value = None

            # Mock HTML extraction to succeed
            with patch.object(
                self.spider, "_extract_with_html_selectors"
            ) as mock_html_extract:
                mock_html_extract.return_value = {
                    "title": "Test Event",
                    "date": "2025-07-21",
                    "location": "Test Location",
                    "extraction_method": "html_fallback",
                }

                # Call parse_event
                result = list(self.spider.parse_event(response))

                # Should yield one dict
                self.assertEqual(len(result), 1)
                item = result[0]
                self.assertIsInstance(item, dict)
                self.assertIn("title", item)
                self.assertIn("url", item)

                # Check that fallback was used
                self.assertEqual(item["extraction_method"], "html_fallback")
                mock_json_extract.assert_called_once()
                mock_html_extract.assert_called_once()

    def test_parse_event_with_all_extraction_methods_failing(self):
        """Test parse_event when all extraction methods fail."""
        html_content = """
        <html>
            <head><title>Test Event | Luma</title></head>
            <body>
                <div>No structured data</div>
            </body>
        </html>
        """

        request = Request("https://lu.ma/test-event")
        response = HtmlResponse(
            url="https://lu.ma/test-event",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Mock all extraction methods to fail
        with patch.object(self.spider, "_extract_with_json") as mock_json_extract:
            mock_json_extract.return_value = None

            with patch.object(
                self.spider, "_extract_with_html_selectors"
            ) as mock_html_extract:
                mock_html_extract.return_value = None

                # Call parse_event
                result = list(self.spider.parse_event(response))

                # Should still yield one dict with fallback data
                self.assertEqual(len(result), 1)
                item = result[0]
                self.assertIsInstance(item, dict)
                self.assertIn("title", item)
                self.assertIn("url", item)

                # Check that fallback title was extracted
                self.assertEqual(item["title"], "Test Event")
                self.assertEqual(item["extraction_method"], "fallback")

    def test_extract_with_json_success(self):
        """Test _extract_with_json method success case."""
        # Mock settings to enable JSON extraction
        self.spider.settings = Mock()
        self.spider.settings.getbool.return_value = True

        # Mock JSON extractor
        mock_extracted_data = {
            "title": "Test Event",
            "date": "2025-07-21T22:30:00.000Z",
            "extraction_method": "json",
        }

        with patch.object(self.spider.json_extractor, "extract") as mock_extract:
            mock_extract.return_value = mock_extracted_data

            # Create mock response
            response = Mock()
            response.text = "<html>Mock HTML</html>"
            response.url = "https://lu.ma/test-event"

            # Call method
            result = self.spider._extract_with_json(response)

            # Check result
            self.assertEqual(result, mock_extracted_data)
            mock_extract.assert_called_once_with(response.text, url=response.url)

    def test_extract_with_json_disabled(self):
        """Test _extract_with_json method when JSON extraction is disabled."""
        # Mock settings to disable JSON extraction
        self.spider.settings = Mock()
        self.spider.settings.getbool.return_value = False

        response = Mock()
        result = self.spider._extract_with_json(response)

        # Should return None
        self.assertIsNone(result)

    def test_extract_with_json_exception_handling(self):
        """Test _extract_with_json method exception handling."""
        # Mock settings to enable JSON extraction
        self.spider.settings = Mock()
        self.spider.settings.getbool.return_value = True

        # Mock JSON extractor to raise exception
        with patch.object(self.spider.json_extractor, "extract") as mock_extract:
            mock_extract.side_effect = Exception("JSON extraction error")

            response = Mock()
            response.text = "<html>Mock HTML</html>"
            response.url = "https://lu.ma/test-event"

            # Call method
            result = self.spider._extract_with_json(response)

            # Should return None
            self.assertIsNone(result)

    def test_extract_with_html_selectors_success(self):
        """Test _extract_with_html_selectors method success case."""
        html_content = """
        <html>
            <body>
                <h1>Test Event Title</h1>
                <time datetime="2025-07-21T22:30:00.000Z">July 21, 2025</time>
                <address>Test Location</address>
            </body>
        </html>
        """

        request = Request("https://lu.ma/test-event")
        response = HtmlResponse(
            url="https://lu.ma/test-event",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Call method
        result = self.spider._extract_with_html_selectors(response)
        assert result

        # Check result
        self.assertIsNotNone(result)
        self.assertEqual(result["title"], "Test Event Title")
        self.assertEqual(result["date"], "July 21, 2025")
        self.assertEqual(result["location"], "Test Location")
        self.assertEqual(result["extraction_method"], "html_fallback")

    def test_extract_with_html_selectors_partial_data(self):
        """Test _extract_with_html_selectors method with partial data."""
        html_content = """
        <html>
            <body>
                <h1>Test Event Title</h1>
                <!-- No date or location -->
            </body>
        </html>
        """

        request = Request("https://lu.ma/test-event")
        response = HtmlResponse(
            url="https://lu.ma/test-event",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Call method
        result = self.spider._extract_with_html_selectors(response)
        assert result

        # Check result
        self.assertEqual(result["title"], "Test Event Title")
        self.assertNotIn("date", result)
        self.assertNotIn("location", result)

    def test_extract_with_html_selectors_no_title(self):
        """Test _extract_with_html_selectors method when no title is found."""
        html_content = """
        <html>
            <body>
                <div>No title element</div>
            </body>
        </html>
        """

        request = Request("https://lu.ma/test-event")
        response = HtmlResponse(
            url="https://lu.ma/test-event",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Call method
        result = self.spider._extract_with_html_selectors(response)

        # Should return None because no title was found
        self.assertIsNone(result)

    def test_extract_title_fallback_from_page_title(self):
        """Test _extract_title_fallback method extracting from page title."""
        html_content = """
        <html>
            <head><title>Test Event | Luma</title></head>
            <body></body>
        </html>
        """

        request = Request("https://lu.ma/test-event")
        response = HtmlResponse(
            url="https://lu.ma/test-event",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Call method
        result = self.spider._extract_title_fallback(response)

        # Should extract and clean title
        self.assertEqual(result, "Test Event")

    def test_extract_title_fallback_from_h1(self):
        """Test _extract_title_fallback method extracting from h1 tag."""
        html_content = """
        <html>
            <body>
                <h1>Test Event Title</h1>
            </body>
        </html>
        """

        request = Request("https://lu.ma/test-event")
        response = HtmlResponse(
            url="https://lu.ma/test-event",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Call method
        result = self.spider._extract_title_fallback(response)

        # Should extract h1 title
        self.assertEqual(result, "Test Event Title")

    def test_extract_title_fallback_from_url(self):
        """Test _extract_title_fallback method extracting from URL."""
        html_content = """
        <html>
            <body>
                <div>No title elements</div>
            </body>
        </html>
        """

        request = Request("https://lu.ma/test-event-name")
        response = HtmlResponse(
            url="https://lu.ma/test-event-name",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Call method
        result = self.spider._extract_title_fallback(response)

        # Should extract and format from URL
        self.assertEqual(result, "Test Event Name")

    def test_extract_title_fallback_unknown_event(self):
        """Test _extract_title_fallback method with no extractable title."""
        html_content = "<html><body></body></html>"

        request = Request("https://lu.ma/")
        response = HtmlResponse(
            url="https://lu.ma/",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Call method
        result = self.spider._extract_title_fallback(response)

        # Should return default
        self.assertEqual(result, "Unknown Event")

    def test_populate_item_with_complete_data(self):
        """Test _populate_item method with complete data."""
        item = EventItem()
        data = {
            "title": "Test Event",
            "date": "2025-07-21T22:30:00.000Z",
            "location": "Test Location",
            "coordinates": {"latitude": -34.6037, "longitude": -58.3816},
            "organizer": "Test Organizer",
            "extraction_method": "json",
        }

        self.spider._populate_item(item, data)

        # Check that all fields were populated
        self.assertEqual(item["title"], "Test Event")
        self.assertEqual(item["date"], "2025-07-21T22:30:00.000Z")
        self.assertEqual(item["location"], "Test Location")
        self.assertEqual(
            item["coordinates"], {"latitude": -34.6037, "longitude": -58.3816}
        )
        self.assertEqual(item["organizer"], "Test Organizer")
        self.assertEqual(item["extraction_method"], "json")

    def test_populate_item_with_partial_data(self):
        """Test _populate_item method with partial data."""
        item = EventItem()
        data = {"title": "Test Event", "extraction_method": "html_fallback"}

        self.spider._populate_item(item, data)

        # Check that only provided fields were populated
        self.assertEqual(item["title"], "Test Event")
        self.assertEqual(item["extraction_method"], "html_fallback")
        self.assertNotIn("date", dict(item))
        self.assertNotIn("location", dict(item))

    # HTML content processing tests removed - JSON output only
    # The spider no longer processes HTML content, only extracts JSON data

    def test_validation_success(self):
        """Test successful validation in parse_event."""
        html_content = "<html><body><h1>Test</h1></body></html>"

        request = Request("https://lu.ma/test-event")
        response = HtmlResponse(
            url="https://lu.ma/test-event",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Mock extraction to return valid data
        with patch.object(self.spider, "_extract_with_json") as mock_json_extract:
            mock_json_extract.return_value = {
                "title": "Test Event",
                "url": "https://lu.ma/test-event",
                "extraction_method": "json",
            }

            # Mock validation to return enhanced data
            with patch("show_up.spiders.luma.validate_event_data") as mock_validate:
                mock_validate.return_value = {
                    "title": "Test Event",
                    "url": "https://lu.ma/test-event",
                    "extraction_method": "json",
                    "validated": True,
                }

                # Call parse_event
                result = list(self.spider.parse_event(response))

                # Check that validation was called and data was updated
                mock_validate.assert_called_once()
                item = result[0]
                self.assertEqual(item["title"], "Test Event")
                self.assertEqual(item["url"], "https://lu.ma/test-event")

    def test_validation_failure(self):
        """Test validation failure handling in parse_event."""
        html_content = "<html><body><h1>Test</h1></body></html>"

        request = Request("https://lu.ma/test-event")
        response = HtmlResponse(
            url="https://lu.ma/test-event",
            body=html_content.encode("utf-8"),
            encoding="utf-8",
            request=request,
        )

        # Mock extraction to return data
        with patch.object(self.spider, "_extract_with_json") as mock_json_extract:
            mock_json_extract.return_value = {
                "title": "Test Event",
                "extraction_method": "json",
            }

            # Mock validation to raise exception
            with patch("show_up.spiders.luma.validate_event_data") as mock_validate:
                mock_validate.side_effect = Exception("Validation error")

                # Call parse_event
                result = list(self.spider.parse_event(response))

                # Should continue with unvalidated data
                self.assertEqual(len(result), 1)
                item = result[0]
                self.assertEqual(item["title"], "Test Event")


if __name__ == "__main__":
    unittest.main()
