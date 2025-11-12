"""
Comprehensive tests for validation utilities.

This module tests the data validation and cleaning functions used
throughout the Show Up Crawler, ensuring data quality and consistency.
"""

import pytest
from datetime import datetime
from show_up.utils.validation import (
    validate_event_data,
    clean_event_data,
    normalize_extraction_method,
    validate_required_fields,
    get_data_completeness_score,
)


def test_validate_valid_event_data():
    """Test validation with valid event data."""
    valid_data = {
        "title": "Test Event",
        "url": "https://lu.ma/test-event",
        "date": "2025-07-21T22:30:00.000Z",
        "location": "Test Location",
        "city": "Buenos Aires",
        "country": "Argentina",
    }
    result = validate_event_data(valid_data)
    assert isinstance(result, dict)
    assert result["title"] == "Test Event"
    assert result["url"] == "https://lu.ma/test-event"


def test_validate_with_missing_required_fields():
    """Test validation with missing required fields."""
    invalid_data = {"date": "2025-07-21T22:30:00.000Z", "location": "Test Location"}
    with pytest.raises(ValueError, match="Required field"):
        validate_event_data(invalid_data)


def test_validate_with_empty_required_fields():
    """Test validation with empty required fields."""
    invalid_data = {
        "title": "",
        "url": "https://lu.ma/test-event",
        "date": "2025-07-21T22:30:00.000Z",
    }
    with pytest.raises(ValueError, match="title"):
        validate_event_data(invalid_data)


def test_validate_with_non_dict_input():
    """Test validation with non-dictionary input."""
    with pytest.raises(ValueError, match="Required field"):
        validate_event_data({"invalid": "not a dictionary"})


def test_validate_with_coordinates():
    """Test validation with coordinate data."""
    data_with_coords = {
        "title": "Test Event",
        "url": "https://lu.ma/test-event",
        "coordinates": {"latitude": -34.6037, "longitude": -58.3816},
    }
    result = validate_event_data(data_with_coords)
    assert "coordinates" in result
    assert result["coordinates"]["latitude"] == -34.6037
    assert result["coordinates"]["longitude"] == -58.3816


def test_validate_with_invalid_coordinates():
    """Test validation with invalid coordinate data."""
    data_with_invalid_coords = {
        "title": "Test Event",
        "url": "https://lu.ma/test-event",
        "coordinates": {
            "latitude": 999,  # Invalid latitude
            "longitude": -58.3816,
        },
    }
    result = validate_event_data(data_with_invalid_coords)
    assert "coordinates" not in result


def test_validate_with_malformed_url():
    """Test validation with malformed URLs."""
    data_with_partial_url = {
        "title": "Test Event",
        "url": "/test-event",  # Partial URL
        "date": "2025-07-21T22:30:00.000Z",
    }
    result = validate_event_data(data_with_partial_url)
    assert result["url"] == "https://lu.ma/test-event"


def test_validate_with_datetime_object():
    """Test validation with datetime objects."""
    data_with_datetime = {
        "title": "Test Event",
        "url": "https://lu.ma/test-event",
        "date": datetime(2025, 7, 21, 22, 30, 0),
    }
    result = validate_event_data(data_with_datetime)
    assert isinstance(result["date"], str)
    assert "2025-07-21T22:30:00" in result["date"]


def test_clean_with_empty_strings():
    """Test cleaning with empty strings."""
    dirty_data = {
        "title": "Test Event",
        "empty_field": "",
        "whitespace_field": "   ",
        "null_field": None,
        "valid_field": "Valid Value",
    }
    result = clean_event_data(dirty_data)
    assert "title" in result
    assert "valid_field" in result
    assert "empty_field" not in result
    assert "whitespace_field" not in result
    assert "null_field" not in result


def test_clean_with_whitespace_strings():
    """Test cleaning with whitespace in strings."""
    dirty_data = {"title": "  Test Event  ", "location": "\n  Test Location  \t"}
    result = clean_event_data(dirty_data)
    assert result["title"] == "Test Event"
    assert result["location"] == "Test Location"


def test_clean_with_non_string_values():
    """Test cleaning with non-string values."""
    dirty_data = {
        "title": "Test Event",
        "guest_count": 42,
        "coordinates": {"lat": -34.6037, "lng": -58.3816},
        "tags": ["crypto", "blockchain"],
        "zero_value": 0,
        "false_value": False,
    }
    result = clean_event_data(dirty_data)
    assert result["title"] == "Test Event"
    assert result["guest_count"] == 42
    assert result["coordinates"] == {"lat": -34.6037, "lng": -58.3816}
    assert result["tags"] == ["crypto", "blockchain"]
    assert "zero_value" not in result
    assert "false_value" not in result


def test_clean_preserves_empty_dict():
    """Test that cleaning handles empty dictionaries."""
    result = clean_event_data({})
    assert result == {}


@pytest.mark.parametrize(
    "input_method,expected",
    [
        ("json", "json"),
        ("JSON", "json"),
        ("html", "html"),
        ("HTML", "html"),
        ("fallback", "html_fallback"),
        ("css", "html"),
        ("selector", "html"),
        ("unknown_method", "unknown"),
        ("", "unknown"),
    ],
)
def test_normalize_extraction_method(input_method, expected):
    """Test normalization of extraction methods."""
    assert normalize_extraction_method(input_method) == expected


def test_validate_with_all_required_fields_present():
    """Test validation when all required fields are present."""
    data = {
        "title": "Test Event",
        "url": "https://lu.ma/test",
        "date": "2025-07-21T22:30:00.000Z",
    }
    assert validate_required_fields(data, ["title", "url"])


