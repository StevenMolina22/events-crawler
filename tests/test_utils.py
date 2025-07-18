"""
Comprehensive tests for validation utilities.

This module tests the data validation and cleaning functions used
throughout the Show Up Crawler, ensuring data quality and consistency.
"""

import unittest
from datetime import datetime
from show_up.utils.validation import (
    validate_event_data, clean_event_data, normalize_extraction_method,
    validate_required_fields, get_data_completeness_score
)


class TestValidateEventData(unittest.TestCase):
    """Test the validate_event_data function."""

    def test_validate_valid_event_data(self):
        """Test validation with valid event data."""
        valid_data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test-event',
            'date': '2025-07-21T22:30:00.000Z',
            'location': 'Test Location',
            'city': 'Buenos Aires',
            'country': 'Argentina'
        }

        result = validate_event_data(valid_data)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['title'], 'Test Event')
        self.assertEqual(result['url'], 'https://lu.ma/test-event')

    def test_validate_with_missing_required_fields(self):
        """Test validation with missing required fields."""
        invalid_data = {
            'date': '2025-07-21T22:30:00.000Z',
            'location': 'Test Location'
        }

        with self.assertRaises(ValueError) as context:
            validate_event_data(invalid_data)

        self.assertIn('Required field', str(context.exception))

    def test_validate_with_empty_required_fields(self):
        """Test validation with empty required fields."""
        invalid_data = {
            'title': '',
            'url': 'https://lu.ma/test-event',
            'date': '2025-07-21T22:30:00.000Z'
        }

        with self.assertRaises(ValueError) as context:
            validate_event_data(invalid_data)

        self.assertIn('title', str(context.exception))

    def test_validate_with_non_dict_input(self):
        """Test validation with non-dictionary input."""
        with self.assertRaises(ValueError) as context:
            validate_event_data("not a dictionary")

        self.assertIn('must be a dictionary', str(context.exception))

    def test_validate_with_coordinates(self):
        """Test validation with coordinate data."""
        data_with_coords = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test-event',
            'coordinates': {
                'latitude': -34.6037,
                'longitude': -58.3816
            }
        }

        result = validate_event_data(data_with_coords)

        self.assertIn('coordinates', result)
        self.assertEqual(result['coordinates']['latitude'], -34.6037)
        self.assertEqual(result['coordinates']['longitude'], -58.3816)

    def test_validate_with_invalid_coordinates(self):
        """Test validation with invalid coordinate data."""
        data_with_invalid_coords = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test-event',
            'coordinates': {
                'latitude': 999,  # Invalid latitude
                'longitude': -58.3816
            }
        }

        result = validate_event_data(data_with_invalid_coords)

        # Invalid coordinates should be removed
        self.assertNotIn('coordinates', result)

    def test_validate_with_malformed_url(self):
        """Test validation with malformed URLs."""
        data_with_partial_url = {
            'title': 'Test Event',
            'url': '/test-event',  # Partial URL
            'date': '2025-07-21T22:30:00.000Z'
        }

        result = validate_event_data(data_with_partial_url)

        # URL should be normalized
        self.assertEqual(result['url'], 'https://lu.ma/test-event')

    def test_validate_with_datetime_object(self):
        """Test validation with datetime objects."""
        data_with_datetime = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test-event',
            'date': datetime(2025, 7, 21, 22, 30, 0)
        }

        result = validate_event_data(data_with_datetime)

        # Datetime should be converted to ISO string
        self.assertIsInstance(result['date'], str)
        self.assertIn('2025-07-21T22:30:00', result['date'])


