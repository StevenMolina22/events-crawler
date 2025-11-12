import scrapy

HTML_FILE = "output/meetup.html"


class MeetupSpider(scrapy.Spider):
    name = "meetup"
    allowed_domains = ["meetup.com"]
    start_urls = ["https://www.meetup.com/find/?keywords=tech"]

    def parse(self, response):
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(response.text)
