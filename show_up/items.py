# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from typing import Any


class EventItem(scrapy.Item):
    """
    Enhanced EventItem for complete event data extraction.

    This item supports comprehensive event information including temporal data,
    location details, metadata, and technical fields for tracking extraction methods.
    """

    # Basic fields
    title = scrapy.Field()  # Event title
    url = scrapy.Field()  # Event URL
    description = scrapy.Field()  # Event description

    # Temporal fields
    date = scrapy.Field()  # Start date (ISO format)
    end_date = scrapy.Field()  # End date (ISO format)
    timezone = scrapy.Field()  # Event timezone (e.g., "America/Buenos_Aires")

    # Location fields
    location = scrapy.Field()  # Simple location string for backward compatibility
    full_address = scrapy.Field()  # Complete formatted address
    city = scrapy.Field()  # City name
    country = scrapy.Field()  # Country name
    coordinates = scrapy.Field()  # Dict with 'latitude' and 'longitude'
    place_id = scrapy.Field()  # Google Place ID or similar

    # Metadata fields
    event_type = scrapy.Field()  # Event type (e.g., "independent", "series")
    visibility = scrapy.Field()  # Visibility (e.g., "public", "private")
    api_id = scrapy.Field()  # Platform-specific API ID
    cover_url = scrapy.Field()  # Cover image URL
    organizer = scrapy.Field()  # Event organizer information
    guest_count = scrapy.Field()  # Number of guests/attendees

    # Technical fields
    html_content = scrapy.Field()  # Processed HTML content
    raw_html = scrapy.Field()  # Raw HTML response
    extraction_method = scrapy.Field()  # How data was extracted ("json", "html", "fallback")

    def __setitem__(self, key: str, value: Any) -> None:
        """Override to provide type hints and validation."""
        super().__setitem__(key, value)

    def __getitem__(self, key: str) -> Any:
        """Override to provide type hints."""
        return super().__getitem__(key)

    def get(self, key: str, default: Any = None) -> Any:
        """Get field value with default."""
        try:
            return self[key]
        except KeyError:
            return default