class TestCleanEventData(unittest.TestCase):
    """Test the clean_event_data function."""

    def test_clean_with_empty_strings(self):
        """Test cleaning with empty strings."""
        dirty_data = {
            'title': 'Test Event',
            'empty_field': '',
            'whitespace_field': '   ',
            'null_field': None,
            'valid_field': 'Valid Value'
        }

        result = clean_event_data(dirty_data)

        self.assertIn('title', result)
        self.assertIn('valid_field', result)
        self.assertNotIn('empty_field', result)
        self.assertNotIn('whitespace_field', result)
        self.assertNotIn('null_field', result)

    def test_clean_with_whitespace_strings(self):
        """Test cleaning with whitespace in strings."""
        dirty_data = {
            'title': '  Test Event  ',
            'location': '\n  Test Location  \t'
        }

        result = clean_event_data(dirty_data)

        self.assertEqual(result['title'], 'Test Event')
        self.assertEqual(result['location'], 'Test Location')

    def test_clean_with_non_string_values(self):
        """Test cleaning with non-string values."""
        dirty_data = {
            'title': 'Test Event',
            'guest_count': 42,
            'coordinates': {'lat': -34.6037, 'lng': -58.3816},
            'tags': ['crypto', 'blockchain'],
            'zero_value': 0,
            'false_value': False
        }

        result = clean_event_data(dirty_data)

        self.assertEqual(result['title'], 'Test Event')
        self.assertEqual(result['guest_count'], 42)
        self.assertEqual(result['coordinates'], {'lat': -34.6037, 'lng': -58.3816})
        self.assertEqual(result['tags'], ['crypto', 'blockchain'])
        # Zero and False should be removed as they're falsy
        self.assertNotIn('zero_value', result)
        self.assertNotIn('false_value', result)

    def test_clean_preserves_empty_dict(self):
        """Test that cleaning handles empty dictionaries."""
        result = clean_event_data({})
        self.assertEqual(result, {})


class TestNormalizeExtractionMethod(unittest.TestCase):
    """Test the normalize_extraction_method function."""

    def test_normalize_known_methods(self):
        """Test normalization of known extraction methods."""
        test_cases = [
            ('json', 'json'),
            ('JSON', 'json'),
            ('html', 'html'),
            ('HTML', 'html'),
            ('fallback', 'html_fallback'),
            ('css', 'html'),
            ('selector', 'html')
        ]

        for input_method, expected in test_cases:
            result = normalize_extraction_method(input_method)
            self.assertEqual(result, expected)

    def test_normalize_unknown_method(self):
        """Test normalization of unknown extraction methods."""
        result = normalize_extraction_method('unknown_method')
        self.assertEqual(result, 'unknown')

    def test_normalize_empty_method(self):
        """Test normalization of empty extraction method."""
        result = normalize_extraction_method('')
        self.assertEqual(result, 'unknown')


class TestValidateRequiredFields(unittest.TestCase):
    """Test the validate_required_fields function."""

    def test_validate_with_all_required_fields_present(self):
        """Test validation when all required fields are present."""
        data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'date': '2025-07-21T22:30:00.000Z'
        }

        result = validate_required_fields(data, ['title', 'url'])
        self.assertTrue(result)

    def test_validate_with_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {
            'title': 'Test Event',
            'date': '2025-07-21T22:30:00.000Z'
        }

        result = validate_required_fields(data, ['title', 'url'])
        self.assertFalse(result)

    def test_validate_with_empty_required_fields(self):
        """Test validation when required fields are empty."""
        data = {
            'title': '',
            'url': 'https://lu.ma/test'
        }

        result = validate_required_fields(data, ['title', 'url'])
        self.assertFalse(result)

    def test_validate_with_no_required_fields(self):
        """Test validation when no fields are required."""
        data = {'title': 'Test Event'}
        result = validate_required_fields(data, [])
        self.assertTrue(result)


class TestGetDataCompletenessScore(unittest.TestCase):
    """Test the get_data_completeness_score function."""

    def test_completeness_score_with_minimal_data(self):
        """Test completeness score with minimal data."""
        minimal_data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test'
        }

        score = get_data_completeness_score(minimal_data)
        self.assertGreater(score, 0)
        self.assertLess(score, 1)

    def test_completeness_score_with_comprehensive_data(self):
        """Test completeness score with comprehensive data."""
        comprehensive_data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'date': '2025-07-21T22:30:00.000Z',
            'end_date': '2025-07-22T01:00:00.000Z',
            'timezone': 'America/Buenos_Aires',
            'location': 'Test Location',
            'full_address': 'Test Address 123, Buenos Aires, Argentina',
            'city': 'Buenos Aires',
            'country': 'Argentina',
            'coordinates': {'latitude': -34.6037, 'longitude': -58.3816},
            'event_type': 'independent',
            'visibility': 'public',
            'organizer': 'Test Organizer',
            'description': 'Test event description',
            'cover_url': 'https://example.com/cover.jpg',
            'api_id': 'evt-test123',
            'guest_count': 42
        }

        score = get_data_completeness_score(comprehensive_data)
        self.assertGreater(score, 0.8)  # Should be high score
        self.assertLessEqual(score, 1.0)

    def test_completeness_score_with_empty_data(self):
        """Test completeness score with empty data."""
        empty_data = {}
        score = get_data_completeness_score(empty_data)
        self.assertEqual(score, 0.0)

    def test_completeness_score_with_weighted_fields(self):
        """Test that higher-weight fields contribute more to score."""
        # Data with only high-weight fields
        high_weight_data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'date': '2025-07-21T22:30:00.000Z',
            'location': 'Test Location'
        }

        # Data with only low-weight fields
        low_weight_data = {
            'api_id': 'evt-test123',
            'guest_count': 42,
            'cover_url': 'https://example.com/cover.jpg'
        }

        high_score = get_data_completeness_score(high_weight_data)
        low_score = get_data_completeness_score(low_weight_data)

        self.assertGreater(high_score, low_score)


