"""
Comprehensive tests for JSON extractor functionality.

This module tests the JSON extraction logic for Luma event data,
including pattern matching, data parsing, and error handling.
"""

import unittest
import json
from unittest.mock import Mock, patch
from show_up.extractors.json_extractor import JsonExtractor
from show_up.extractors.base import BaseExtractor, MultiExtractor


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
                "place_id": "ChIJ_test123"
            },
            "coordinate": {
                "latitude": -34.6037,
                "longitude": -58.3816
            },
            "user": {
                "name": "Test Organizer"
            },
            "description": "Test event description"
        }

    def test_can_extract_with_json_indicators(self):
        """Test can_extract returns True for content with JSON indicators."""
        html_with_json = '''
        <html>
            <body>
                <script>
                    window.__INITIAL_DATA__ = {"event": {"name": "Test"}};
                </script>
            </body>
        </html>
        '''

        self.assertTrue(self.extractor.can_extract(html_with_json))

    def test_can_extract_without_json_indicators(self):
        """Test can_extract returns False for content without JSON indicators."""
        html_without_json = '''
        <html>
            <body>
                <h1>Test Page</h1>
                <p>No JSON data here</p>
            </body>
        </html>
        '''

        self.assertFalse(self.extractor.can_extract(html_without_json))

    def test_can_extract_with_empty_content(self):
        """Test can_extract handles empty content gracefully."""
        self.assertFalse(self.extractor.can_extract(""))
        self.assertFalse(self.extractor.can_extract(""))

    def test_extract_with_direct_event_pattern(self):
        """Test extraction with direct event object pattern."""
        html_content = f'''
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(self.sample_event_data)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content, url="https://lu.ma/test")

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result['title'], "Test Event")
            self.assertEqual(result['date'], "2025-07-21T22:30:00.000Z")
            self.assertEqual(result['location'], "Test Address 123, Buenos Aires, Argentina")
            self.assertEqual(result['extraction_method'], 'json')

    def test_extract_with_initial_data_pattern(self):
        """Test extraction with window.__INITIAL_DATA__ pattern."""
        html_content = f'''
        <html>
            <body>
                <script>
                    window.__INITIAL_DATA__ = {{"event": {json.dumps(self.sample_event_data)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content, url="https://lu.ma/test")

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result['title'], "Test Event")
            self.assertEqual(result['api_id'], "evt-test123")
            self.assertEqual(result['event_type'], "independent")

    def test_extract_with_nested_event_data(self):
        """Test extraction with nested event data structure."""
        nested_data = {
            "props": {
                "event": self.sample_event_data
            }
        }

        html_content = f'''
        <html>
            <body>
                <script>
                    window.__INITIAL_DATA__ = {json.dumps(nested_data)};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result['title'], "Test Event")
            self.assertEqual(result['timezone'], "America/Buenos_Aires")

    def test_extract_location_data(self):
        """Test comprehensive location data extraction."""
        html_content = f'''
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(self.sample_event_data)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result['location'], "Test Address 123, Buenos Aires, Argentina")
            self.assertEqual(result['full_address'], "Test Address 123, Buenos Aires, Argentina")
            self.assertEqual(result['city'], "Buenos Aires")
            self.assertEqual(result['country'], "Argentina")
            self.assertEqual(result['place_id'], "ChIJ_test123")

            # Check coordinates
            self.assertIn('coordinates', result)
            self.assertEqual(result['coordinates']['latitude'], -34.6037)
            self.assertEqual(result['coordinates']['longitude'], -58.3816)

    def test_extract_with_url_construction(self):
        """Test URL construction from event data."""
        html_content = f'''
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(self.sample_event_data)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result['url'], "https://lu.ma/test-event")

    def test_extract_with_malformed_json(self):
        """Test handling of malformed JSON."""
        html_content = '''
        <html>
            <body>
                <script>
                    var data = {"event": {"name": "Test Event", "invalid": }};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNone(result)

    def test_extract_with_no_event_data(self):
        """Test extraction when no event data is present."""
        html_content = '''
        <html>
            <body>
                <script>
                    var data = {"user": {"name": "Test User"}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNone(result)

    def test_clean_json_string(self):
        """Test JSON string cleaning functionality."""
        # Test HTML entity cleaning
        dirty_json = '{"name": "Test &quot;Event&quot;", "location": "Test &amp; Place"}'
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
            self.assertNotIn('/*', cleaned)
            self.assertNotIn('*/', cleaned)

    def test_validate_extracted_data(self):
        """Test validation of extracted data."""
        # Valid data
        valid_data = {
            'title': 'Test Event',
            'date': '2025-07-21T22:30:00.000Z',
            'location': 'Test Location'
        }

        self.assertTrue(self.extractor.validate_extracted_data(valid_data))

        # Invalid data - missing title
        invalid_data = {
            'date': '2025-07-21T22:30:00.000Z',
            'location': 'Test Location'
        }

        self.assertFalse(self.extractor.validate_extracted_data(invalid_data))

        # Invalid data - malformed date
        invalid_date_data = {
            'title': 'Test Event',
            'date': 'invalid-date-format',
            'location': 'Test Location'
        }

        self.assertFalse(self.extractor.validate_extracted_data(invalid_date_data))

    def test_get_extraction_method(self):
        """Test extraction method name."""
        self.assertEqual(self.extractor.get_extraction_method(), 'json')

    def test_custom_patterns_in_config(self):
        """Test custom patterns from configuration."""
        custom_patterns = [
            r'customPattern:\s*({.*?})',
            r'specialData\s*=\s*({.*?});'
        ]

        extractor = JsonExtractor(config={'custom_patterns': custom_patterns})

        # Check that custom patterns are added
        self.assertEqual(len(extractor.patterns), len(JsonExtractor.JSON_PATTERNS) + 2)
        self.assertIn(custom_patterns[0], extractor.patterns)
        self.assertIn(custom_patterns[1], extractor.patterns)

    def test_extraction_with_minimal_event_data(self):
        """Test extraction with minimal event data."""
        minimal_event = {
            "name": "Minimal Event",
            "start_at": "2025-07-21T22:30:00.000Z"
        }

        html_content = f'''
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(minimal_event)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result['title'], "Minimal Event")
            self.assertEqual(result['date'], "2025-07-21T22:30:00.000Z")
            self.assertEqual(result['extraction_method'], 'json')

    def test_extraction_with_alternative_organizer_field(self):
        """Test extraction with alternative organizer field names."""
        event_data = self.sample_event_data.copy()
        event_data['organizer'] = {'name': 'Alternative Organizer'}
        del event_data['user']

        html_content = f'''
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(event_data)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        if result:
            # Should not extract organizer from this structure in current implementation
            self.assertNotIn('organizer', result)

    def test_extraction_with_guest_count_alternatives(self):
        """Test extraction with different guest count field names."""
        event_data = self.sample_event_data.copy()
        event_data['rsvp_count'] = 42

        html_content = f'''
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(event_data)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result['guest_count'], 42)