def test_validate_with_missing_required_fields():
    """Test validation when required fields are missing."""
    data = {"title": "Test Event", "date": "2025-07-21T22:30:00.000Z"}
    assert not validate_required_fields(data, ["title", "url"])


def test_validate_with_empty_required_fields():
    """Test validation when required fields are empty."""
    data = {"title": "", "url": "https://lu.ma/test"}
    assert not validate_required_fields(data, ["title", "url"])


def test_validate_with_no_required_fields():
    """Test validation when no fields are required."""
    data = {"title": "Test Event"}
    assert validate_required_fields(data, [])


def test_completeness_score_with_minimal_data():
    """Test completeness score with minimal data."""
    minimal_data = {"title": "Test Event", "url": "https://lu.ma/test"}
    score = get_data_completeness_score(minimal_data)
    assert 0 < score < 1


def test_completeness_score_with_comprehensive_data():
    """Test completeness score with comprehensive data."""
    comprehensive_data = {
        "title": "Test Event",
        "url": "https://lu.ma/test",
        "date": "2025-07-21T22:30:00.000Z",
        "end_date": "2025-07-22T01:00:00.000Z",
        "timezone": "America/Buenos_Aires",
        "location": "Test Location",
        "full_address": "Test Address 123, Buenos Aires, Argentina",
        "city": "Buenos Aires",
        "country": "Argentina",
        "coordinates": {"latitude": -34.6037, "longitude": -58.3816},
        "event_type": "independent",
        "visibility": "public",
        "organizer": "Test Organizer",
        "description": "Test event description",
        "cover_url": "https://example.com/cover.jpg",
        "api_id": "evt-test123",
        "guest_count": 42,
    }
    score = get_data_completeness_score(comprehensive_data)
    assert 0.8 < score <= 1.0


def test_completeness_score_with_empty_data():
    """Test completeness score with empty data."""
    empty_data = {}
    score = get_data_completeness_score(empty_data)
    assert score == 0.0


def test_completeness_score_with_weighted_fields():
    """Test that higher-weight fields contribute more to score."""
    high_weight_data = {
        "title": "Test Event",
        "url": "https://lu.ma/test",
        "date": "2025-07-21T22:30:00.000Z",
        "location": "Test Location",
    }
    low_weight_data = {
        "api_id": "evt-test123",
        "guest_count": 42,
        "cover_url": "https://example.com/cover.jpg",
    }
    high_score = get_data_completeness_score(high_weight_data)
    low_score = get_data_completeness_score(low_weight_data)
    assert high_score > low_score


def test_url_with_missing_protocol():
    """Test URL normalization when protocol is missing."""
    data = {"title": "Test Event", "url": "lu.ma/test-event"}
    result = validate_event_data(data)
    assert result["url"] == "https://lu.ma/test-event"


def test_url_with_relative_path():
    """Test URL normalization with relative paths."""
    data = {"title": "Test Event", "url": "/test-event"}
    result = validate_event_data(data)
    assert result["url"] == "https://lu.ma/test-event"


def test_url_with_protocol_relative():
    """Test URL normalization with protocol-relative URLs."""
    data = {"title": "Test Event", "url": "//lu.ma/test-event"}
    result = validate_event_data(data)
    assert result["url"] == "https://lu.ma/test-event"


def test_url_with_complete_url():
    """Test that complete URLs are preserved."""
    data = {"title": "Test Event", "url": "https://lu.ma/test-event"}
    result = validate_event_data(data)
    assert result["url"] == "https://lu.ma/test-event"


def test_date_with_iso_format():
    """Test date validation with ISO format."""
    data = {
        "title": "Test Event",
        "url": "https://lu.ma/test",
        "date": "2025-07-21T22:30:00.000Z",
    }
    result = validate_event_data(data)
    assert result["date"] == "2025-07-21T22:30:00.000Z"


@pytest.mark.parametrize(
    "input_date,expected_start",
    [
        ("2025-07-21 22:30:00", "2025-07-21T22:30:00"),
        ("2025-07-21", "2025-07-21T00:00:00"),
        ("21/07/2025", "2025-07-21T00:00:00"),
        ("07/21/2025", "2025-07-21T00:00:00"),
    ],
)
def test_date_with_alternative_formats(input_date, expected_start):
    """Test date validation with alternative formats."""
    data = {
        "title": "Test Event",
        "url": "https://lu.ma/test",
        "date": input_date,
    }
    result = validate_event_data(data)
    assert result["date"].startswith(expected_start)


def test_date_with_invalid_format():
    """Test date validation with invalid format."""
    data = {
        "title": "Test Event",
        "url": "https://lu.ma/test",
        "date": "invalid-date-format",
    }
    result = validate_event_data(data)
    assert result["date"] == "invalid-date-format"


def test_location_with_extra_whitespace():
    """Test location cleaning with extra whitespace."""
    data = {
        "title": "Test Event",
        "url": "https://lu.ma/test",
        "location": "  Buenos Aires,    Argentina  ",
        "full_address": "\n\n  Test Address 123  \t\t",
    }
    result = validate_event_data(data)
    assert result["location"] == "Buenos Aires, Argentina"
    assert result["full_address"] == "Test Address 123"


def test_location_with_multiple_spaces():
    """Test location cleaning with multiple spaces."""
    data = {
        "title": "Test Event",
        "url": "https://lu.ma/test",
        "location": "Buenos  Aires,     Argentina",
    }
    result = validate_event_data(data)
    assert result["location"] == "Buenos Aires, Argentina"
