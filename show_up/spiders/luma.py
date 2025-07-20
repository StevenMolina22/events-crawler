import scrapy
from show_up.items import EventItem
from show_up.extractors import JsonExtractor
from show_up.utils.validation import validate_event_data
from scrapy_playwright.page import PageMethod
from typing import Any

HTML_FILE = "output/luma.html"

class LumaSpider(scrapy.Spider):
    name = "luma"
    allowed_domains = ["lu.ma"]
    start_urls = ["https://lu.ma/crypto"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize JSON extractor
        custom_patterns = []
        if hasattr(self, "settings") and self.settings:
            custom_patterns = self.settings.getlist("JSON_EXTRACTION_PATTERNS", [])

        self.json_extractor = JsonExtractor(
            config={"required_fields": ["title"], "custom_patterns": custom_patterns}
        )

    async def start(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                    ],
                },
            )

    def parse(self, response):
        # Save the full HTML response for debugging
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(response.text)

        # Extract event links from the timeline section
        # Look for individual event cards in the timeline
        event_links = response.css("a.event-link::attr(href)").getall()
        self.logger.info(
            f"Found {len(event_links)} event links with selector 'a.event-link'"
        )

        # Try different selectors to find event links
        alternative_selectors = [
            "a.event-link",
            'a[aria-label*="event"]',
            'a[href*="/1"]',  # Individual event IDs seem to start with /1
            'a[href*="/g"]',  # Some event IDs start with /g
            'a[href*="/v"]',  # Some event IDs start with /v
            '.timeline a[href^="/"]',  # Links in timeline starting with /
        ]

        for selector in alternative_selectors:
            links = response.css(f"{selector}::attr(href)").getall()
            self.logger.info(f"Selector '{selector}' found {len(links)} links")
            if links:
                # Show first few links as examples
                for link in links[:3]:
                    self.logger.info(f"  Example link: {link}")

        # If we found event links, process them
        if event_links:
            for link in event_links:
                yield response.follow(
                    link,
                    self.parse_event,
                    meta={
                        "playwright": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_selector", "h1", timeout=60000),
                        ],
                    },
                )
        else:
            self.logger.warning(
                "No event links found! This might be a JavaScript-heavy page that needs more time to load."
            )

    def parse_event(self, response):
        """Parse event page and extract complete event data using JSON extraction.

        Returns:
            dict: Event data as a dictionary for JSON serialization.
        """
        # Initialize event item
        item = EventItem()

        # Set basic fields
        item["url"] = response.url

        # Try JSON extraction first (primary method)
        extracted_data = self._extract_with_json(response)

        # If JSON extraction fails, fall back to HTML parsing
        if not extracted_data and self.settings.getbool(
            "JSON_EXTRACTION_FALLBACK", True
        ):
            extracted_data = self._extract_with_html_selectors(response)

        # If we still don't have data, create minimal item
        if not extracted_data:
            self.logger.warning(f"Failed to extract data from {response.url}")
            extracted_data = {
                "title": self._extract_title_fallback(response),
                "extraction_method": "fallback",
            }

        # Populate item with extracted data
        self._populate_item(item, extracted_data)

        # Validate and clean data
        try:
            item_dict = dict(item)
            validated_data = validate_event_data(item_dict)

            # Update item with validated data
            for key, value in validated_data.items():
                item[key] = value

            self.logger.info(
                f"Successfully extracted event: {item.get('title', 'Unknown')} using {item.get('extraction_method', 'unknown')}"
            )

        except Exception as e:
            self.logger.error(f"Data validation failed for {response.url}: {e}")

        # Convert to dictionary for JSON serialization (required for -o events.json)
        event_dict: dict[str, Any] = dict(item)
        yield event_dict
        return  # prevents the old `yield item`

    def _extract_with_json(self, response) -> dict[str, Any] | None:
        """Extract event data using JSON extraction."""
        if not self.settings.getbool("JSON_EXTRACTION_ENABLED", True):
            return None

        try:
            extracted_data = self.json_extractor.extract(
                response.text, url=response.url
            )

            if extracted_data:
                self.logger.info(f"JSON extraction successful for {response.url}")
                return extracted_data
            else:
                self.logger.debug(f"JSON extraction found no data for {response.url}")

        except Exception as e:
            self.logger.warning(f"JSON extraction failed for {response.url}: {e}")

        return None

    def _extract_with_html_selectors(self, response) -> dict[str, Any] | None:
        """Extract event data using HTML selectors (fallback method)."""
        self.logger.info(f"Falling back to HTML selector extraction for {response.url}")

        extracted_data = {"extraction_method": "html_fallback"}

        # Try multiple selectors for title
        title = response.css("h1::text").get()
        if not title:
            title = response.css('[data-testid="event-title"]::text').get()
        if not title:
            title = response.css("title::text").get()
        if not title:
            title = response.css(".title::text").get()

        # Try multiple selectors for date
        date = response.css(".event-date::text").get()
        if not date:
            date = response.css('[data-testid="event-date"]::text').get()
        if not date:
            date = response.css("time::text").get()
        if not date:
            date = response.css("[datetime]::attr(datetime)").get()

        # Try multiple selectors for location
        location = response.css(".event-location::text").get()
        if not location:
            location = response.css('[data-testid="event-location"]::text').get()
        if not location:
            location = response.css("address::text").get()
        if not location:
            location = response.css(".location::text").get()

        # Populate extracted data
        if title:
            extracted_data["title"] = title.strip()
        if date:
            extracted_data["date"] = date.strip()
        if location:
            extracted_data["location"] = location.strip()

        return extracted_data if extracted_data.get("title") else None

    def _extract_title_fallback(self, response) -> str:
        """Extract title using multiple fallback methods."""
        # Try page title
        title = response.css("title::text").get()
        if title:
            # Clean up title (remove site name, etc.)
            title = title.replace(" | Luma", "").replace(" - Luma", "").strip()
            return title

        # Try any h1 tag
        title = response.css("h1::text").get()
        if title:
            return title.strip()

        # Try meta property
        title = response.css('meta[property="og:title"]::attr(content)').get()
        if title:
            return title.strip()

        # Final fallback - extract from URL
        url_parts = response.url.split("/")
        if url_parts and url_parts[-1]:
            return url_parts[-1].replace("-", " ").title()

        return "Unknown Event"

    def _populate_item(self, item: EventItem, data: dict[str, Any]) -> None:
        """Populate EventItem with extracted data."""
        # Map extracted data to item fields
        field_mapping = {
            "title": "title",
            "date": "date",
            "end_date": "end_date",
            "timezone": "timezone",
            "location": "location",
            "full_address": "full_address",
            "city": "city",
            "country": "country",
            "coordinates": "coordinates",
            "place_id": "place_id",
            "event_type": "event_type",
            "visibility": "visibility",
            "api_id": "api_id",
            "cover_url": "cover_url",
            "organizer": "organizer",
            "guest_count": "guest_count",
            "description": "description",
            "extraction_method": "extraction_method",
        }

        for data_key, item_key in field_mapping.items():
            if data_key in data and data[data_key]:
                item[item_key] = data[data_key]
