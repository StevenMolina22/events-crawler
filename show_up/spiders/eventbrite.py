import scrapy
import json
import re

HTML_FILE = "output/eventbrite.html"
JSON_FILE = "output/evenbrite.json"


class EventbriteSpider(scrapy.Spider):
    name = "eventbrite"
    allowed_domains = ["eventbrite.com.ar"]
    start_urls = ["https://www.eventbrite.com.ar/d/argentina--buenos-aires/tech/"]

    def parse(self, response):
        """
        This function parses the Eventbrite search results page.
        It extracts the event data from the window.__SERVER_DATA__ variable using a regex.
        """
        server_data_script = response.xpath(
            '//script[contains(., "window.__SERVER_DATA__")]/text()'
        ).get()
        if not server_data_script:
            self.logger.error("Could not find window.__SERVER_DATA__ script.")
            return

        # Use regex to find the JSON object
        match = re.search(
            r"window\.__SERVER_DATA__\s*=\s*(\{.*?\});", server_data_script
        )
        if not match:
            self.logger.error("Could not find server data JSON in script.")
            return

        try:
            server_data = json.loads(match.group(1))
            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(server_data, f, ensure_ascii=False, indent=4)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse server data: {e}")
            return

        events = server_data.get("search_data", {}).get("events", {})
        if not events:
            self.logger.warning("No events found in server data.")
            return

        results = events.get("results", [])
        if not results:
            self.logger.warning("No results found in server data.")
            return

        for event in results:
            yield {
                "title": event.get("name"),
                "url": event.get("url"),
                "summary": event.get("summary"),
                "start_date": event.get("start_date"),
                "end_date": event.get("end_date"),
                "location": event.get("primary_venue", {}).get("name"),
                "organizer": event.get("primary_organizer", {}).get("name"),
                "tags": [tag.get("display_name") for tag in event.get("tags", [])],
                "image": event.get("image", {}).get("url"),
                "ticket_availability": event.get("ticket_availability", {}),
            }
