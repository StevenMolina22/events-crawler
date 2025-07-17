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
                        PageMethod("wait_for_selector", ".event-card-link", timeout=60000),
                    ],
                },
            )

    def parse(self, response):
        # Extract event links from the main page
        event_links = response.css('a.event-card-link::attr(href)').getall()
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

    def parse_event(self, response):
        # Parse the event page and extract the data
        item = EventItem()
        item['title'] = response.css('h1::text').get()
        item['date'] = response.css('.event-date::text').get()
        item['location'] = response.css('.event-location::text').get()
        item['url'] = response.url
        item['html_content'] = response.css('main').get()
        yield item
