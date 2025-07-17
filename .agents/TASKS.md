# ✅ Tasks

This file tracks the tasks for the Show Up Crawler project.

## 📅 2025-01-15

- **[DONE]** Create a new Raw HTML Pipeline to save complete unfiltered HTML.
  - **[DONE]** Update `show_up/items.py` to include `raw_html` field.
  - **[DONE]** Modify `show_up/spiders/luma.py` to capture complete HTML response.
  - **[DONE]** Create `RawHtmlFilePipeline` in `show_up/pipelines.py`.
  - **[DONE]** Update `show_up/settings.py` to enable the new raw HTML pipeline.
  - **[DONE]** Add comprehensive tests for the raw HTML pipeline functionality.
  - **[DONE]** Verify pipeline works with live spider execution.

## 📅 2025-07-16

- **[DONE]** Create a new Scrapy pipeline to save the raw HTML of the event's main content.
  - **[DONE]** Update `show_up/items.py` to include `html_content` field.
  - **[DONE]** Modify `show_up/spiders/luma.py` to extract the main content HTML.
  - **[DONE]** Create `show_up/pipelines.py` with `HtmlFilePipeline`.
  - **[DONE]** Update `show_up/settings.py` to enable the new pipeline.

## 📅 2025-07-15

- **[DONE]** Create the initial `.agents` files.
- **[IN PROGRESS]** Develop a Scrapy spider to crawl `lu.ma` for crypto events.
  - **[DONE]** Define the data structure (Scrapy Item) for the event information.
  - **[DONE]** Implement the spider logic to extract event data.
  - **[DONE]** Implement a pipeline to store the scraped data in a JSON file.
  - **[TODO]** Add basic tests for the crawler.

## 💡 Discovered During Work

- *No issues discovered yet.*