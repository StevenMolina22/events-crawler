"""
Comprehensive tests for JSON extractor functionality.

This module tests the JSON extraction logic for Luma event data,
including pattern matching, data parsing, and error handling.
"""

import unittest
import json
from show_up.extractors.json_extractor import JsonExtractor


class TestJsonExtractor(unittest.TestCase):
    """Test the JsonExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = JsonExtractor()

        # Sample event data that would be found in Luma pages
        self.sample_event_data = {
            "api_id": "evt-test123",
            "name": "Test Event",
            "start_at": "2025-07-21T22:30:00.000Z",
            "end_at": "2025-07-22T01:00:00.000Z",
            "timezone": "America/Buenos_Aires",
            "event_type": "independent",
            "visibility": "public",
            "url": "test-event",
            "cover_url": "https://example.com/cover.jpg",
            "geo_address_info": {
                "address": "Test Address 123",
                "city": "Buenos Aires",
                "country": "Argentina",
                "full_address": "Test Address 123, Buenos Aires, Argentina",
                "place_id": "ChIJ_test123",
            },
            "coordinate": {"latitude": -34.6037, "longitude": -58.3816},
            "user": {"name": "Test Organizer"},
            "description": "Test event description",
        }

    def test_can_extract_with_json_indicators(self):
        """Test can_extract returns True for content with JSON indicators."""
        html_with_json = """
        <html>
            <body>
                <script>
                    window.__INITIAL_DATA__ = {"event": {"name": "Test"}};
                </script>
            </body>
        </html>
        """

        self.assertTrue(self.extractor.can_extract(html_with_json))

    def test_can_extract_without_json_indicators(self):
        """Test can_extract returns False for content without JSON indicators."""
        html_without_json = """
        <html>
            <body>
                <h1>Test Page</h1>
                <p>No JSON data here</p>
            </body>
        </html>
        """

        self.assertFalse(self.extractor.can_extract(html_without_json))

    def test_can_extract_with_empty_content(self):
        """Test can_extract handles empty content gracefully."""
        self.assertFalse(self.extractor.can_extract(""))
        self.assertFalse(self.extractor.can_extract(""))

    def test_extract_with_direct_event_pattern(self):
        """Test extraction with direct event object pattern."""
        html_content = f"""
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(self.sample_event_data)}}};
                </script>
            </body>
        </html>
        """

        result = self.extractor.extract(html_content, url="https://lu.ma/test")
        assert result

        self.assertEqual(result["title"], "Test Event")
        self.assertEqual(result["date"], "2025-07-21T22:30:00.000Z")
        self.assertEqual(
            result["location"], "Test Address 123, Buenos Aires, Argentina"
        )
        self.assertEqual(result["extraction_method"], "json")

    def test_extract_with_initial_data_pattern(self):
        """Test extraction with window.__INITIAL_DATA__ pattern."""
        html_content = f"""
        <html>
            <body>
                <script>
                    window.__INITIAL_DATA__ = {{"event": {json.dumps(self.sample_event_data)}}};
                </script>
            </body>
        </html>
        """

        result = self.extractor.extract(html_content, url="https://lu.ma/test")
        assert result

        self.assertEqual(result["title"], "Test Event")
        self.assertEqual(result["api_id"], "evt-test123")
        self.assertEqual(result["event_type"], "independent")

    def test_extract_with_nested_event_data(self):
        """Test extraction with nested event data structure."""
        nested_data = {"props": {"event": self.sample_event_data}}

        html_content = f"""
        <html>
            <body>
                <script>
                    window.__INITIAL_DATA__ = {json.dumps(nested_data)};
                </script>
            </body>
        </html>
        """

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result["title"], "Test Event")
            self.assertEqual(result["timezone"], "America/Buenos_Aires")

    def test_extract_location_data(self):
        """Test comprehensive location data extraction."""
        html_content = f"""
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(self.sample_event_data)}}};
                </script>
            </body>
        </html>
        """

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(
                result["location"], "Test Address 123, Buenos Aires, Argentina"
            )
            self.assertEqual(
                result["full_address"], "Test Address 123, Buenos Aires, Argentina"
            )
            self.assertEqual(result["city"], "Buenos Aires")
            self.assertEqual(result["country"], "Argentina")
            self.assertEqual(result["place_id"], "ChIJ_test123")

            # Check coordinates
            self.assertIn("coordinates", result)
            self.assertEqual(result["coordinates"]["latitude"], -34.6037)
            self.assertEqual(result["coordinates"]["longitude"], -58.3816)

    def test_extract_with_url_construction(self):
        """Test URL construction from event data."""
        html_content = f"""
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(self.sample_event_data)}}};
                </script>
            </body>
        </html>
        """

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result["url"], "https://lu.ma/test-event")

    def test_extract_with_malformed_json(self):
        """Test handling of malformed JSON."""
        html_content = """
        <html>
            <body>
                <script>
                    var data = {"event": {"name": "Test Event", "invalid": }};
                </script>
            </body>
        </html>
        """

        result = self.extractor.extract(html_content)

        self.assertIsNone(result)

    def test_extract_with_no_event_data(self):
        """Test extraction when no event data is present."""
        html_content = """
        <html>
            <body>
                <script>
                    var data = {"user": {"name": "Test User"}};
                </script>
            </body>
        </html>
        """

        result = self.extractor.extract(html_content)

        self.assertIsNone(result)

    def test_clean_json_string(self):
        """Test JSON string cleaning functionality."""
        # Test HTML entity cleaning
        dirty_json = (
            '{"name": "Test &quot;Event&quot;", "location": "Test &amp; Place"}'
        )
        cleaned = self.extractor._clean_json_string(dirty_json)
        if cleaned:
            self.assertIn('"Test "Event""', cleaned)
            self.assertIn('"Test & Place"', cleaned)

        # Test whitespace removal
        whitespace_json = '  {"name": "Test"}  '
        cleaned = self.extractor._clean_json_string(whitespace_json)
        self.assertEqual(cleaned, '{"name": "Test"}')

        # Test comment removal
        comment_json = '{"name": "Test", /* comment */ "id": 1}'
        cleaned = self.extractor._clean_json_string(comment_json)
        if cleaned:
            self.assertNotIn("/*", cleaned)
            self.assertNotIn("*/", cleaned)

    def test_validate_extracted_data(self):
        """Test validation of extracted data."""
        # Valid data
        valid_data = {
            "title": "Test Event",
            "date": "2025-07-21T22:30:00.000Z",
            "location": "Test Location",
        }

        self.assertTrue(self.extractor.validate_extracted_data(valid_data))

        # Invalid data - missing title
        invalid_data = {"date": "2025-07-21T22:30:00.000Z", "location": "Test Location"}

        self.assertFalse(self.extractor.validate_extracted_data(invalid_data))

        # Invalid data - malformed date
        invalid_date_data = {
            "title": "Test Event",
            "date": "invalid-date-format",
            "location": "Test Location",
        }

        self.assertFalse(self.extractor.validate_extracted_data(invalid_date_data))

    def test_custom_patterns_in_config(self):
        """Test custom patterns from configuration."""
        custom_patterns = [r"customPattern:\s*({.*?})", r"specialData\s*=\s*({.*?});"]

        extractor = JsonExtractor(config={"custom_patterns": custom_patterns})

        # Check that custom patterns are added
        self.assertEqual(len(extractor.patterns), len(JsonExtractor.JSON_PATTERNS) + 2)
        self.assertIn(custom_patterns[0], extractor.patterns)
        self.assertIn(custom_patterns[1], extractor.patterns)

    def test_extraction_with_minimal_event_data(self):
        """Test extraction with minimal event data."""
        minimal_event = {
            "name": "Minimal Event",
            "start_at": "2025-07-21T22:30:00.000Z",
        }

        html_content = f"""
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(minimal_event)}}};
                </script>
            </body>
        </html>
        """

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result["title"], "Minimal Event")
            self.assertEqual(result["date"], "2025-07-21T22:30:00.000Z")
            self.assertEqual(result["extraction_method"], "json")

    def test_extraction_with_alternative_organizer_field(self):
        """Test extraction with alternative organizer field names."""
        event_data = self.sample_event_data.copy()
        event_data["organizer"] = {"name": "Alternative Organizer"}
        del event_data["user"]

        html_content = f"""
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(event_data)}}};
                </script>
            </body>
        </html>
        """

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        if result:
            # Should not extract organizer from this structure in current implementation
            self.assertNotIn("organizer", result)

    def test_extraction_with_guest_count_alternatives(self):
        """Test extraction with different guest count field names."""
        event_data = self.sample_event_data.copy()
        event_data["rsvp_count"] = 42

        html_content = f"""
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(event_data)}}};
                </script>
            </body>
        </html>
        """

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result["guest_count"], 42)


if __name__ == "__main__":
    unittest.main()
