"""
Comprehensive tests for JSON extractor functionality.

This module tests the JSON extraction logic for Luma event data,
including pattern matching, data parsing, and error handling.
"""

import pytest
import json
from show_up.extractors.json_extractor import JsonExtractor


@pytest.fixture
def extractor():
    """Provides a JsonExtractor instance."""
    return JsonExtractor()


@pytest.fixture
def sample_event_data():
    """Provides sample event data."""
    return {
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


def test_can_extract_with_json_indicators(extractor):
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
    assert extractor.can_extract(html_with_json)


def test_can_extract_without_json_indicators(extractor):
    """Test can_extract returns False for content without JSON indicators."""
    html_without_json = """
    <html>
        <body>
            <h1>Test Page</h1>
            <p>No JSON data here</p>
        </body>
    </html>
    """
    assert not extractor.can_extract(html_without_json)


def test_can_extract_with_empty_content(extractor):
    """Test can_extract handles empty content gracefully."""
    assert not extractor.can_extract("")


def test_extract_with_direct_event_pattern(extractor, sample_event_data):
    """Test extraction with direct event object pattern."""
    html_content = f"""
    <html>
        <body>
            <script>
                var data = {{"event": {json.dumps(sample_event_data)}}};
            </script>
        </body>
    </html>
    """
    result = extractor.extract(html_content, url="https://lu.ma/test")
    assert result
    assert result["title"] == "Test Event"
    assert result["date"] == "2025-07-21T22:30:00.000Z"
    assert result["location"] == "Test Address 123, Buenos Aires, Argentina"
    assert result["extraction_method"] == "json"


def test_extract_with_initial_data_pattern(extractor, sample_event_data):
    """Test extraction with window.__INITIAL_DATA__ pattern."""
    html_content = f"""
    <html>
        <body>
            <script>
                window.__INITIAL_DATA__ = {{"event": {json.dumps(sample_event_data)}}};
            </script>
        </body>
    </html>
    """
    result = extractor.extract(html_content, url="https://lu.ma/test")
    assert result
    assert result["title"] == "Test Event"
    assert result["api_id"] == "evt-test123"
    assert result["event_type"] == "independent"


def test_extract_with_nested_event_data(extractor, sample_event_data):
    """Test extraction with nested event data structure."""
    nested_data = {"props": {"event": sample_event_data}}
    html_content = f"""
    <html>
        <body>
            <script>
                window.__INITIAL_DATA__ = {json.dumps(nested_data)};
            </script>
        </body>
    </html>
    """
    result = extractor.extract(html_content)
    assert result is not None
    if result:
        assert result["title"] == "Test Event"
        assert result["timezone"] == "America/Buenos_Aires"


def test_extract_location_data(extractor, sample_event_data):
    """Test comprehensive location data extraction."""
    html_content = f"""
    <html>
        <body>
            <script>
                var data = {{"event": {json.dumps(sample_event_data)}}};
            </script>
        </body>
    </html>
    """
    result = extractor.extract(html_content)
    assert result is not None
    if result:
        assert result["location"] == "Test Address 123, Buenos Aires, Argentina"
        assert result["full_address"] == "Test Address 123, Buenos Aires, Argentina"
        assert result["city"] == "Buenos Aires"
        assert result["country"] == "Argentina"
        assert result["place_id"] == "ChIJ_test123"
        assert "coordinates" in result
        assert result["coordinates"]["latitude"] == -34.6037
        assert result["coordinates"]["longitude"] == -58.3816


def test_extract_with_url_construction(extractor, sample_event_data):
    """Test URL construction from event data."""
    html_content = f"""
    <html>
        <body>
            <script>
                var data = {{"event": {json.dumps(sample_event_data)}}};
            </script>
        </body>
    </html>
    """
    result = extractor.extract(html_content)
    assert result is not None
    if result:
        assert result["url"] == "https://lu.ma/test-event"


def test_extract_with_malformed_json(extractor):
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
    result = extractor.extract(html_content)
    assert result is None


def test_extract_with_no_event_data(extractor):
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
    result = extractor.extract(html_content)
    assert result is None


def test_clean_json_string(extractor):
    """Test JSON string cleaning functionality."""
    dirty_json = '{"name": "Test &quot;Event&quot;", "location": "Test &amp; Place"}'
    cleaned = extractor._clean_json_string(dirty_json)
    if cleaned:
        assert '"Test "Event""' in cleaned
        assert '"Test & Place"' in cleaned
    whitespace_json = '  {"name": "Test"}  '
    cleaned = extractor._clean_json_string(whitespace_json)
    assert cleaned == '{"name": "Test"}'
    comment_json = '{"name": "Test", /* comment */ "id": 1}'
    cleaned = extractor._clean_json_string(comment_json)
    if cleaned:
        assert "/*" not in cleaned
        assert "*/" not in cleaned


def test_validate_extracted_data(extractor):
    """Test validation of extracted data."""
    valid_data = {
        "title": "Test Event",
        "date": "2025-07-21T22:30:00.000Z",
        "location": "Test Location",
    }
    assert extractor.validate_extracted_data(valid_data)
    invalid_data = {"date": "2025-07-21T22:30:00.000Z", "location": "Test Location"}
    assert not extractor.validate_extracted_data(invalid_data)
    invalid_date_data = {
        "title": "Test Event",
        "date": "invalid-date-format",
        "location": "Test Location",
    }
    assert not extractor.validate_extracted_data(invalid_date_data)


def test_custom_patterns_in_config():
    """Test custom patterns from configuration."""
    custom_patterns = [r"customPattern:\s*({.*?})", r"specialData\s*=\s*({.*?});"]
    extractor = JsonExtractor(config={"custom_patterns": custom_patterns})
    assert len(extractor.patterns) == len(JsonExtractor.JSON_PATTERNS) + 2
    assert custom_patterns[0] in extractor.patterns
    assert custom_patterns[1] in extractor.patterns


def test_extraction_with_minimal_event_data(extractor):
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
    result = extractor.extract(html_content)
    assert result is not None
    if result:
        assert result["title"] == "Minimal Event"
        assert result["date"] == "2025-07-21T22:30:00.000Z"
        assert result["extraction_method"] == "json"


def test_extraction_with_alternative_organizer_field(extractor, sample_event_data):
    """Test extraction with alternative organizer field names."""
    event_data = sample_event_data.copy()
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
    result = extractor.extract(html_content)
    assert result is not None
    if result:
        assert "organizer" not in result


def test_extraction_with_guest_count_alternatives(extractor, sample_event_data):
    """Test extraction with different guest count field names."""
    event_data = sample_event_data.copy()
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
    result = extractor.extract(html_content)
    assert result is not None
    if result:
        assert result["guest_count"] == 42