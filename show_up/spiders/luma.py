import scrapy
from show_up.items import EventItem


class LumaSpider(scrapy.Spider):
    name = "luma"
    allowed_domains = ["lu.ma"]
    start_urls = ["https://lu.ma/crypto"]

    def parse(self, response):
        # Extract event links from the main page
        event_links = response.css('a.event-card-link::attr(href)').getall()
        for link in event_links:
            yield response.follow(link, self.parse_event)

    def parse_event(self, response):
        # Parse the event page and extract the data
        item = EventItem()
        item['title'] = response.css('h1::text').get()
        item['date'] = response.css('.event-date::text').get()
        item['location'] = response.css('.event-location::text').get()
        item['url'] = response.url
        yield item
