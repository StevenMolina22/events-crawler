import scrapy
from show_up.extractors.json_extractor import EventData
from show_up.items import EventItem
from show_up.extractors import JsonExtractor
from show_up.utils.validation import validate_event_data
from scrapy_playwright.page import PageMethod

HTML_FILE = "output/luma.html"


class LumaSpider(scrapy.Spider):
    name = "luma"
    allowed_domains = ["lu.ma"]
    start_urls = ["https://lu.ma/crypto"]

    def __init__(self, *args, **kwargs):
        self.json_extractor = JsonExtractor(config={"required_fields": ["title"]})

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
        item = EventItem()
        item["url"] = response.url

        extracted_data = self._extract_with_json(response)
        if extracted_data is None:
            raise ValueError("No JSON data found")

        self._populate_item(item, extracted_data)

        # Validate and clean data
        try:
            item_dict = dict(item)
            validated_data = validate_event_data(item_dict)

            for key, value in validated_data.items():
                item[key] = value

        except Exception as e:
            self.logger.error(f"Data validation failed for {response.url}: {e}")

        yield dict(item)  # convert to dict for serialization

    def _extract_with_json(self, response) -> EventData | None:
        """Extract event data using JSON extraction."""
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

    def _populate_item(self, item: EventItem, data: EventData) -> None:
        """Populate EventItem with extracted data."""
        for key, value in data.items():
            if key in item.fields and value:
                item[key] = value
