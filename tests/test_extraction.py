import pytest
import json
from pathlib import Path
from show_up.extractors.json_extractor import JsonExtractor


@pytest.fixture
def html_dir():
    return Path("output/html")


@pytest.fixture
def html_files(html_dir):
    return list(html_dir.glob("*.html")) if html_dir.exists() else []


@pytest.fixture
def json_extractor():
    return JsonExtractor()


def test_compare_with_original_data():
    original_file = Path("output/debug.json")
    assert original_file.exists(), f"Original file {original_file} not found"
    with open(original_file, "r", encoding="utf-8") as f:
        original_data = json.load(f)
    events = original_data.get("events", [])
    assert events, "No events found in original data"
    events_with_titles = len([e for e in events if e.get("title")])
    assert events_with_titles / len(events) > 0.9, "Less than 90% of events have titles"
