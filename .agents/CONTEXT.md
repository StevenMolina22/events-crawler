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
.agents/
  AGENT.md
  PLANNING.md
  RULES.md
  TASKS.md
show_up/
  spiders/
    __init__.py
    luma.py
  items.py
  middlewares.py
  pipelines.py
  settings.py
main.py
pyproject.toml
```

# Files

## File: show_up/spiders/__init__.py
```python
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
```

## File: show_up/spiders/luma.py
```python
import scrapy


class LumaSpider(scrapy.Spider):
    name = "luma"
    allowed_domains = ["lu.ma"]
    start_urls = ["https://lu.ma/crypto"]

    def parse(self, response):
        pass
```

## File: show_up/items.py
```python
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ShowUpItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
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

## File: show_up/pipelines.py
```python
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ShowUpPipeline:
    def process_item(self, item, spider):
        return item
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
#USER_AGENT = "show_up (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

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

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "show_up.pipelines.ShowUpPipeline": 300,
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
```

## File: .agents/AGENT.md
```markdown
# 🤖 Agent Guide

This document defines how an agent should operate within this project. **Follow these instructions strictly.**

---

### 🧭 Project Awareness & Context

- **Check** `.agents/` directory to get information adapted for LLMs for the project
- **Always read `.agents/PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `.agents/TASKS.md`** before starting a new task. If the task isn’t listed, add it with a brief description and today's date.
- **Check `.agents/RULES.md`** for any rules the project has.
- **Check `.agents/CONTEXT.md`** for the context and files of the project.
- **NEVER modify the `.agents/CONTEXT.md`** file.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `.agents/PLANNING.md`.

---

### 🧱 Code Structure & Modularity

- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
- **Use clear, consistent imports** (prefer relative imports within packages).

---

### ✅ Task Completion

- **Mark completed tasks in `.agents/TASKS.md`** immediately after finishing them.
- **Add discovered bugs or sub-tasks** during development under “Discovered During Work” in `.agents/TASKS.md`.
- **Focus ONLY on the requested problem or feature**.
  - If unrelated issues are found, log them under “Discovered During Work.”
  - Do not fix unrelated issues unless they block the current task.

---

### 📚 Documentation & Explainability

- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Update `.agents/`** when new features are added, tasks are done or there is any relevant change on the codebase, **ALWAYS** make sure the `.agents/` folder is up to date with the codebase.
- **For complex logic, add inline `# Reason:` comment** explaining the why, not just the what.

---

### 🧠 AI Behavior Rules

- **Never assume missing context. Ask questions if uncertain.**
- **Always confirm file paths and module names** exist before referencing them in code.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `.agents/TASKS.md`.
- **Focus ONLY on the problem and prompt at hand** Do not build unrelated features.
- **ALWAYS plan before codign complex tasks** Wait for approval before proceeding with implementation.
- When planning, analyze options first — don’t implement until requested.
- Install new dependencies only if absolutely required by the task.
- If an error occurs during execution or installation, document the error in `.agents/TASKS.md` and propose a resolution before proceeding.
- Use environment variables over hard-coded keys.

---

### Coding Rules

- Always use modern type hints in python (3.13+).
- Always use `uv` as a python manager. Run libraries with `uv run ...`.
- For `python` testing use `assert` when enough or `pytes` when necessary.
- Use `pnpm` on node if possible, except if other package manager is being used.
- Always prefer typescript over javascript.
- Always prefer ES-modules in JS.
- Always use function components in `react`.

---

## ✔️ Summary

**Stick to these principles.**
Keep `.agents/` and the codebase in sync.
Communicate context, plan carefully, commit small, test everything.
If you’re unsure — ask.
No assumptions.
No shortcuts.

---
```

## File: .agents/PLANNING.md
```markdown
# 🗺️ Planning

This document outlines the architecture, goals, and conventions for the Show Up Crawler project.

## 🚀 Project Goals

The primary goal of this project is to create a web crawler that extracts information about crypto-related events happening in Buenos Aires from various event websites. The initial focus will be on `lu.ma`.

The extracted data should include:
- Event title
- Date and time
- Location
- Description
- Organizer
- Event URL

## 🏗️ Architecture

The project will be built using Python and the Scrapy framework.

- **Crawler**: A Scrapy spider will be developed to crawl `lu.ma` and other target websites.
- **Data Storage**: Initially, the scraped data will be stored in a JSON file. In the future, we might consider a database like PostgreSQL or MongoDB.
- **Configuration**: Project settings and configurations will be managed in `scrapy.cfg` and the Scrapy settings file.

## 🎨 Code Style & Conventions

- **Language**: Python 3.13+ with modern type hints.
- **Package Manager**: `uv` will be used for managing Python dependencies.
- **Testing**: `pytest` will be used for testing.
- **Linting & Formatting**: `ruff` will be used for linting and formatting to ensure code quality.
- **Modularity**: Code will be organized into spiders, items, and pipelines as per Scrapy's conventions.

## ⛓️ Constraints

- Adhere to the rules in `.agents/RULES.md`.
- Do not add any new dependencies without prior discussion and approval.
- All code must be tested.
```

## File: .agents/RULES.md
```markdown
# 📜 Rules

This document outlines the rules and guidelines for the Show Up Crawler project.

1.  **Adhere to the `AGENT.md` guide**: All development must follow the instructions in `.agents/AGENT.md`.
2.  **Respect `robots.txt`**: The crawler must respect the `robots.txt` file of the websites it crawls.
3.  **Set a reasonable crawl rate**: Do not overload the servers of the target websites. Implement a download delay and other throttling settings in Scrapy.
4.  **Use a proper User-Agent**: The crawler should identify itself with a clear User-Agent string (e.g., `ShowUpCrawler/1.0`).
5.  **Handle errors gracefully**: The crawler should be resilient to errors and handle them gracefully (e.g., by logging them and continuing).
6.  **Write clean and maintainable code**: Follow the code style and conventions defined in `.agents/PLANNING.md`.
7.  **Keep documentation up-to-date**: Ensure that the `README.md` and `.agents` files are always in sync with the codebase.
```

## File: .agents/TASKS.md
```markdown
# ✅ Tasks

This file tracks the tasks for the Show Up Crawler project.

## 📅 2025-07-15

- **[DONE]** Create the initial `.agents` files.
- **[TODO]** Develop a Scrapy spider to crawl `lu.ma` for crypto events in Buenos Aires.
- **[TODO]** Define the data structure (Scrapy Item) for the event information.
- **[TODO]** Implement a pipeline to store the scraped data in a JSON file.
- **[TODO]** Add basic tests for the crawler.

## 💡 Discovered During Work

- *No issues discovered yet.*
```

## File: main.py
```python
def main():
    print("Hello from show-up-crawler!")


if __name__ == "__main__":
    main()
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
]
```