class TestUrlValidation(unittest.TestCase):
    """Test URL validation and normalization."""

    def test_url_with_missing_protocol(self):
        """Test URL normalization when protocol is missing."""
        data = {
            'title': 'Test Event',
            'url': 'lu.ma/test-event'
        }

        result = validate_event_data(data)
        self.assertEqual(result['url'], 'https://lu.ma/test-event')

    def test_url_with_relative_path(self):
        """Test URL normalization with relative paths."""
        data = {
            'title': 'Test Event',
            'url': '/test-event'
        }

        result = validate_event_data(data)
        self.assertEqual(result['url'], 'https://lu.ma/test-event')

    def test_url_with_protocol_relative(self):
        """Test URL normalization with protocol-relative URLs."""
        data = {
            'title': 'Test Event',
            'url': '//lu.ma/test-event'
        }

        result = validate_event_data(data)
        self.assertEqual(result['url'], 'https://lu.ma/test-event')

    def test_url_with_complete_url(self):
        """Test that complete URLs are preserved."""
        data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test-event'
        }

        result = validate_event_data(data)
        self.assertEqual(result['url'], 'https://lu.ma/test-event')


class TestDateValidation(unittest.TestCase):
    """Test date validation and normalization."""

    def test_date_with_iso_format(self):
        """Test date validation with ISO format."""
        data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'date': '2025-07-21T22:30:00.000Z'
        }

        result = validate_event_data(data)
        self.assertEqual(result['date'], '2025-07-21T22:30:00.000Z')

    def test_date_with_alternative_formats(self):
        """Test date validation with alternative formats."""
        test_cases = [
            ('2025-07-21 22:30:00', '2025-07-21T22:30:00'),
            ('2025-07-21', '2025-07-21T00:00:00'),
            ('21/07/2025', '2025-07-21T00:00:00'),
            ('07/21/2025', '2025-07-21T00:00:00')
        ]

        for input_date, expected_start in test_cases:
            data = {
                'title': 'Test Event',
                'url': 'https://lu.ma/test',
                'date': input_date
            }

            result = validate_event_data(data)
            self.assertTrue(result['date'].startswith(expected_start))

    def test_date_with_invalid_format(self):
        """Test date validation with invalid format."""
        data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'date': 'invalid-date-format'
        }

        # Should not raise exception, just keep original value
        result = validate_event_data(data)
        self.assertEqual(result['date'], 'invalid-date-format')


class TestLocationValidation(unittest.TestCase):
    """Test location validation and normalization."""

    def test_location_with_extra_whitespace(self):
        """Test location cleaning with extra whitespace."""
        data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'location': '  Buenos Aires,    Argentina  ',
            'full_address': '\n\n  Test Address 123  \t\t'
        }

        result = validate_event_data(data)
        self.assertEqual(result['location'], 'Buenos Aires, Argentina')
        self.assertEqual(result['full_address'], 'Test Address 123')

    def test_location_with_multiple_spaces(self):
        """Test location cleaning with multiple spaces."""
        data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'location': 'Buenos  Aires,     Argentina'
        }

        result = validate_event_data(data)
        self.assertEqual(result['location'], 'Buenos Aires, Argentina')


if __name__ == '__main__':
    unittest.main()