class TestBaseExtractor(unittest.TestCase):
    """Test the BaseExtractor abstract class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete implementation for testing
        class TestExtractor(BaseExtractor):
            def extract(self, content, **kwargs):
                if "test_data" in content:
                    return {"title": "Test Event", "extraction_method": "test"}
                return None

            def can_extract(self, content):
                return "test_data" in content

        self.extractor = TestExtractor()

    def test_get_extraction_method(self):
        """Test extraction method name generation."""
        self.assertEqual(self.extractor.get_extraction_method(), 'test')

    def test_validate_extracted_data_with_valid_data(self):
        """Test validation with valid data."""
        valid_data = {"title": "Test Event", "url": "https://test.com"}
        self.assertTrue(self.extractor.validate_extracted_data(valid_data))

    def test_validate_extracted_data_with_invalid_data(self):
        """Test validation with invalid data."""
        # Test with empty dict - should be valid for base extractor
        empty_data = {}
        self.assertTrue(self.extractor.validate_extracted_data(empty_data))

        # Test with invalid type - should be invalid
        invalid_data = "not a dictionary"
        self.assertFalse(self.extractor.validate_extracted_data(invalid_data))

    def test_validate_extracted_data_with_required_fields(self):
        """Test validation with required fields configuration."""
        # Use the concrete TestExtractor instead of abstract BaseExtractor
        class TestExtractorWithConfig(BaseExtractor):
            def extract(self, content, **kwargs):
                return {"title": "Test Event"}

            def can_extract(self, content):
                return True

        extractor = TestExtractorWithConfig(config={'required_fields': ['title', 'url']})

        # Valid data with all required fields
        valid_data = {"title": "Test Event", "url": "https://test.com"}
        self.assertTrue(extractor.validate_extracted_data(valid_data))

        # Invalid data missing required field
        invalid_data = {"title": "Test Event"}
        self.assertFalse(extractor.validate_extracted_data(invalid_data))

    def test_log_extraction_result(self):
        """Test extraction result logging."""
        with patch.object(self.extractor, 'logger') as mock_logger:
            # Test successful extraction
            self.extractor.log_extraction_result(True, {"title": "Test"})
            mock_logger.info.assert_called()

            # Test failed extraction
            self.extractor.log_extraction_result(False)
            mock_logger.warning.assert_called()


class TestMultiExtractor(unittest.TestCase):
    """Test the MultiExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock extractors
        self.mock_extractor1 = Mock(spec=BaseExtractor)
        self.mock_extractor2 = Mock(spec=BaseExtractor)

        self.multi_extractor = MultiExtractor([self.mock_extractor1, self.mock_extractor2])

    def test_extract_with_first_extractor_success(self):
        """Test extraction when first extractor succeeds."""
        # Configure first extractor to succeed
        self.mock_extractor1.can_extract.return_value = True
        self.mock_extractor1.extract.return_value = {"title": "Test Event"}
        self.mock_extractor1.validate_extracted_data.return_value = True
        self.mock_extractor1.get_extraction_method.return_value = "test1"
        self.mock_extractor1.log_extraction_result = Mock()

        # Second extractor should not be called
        self.mock_extractor2.can_extract.return_value = False

        result = self.multi_extractor.extract("test content")

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result['title'], "Test Event")
            self.assertEqual(result['extraction_method'], "test1")

        # Verify only first extractor was used
        self.mock_extractor1.can_extract.assert_called_once()
        self.mock_extractor1.extract.assert_called_once()
        self.mock_extractor2.can_extract.assert_not_called()

    def test_extract_with_fallback_to_second_extractor(self):
        """Test extraction falling back to second extractor."""
        # Configure first extractor to fail
        self.mock_extractor1.can_extract.return_value = True
        self.mock_extractor1.extract.return_value = None
        self.mock_extractor1.validate_extracted_data.return_value = False
        self.mock_extractor1.get_extraction_method.return_value = "test1"
        self.mock_extractor1.log_extraction_result = Mock()

        # Configure second extractor to succeed
        self.mock_extractor2.can_extract.return_value = True
        self.mock_extractor2.extract.return_value = {"title": "Test Event 2"}
        self.mock_extractor2.validate_extracted_data.return_value = True
        self.mock_extractor2.get_extraction_method.return_value = "test2"
        self.mock_extractor2.log_extraction_result = Mock()

        result = self.multi_extractor.extract("test content")

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result['title'], "Test Event 2")
            self.assertEqual(result['extraction_method'], "test2")

        # Verify both extractors were tried
        self.mock_extractor1.can_extract.assert_called_once()
        self.mock_extractor1.extract.assert_called_once()
        self.mock_extractor2.can_extract.assert_called_once()
        self.mock_extractor2.extract.assert_called_once()

    def test_extract_with_all_extractors_failing(self):
        """Test extraction when all extractors fail."""
        # Configure both extractors to fail
        self.mock_extractor1.can_extract.return_value = False
        self.mock_extractor2.can_extract.return_value = False

        result = self.multi_extractor.extract("test content")

        self.assertIsNone(result)

    def test_extract_with_extractor_exception(self):
        """Test extraction when extractor raises exception."""
        # Configure first extractor to raise exception
        self.mock_extractor1.can_extract.return_value = True
        self.mock_extractor1.extract.side_effect = Exception("Test error")
        self.mock_extractor1.log_extraction_result = Mock()

        # Configure second extractor to succeed
        self.mock_extractor2.can_extract.return_value = True
        self.mock_extractor2.extract.return_value = {"title": "Test Event 2"}
        self.mock_extractor2.validate_extracted_data.return_value = True
        self.mock_extractor2.get_extraction_method.return_value = "test2"
        self.mock_extractor2.log_extraction_result = Mock()

        result = self.multi_extractor.extract("test content")

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result['title'], "Test Event 2")

        # Verify exception was handled and second extractor was used
        self.mock_extractor1.log_extraction_result.assert_called_with(False)
        self.mock_extractor2.extract.assert_called_once()

    def test_get_available_extractors(self):
        """Test getting list of available extractors."""
        self.mock_extractor1.get_extraction_method.return_value = "test1"
        self.mock_extractor2.get_extraction_method.return_value = "test2"

        extractors = self.multi_extractor.get_available_extractors()

        self.assertEqual(extractors, ["test1", "test2"])


if __name__ == '__main__':
    unittest.main()
