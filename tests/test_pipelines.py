import pytest
import os
import json
from unittest.mock import Mock
from show_up.pipelines import JsonPipeline
from show_up.items import EventItem


@pytest.fixture
def mock_spider():
    """Provides a mock spider."""
    spider = Mock()
    spider.name = "test_spider"
    spider.start_urls = ["https://example.com/test"]
    spider.logger = Mock()
    return spider


@pytest.fixture
def pipeline(tmp_path):
    """Provides a JsonPipeline instance with a temporary output file."""
    test_file = tmp_path / "test_events.json"
    return JsonPipeline(output_file=str(test_file))


def test_from_crawler_with_custom_settings():
    """Test that pipeline reads custom settings from crawler."""
    mock_crawler = Mock()
    mock_settings = {
        "JSON_OUTPUT_FILE": "custom_output.json",
    }
    mock_crawler.settings.get = lambda key, default: mock_settings.get(key, default)
    pipeline_instance = JsonPipeline.from_crawler(mock_crawler)
    assert pipeline_instance.output_file == "custom_output.json"


def test_from_crawler_with_default_settings():
    """Test that pipeline uses default settings when not specified."""
    mock_crawler = Mock()
    mock_crawler.settings.get = lambda key, default: default
    pipeline_instance = JsonPipeline.from_crawler(mock_crawler)
    assert pipeline_instance.output_file == "output/events.json"


def test_process_item_stores_data(pipeline, mock_spider):
    """Test that process_item stores event data."""
    item = EventItem()
    item["title"] = "Test Event"
    item["url"] = "https://lu.ma/test-event"
    item["description"] = "Test event description"

    result = pipeline.process_item(item, mock_spider)

    assert len(pipeline.items) == 1
    stored_item = pipeline.items[0]
    assert stored_item["title"] == "Test Event"
    assert stored_item["url"] == "https://lu.ma/test-event"
    assert stored_item["description"] == "Test event description"
    assert result == item


def test_close_spider_writes_json(pipeline, mock_spider):
    """Test that close_spider writes JSON file correctly."""
    items = [
        {"title": "Event 1", "url": "https://lu.ma/1"},
        {"title": "Event 2", "url": "https://lu.ma/2"},
    ]

    pipeline.open_spider(mock_spider)
    for item_data in items:
        item = EventItem()
        for key, value in item_data.items():
            item[key] = value
        pipeline.process_item(item, mock_spider)
    pipeline.close_spider(mock_spider)

    assert os.path.exists(pipeline.output_file)

    with open(pipeline.output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "events" in data
    assert "count" in data
    assert "scraped_at" in data

    events = data["events"]
    assert len(events) == 2
    assert data["count"] == 2
    assert events[0]["title"] == "Event 1"
    assert events[1]["title"] == "Event 2"


def test_creates_output_directory(tmp_path, mock_spider):
    """Test that output directory is created if it doesn't exist."""
    nested_dir = tmp_path / "nested" / "directory"
    nested_file = nested_dir / "events.json"

    pipeline_instance = JsonPipeline(output_file=str(nested_file))

    item = EventItem()
    item["title"] = "Test Event"
    item["url"] = "https://lu.ma/test"

    pipeline_instance.open_spider(mock_spider)
    pipeline_instance.process_item(item, mock_spider)
    pipeline_instance.close_spider(mock_spider)

    assert os.path.exists(nested_dir)
    assert os.path.exists(nested_file)