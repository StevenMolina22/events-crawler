import scrapy
from show_up.items import EventItem
from scrapy_playwright.page import PageMethod


class LumaSpider(scrapy.Spider):
    name = "luma"
    allowed_domains = ["lu.ma"]
    start_urls = ["https://lu.ma/crypto"]

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
        with open('debug_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Debug: print the length of the response
        self.logger.info(f"Response length: {len(response.text)}")
        
        # Extract event links from the timeline section
        # Look for individual event cards in the timeline
        event_links = response.css('a.event-link::attr(href)').getall()
        self.logger.info(f"Found {len(event_links)} event links with selector 'a.event-link'")
        
        # Try different selectors to find event links
        alternative_selectors = [
            'a.event-link',
            'a[aria-label*="event"]',
            'a[href*="/1"]',  # Individual event IDs seem to start with /1
            'a[href*="/g"]',  # Some event IDs start with /g
            'a[href*="/v"]',  # Some event IDs start with /v
            '.timeline a[href^="/"]',  # Links in timeline starting with /
        ]
        
        for selector in alternative_selectors:
            links = response.css(f'{selector}::attr(href)').getall()
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
            self.logger.warning("No event links found! This might be a JavaScript-heavy page that needs more time to load.")

    def parse_event(self, response):
        # Parse the event page and extract the data
        item = EventItem()
        
        # Try multiple selectors for title
        title = response.css('h1::text').get()
        if not title:
            title = response.css('[data-testid="event-title"]::text').get()
        if not title:
            title = response.css('title::text').get()
        
        # Try multiple selectors for date
        date = response.css('.event-date::text').get()
        if not date:
            date = response.css('[data-testid="event-date"]::text').get()
        if not date:
            date = response.css('time::text').get()
        
        # Try multiple selectors for location
        location = response.css('.event-location::text').get()
        if not location:
            location = response.css('[data-testid="event-location"]::text').get()
        if not location:
            location = response.css('address::text').get()
        
        # Try multiple selectors for HTML content
        html_content = response.css('main').get()
        if not html_content:
            html_content = response.css('body').get()
        if not html_content:
            html_content = response.text
            
        item['title'] = title
        item['date'] = date
        item['location'] = location
        item['url'] = response.url
        item['html_content'] = html_content
        
        # Debug logging
        self.logger.info(f"Parsed event: {item['title']} at {item['url']}")
        if not html_content:
            self.logger.warning(f"No HTML content found for {item['title']}")
            # Save response for debugging
            debug_filename = f"debug_event_{item['title'][:50]}.html"
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
        
        yield item
