"""
Comprehensive tests for enhanced spider functionality.

This module tests the enhanced LumaSpider with JSON extraction,
validation, and fallback mechanisms.
"""

import pytest
from unittest.mock import Mock, patch
from scrapy.http import HtmlResponse, Request
from scrapy.utils.project import get_project_settings
from show_up.spiders.luma import LumaSpider
from show_up.items import EventItem
from show_up.extractors.json_extractor import JsonExtractor


@pytest.fixture
def spider():
    """Provides a LumaSpider instance."""
    s = LumaSpider()
    s.settings = get_project_settings()
    return s


def test_spider_initialization(spider):
    """Test spider initialization."""
    assert spider.name == "luma"
    assert spider.allowed_domains == ["lu.ma"]
    assert spider.start_urls == ["https://lu.ma/crypto"]
    assert isinstance(spider.json_extractor, JsonExtractor)


def test_spider_initialization_with_custom_patterns():
    """Test spider initialization with custom JSON patterns."""
    mock_settings = Mock()
    mock_settings.getlist.return_value = [
        r"customPattern:\s*({.*?})",
        r"specialData\s*=\s*({.*?});",
    ]
    spider = LumaSpider()
    spider.settings = mock_settings
    spider.__init__()
    # No direct assertion, but we are checking that it runs without error


def test_parse_with_event_links(spider):
    """Test parse method when event links are found."""
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

    with patch.object(response, "css") as mock_css:
        mock_css.return_value.getall.return_value = ["/event1", "/event2", "/event3"]
        with patch.object(response, "follow") as mock_follow:
            mock_follow.return_value = Mock()
            list(spider.parse(response))
            assert mock_follow.call_count == 3
            for call in mock_follow.call_args_list:
                args, kwargs = call
                assert args[1] == spider.parse_event


def test_parse_with_no_event_links(spider):
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

    with patch.object(response, "css") as mock_css:
        mock_css.return_value.getall.return_value = []
        result = list(spider.parse(response))
        assert len(result) == 0


def test_parse_event_with_json_extraction_success(spider):
    """Test parse_event when JSON extraction succeeds."""
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

    with patch.object(spider, "_extract_with_json") as mock_json_extract:
        mock_json_extract.return_value = sample_event_data
        with patch("show_up.spiders.luma.validate_event_data") as mock_validate:
            mock_validate.return_value = sample_event_data
            result = list(spider.parse_event(response))
            assert len(result) == 1
            item = result[0]
            assert isinstance(item, dict)
            assert "title" in item
            assert "url" in item
            assert item["title"] == "Test Event"
            assert item["date"] == "2025-07-21T22:30:00.000Z"
            assert item["location"] == "Test Location"
            assert item["url"] == "https://lu.ma/test-event"
            assert item["extraction_method"] == "json"
            mock_json_extract.assert_called_once()


def test_extract_with_json_success(spider):
    """Test _extract_with_json method success case."""
    spider.settings = Mock()
    spider.settings.getbool.return_value = True
    mock_extracted_data = {
        "title": "Test Event",
        "date": "2025-07-21T22:30:00.000Z",
        "extraction_method": "json",
    }
    with patch.object(spider.json_extractor, "extract") as mock_extract:
        mock_extract.return_value = mock_extracted_data
        response = Mock()
        response.text = "<html>Mock HTML</html>"
        response.url = "https://lu.ma/test-event"
        result = spider._extract_with_json(response)
        assert result == mock_extracted_data
        mock_extract.assert_called_once_with(response.text, url=response.url)


def test_extract_with_json_disabled(spider):
    """Test _extract_with_json method when JSON extraction is disabled."""
    spider.settings = Mock()
    spider.settings.getbool.return_value = False
    response = Mock()
    result = spider._extract_with_json(response)
    assert result is None


def test_extract_with_json_exception_handling(spider):
    """Test _extract_with_json method exception handling."""
    spider.settings = Mock()
    spider.settings.getbool.return_value = True
    with patch.object(spider.json_extractor, "extract") as mock_extract:
        mock_extract.side_effect = Exception("JSON extraction error")
        response = Mock()
        response.text = "<html>Mock HTML</html>"
        response.url = "https://lu.ma/test-event"
        result = spider._extract_with_json(response)
        assert result is None


def test_populate_item_with_complete_data(spider):
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
    spider._populate_item(item, data)
    assert item["title"] == "Test Event"
    assert item["date"] == "2025-07-21T22:30:00.000Z"
    assert item["location"] == "Test Location"
    assert item["coordinates"] == {"latitude": -34.6037, "longitude": -58.3816}
    assert item["organizer"] == "Test Organizer"
    assert item["extraction_method"] == "json"


def test_validation_success(spider):
    """Test successful validation in parse_event."""
    html_content = "<html><body><h1>Test</h1></body></html>"
    request = Request("https://lu.ma/test-event")
    response = HtmlResponse(
        url="https://lu.ma/test-event",
        body=html_content.encode("utf-8"),
        encoding="utf-8",
        request=request,
    )
    with patch.object(spider, "_extract_with_json") as mock_json_extract:
        mock_json_extract.return_value = {
            "title": "Test Event",
            "url": "https://lu.ma/test-event",
            "extraction_method": "json",
        }
        with patch("show_up.spiders.luma.validate_event_data") as mock_validate:
            mock_validate.return_value = {
                "title": "Test Event",
                "url": "https://lu.ma/test-event",
                "extraction_method": "json",
                "validated": True,
            }
            result = list(spider.parse_event(response))
            mock_validate.assert_called_once()
            item = result[0]
            assert item["title"] == "Test Event"
            assert item["url"] == "https://lu.ma/test-event"