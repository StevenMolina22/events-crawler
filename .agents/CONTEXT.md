This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
4. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

## Additional Info

# Directory Structure
```
show_up/
  spiders/
    __init__.py
    luma.py
  items.py
  middlewares.py
  pipelines.py
  settings.py
tests/
  test_pipelines.py
.env.local
main.py
pyproject.toml
```

# Files

## File: tests/test_pipelines.py
```python
import unittest
import tempfile
import os
import shutil
import sys
from unittest.mock import Mock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from show_up.pipelines import RawHtmlFilePipeline
from show_up.items import EventItem


class TestRawHtmlFilePipeline(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.pipeline = RawHtmlFilePipeline()
        self.pipeline.output_dir = self.test_dir

        # Create a mock spider
        self.spider = Mock()
        self.spider.name = "test_spider"

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_open_spider_creates_directory(self):
        # Test that the pipeline creates the output directory
        self.pipeline.open_spider(self.spider)
        self.assertTrue(os.path.exists(self.test_dir))

    def test_process_item_saves_raw_html(self):
        # Arrange
        item = EventItem()
        item['title'] = "Test Event"
        item['raw_html'] = "<html><head><title>Test</title></head><body><h1>Test Event</h1></body></html>"

        self.pipeline.open_spider(self.spider)

        # Act
        result = self.pipeline.process_item(item, self.spider)

        # Assert
        expected_filename = "Test_Event_raw.html"
        expected_filepath = os.path.join(self.test_dir, expected_filename)

        self.assertTrue(os.path.exists(expected_filepath))

        with open(expected_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertEqual(content, item['raw_html'])
        self.assertEqual(result, item)

    def test_process_item_sanitizes_filename(self):
        # Test that special characters in title are sanitized
        item = EventItem()
        item['title'] = "Test Event! @#$%^&*()+=[]{}|;:',.<>?/~`"
        item['raw_html'] = "<html><body>Test content</body></html>"

        self.pipeline.open_spider(self.spider)
        result = self.pipeline.process_item(item, self.spider)

        # Should sanitize to only alphanumeric, spaces, and hyphens
        expected_filename = "Test_Event_raw.html"
        expected_filepath = os.path.join(self.test_dir, expected_filename)

        self.assertTrue(os.path.exists(expected_filepath))

    def test_process_item_without_title_or_raw_html(self):
        # Test that items without title or raw_html are handled gracefully
        item = EventItem()
        item['url'] = "https://example.com"

        self.pipeline.open_spider(self.spider)
        result = self.pipeline.process_item(item, self.spider)

        # Should return the item unchanged and not create any files
        self.assertEqual(result, item)
        self.assertEqual(len(os.listdir(self.test_dir)), 0)

    def test_process_item_with_empty_title(self):
        # Test handling of empty title
        item = EventItem()
        item['title'] = ""
        item['raw_html'] = "<html><body>Content</body></html>"

        self.pipeline.open_spider(self.spider)
        result = self.pipeline.process_item(item, self.spider)

        # Should create a file with sanitized empty name
        expected_filename = "_raw.html"
        expected_filepath = os.path.join(self.test_dir, expected_filename)

        self.assertTrue(os.path.exists(expected_filepath))


if __name__ == '__main__':
    unittest.main()
```

## File: .env.local
```
FIRECRAWL_API_KEY="your_firecrawl_api_key"
```

## File: show_up/spiders/__init__.py
```python
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
```

## File: show_up/middlewares.py
```python
# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ShowUpSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # maching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class ShowUpDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
```

## File: main.py
```python
def main():
    print("Hello from show-up-crawler!")

if __name__ == "__main__":
    main()
```

## File: show_up/items.py
```python
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EventItem(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    location = scrapy.Field()
    url = scrapy.Field()
    html_content = scrapy.Field()
    raw_html = scrapy.Field()
```

## File: show_up/pipelines.py
```python
import json
import os
import re


class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('crypto_events.json', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        # Create a copy of the item and remove the HTML fields
        item_copy = dict(item)
        item_copy.pop('html_content', None)
        item_copy.pop('raw_html', None)
        line = json.dumps(item_copy) + "\n"
        self.file.write(line)
        return item


class HtmlFilePipeline:
    output_dir = 'output/html'

    def open_spider(self, spider):
        os.makedirs(self.output_dir, exist_ok=True)

    def process_item(self, item, spider):
        spider.logger.info(f"Processing item in HtmlFilePipeline: {item}")
        if 'html_content' in item and 'title' in item:
            title = item['title']
            # Sanitize the title to create a valid filename
            filename = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            filepath = os.path.join(self.output_dir, f"{filename}.html")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(item['html_content'])
        return item


class RawHtmlFilePipeline:
    output_dir = 'output/raw_html'

    def open_spider(self, spider):
        os.makedirs(self.output_dir, exist_ok=True)

    def process_item(self, item, spider):
        if 'raw_html' in item and 'title' in item:
            title = item['title']
            # Sanitize the title to create a valid filename
            filename = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            filepath = os.path.join(self.output_dir, f"{filename}_raw.html")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(item['raw_html'])
        return item
```

## File: pyproject.toml
```toml
[project]
name = "show-up-crawler"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "scrapy>=2.13.3",
    "scrapy-playwright>=0.0.33",
]
```

## File: show_up/spiders/luma.py
```python
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
```

## File: show_up/settings.py
```python
# Scrapy settings for show_up project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "show_up"

SPIDER_MODULES = ["show_up.spiders"]
NEWSPIDER_MODULE = "show_up.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "ShowUpCrawler/1.0"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   "show_up.pipelines.JsonWriterPipeline": 300,
   "show_up.pipelines.HtmlFilePipeline": 301,
   "show_up.pipelines.RawHtmlFilePipeline": 302,
}

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "show_up.middlewares.ShowUpSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "show_up.middlewares.ShowUpDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

# Enable Playwright downloader handler
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Configure Playwright
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
}
```
