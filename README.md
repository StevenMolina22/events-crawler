# Show Up Crawler

Show Up Crawler is a web crawler that extracts information about crypto-related events happening in Buenos Aires from various event websites. The initial focus is on `lu.ma`.

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

- Python 3.13+
- `uv` installed (`pip install uv`)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone <repository_url>
    cd show-up-crawler
    ```

2.  **Install dependencies:**
    This project uses `uv` to manage dependencies.
    ```sh
    uv sync
    ```

3.  **Set up environment variables:**
    Create a `.env.local` file in the project root and add your Firecrawl API key:
    ```env
    FIRECRAWL_API_KEY="your_firecrawl_api_key"
    ```

## 🏃‍♀️ Usage

To run the crawler, execute the `main.py` script:

```sh
uv run python main.py
```

The crawler will scrape `lu.ma/crypto` and save the extracted event data to `events.json`.

## 🏗️ Project Structure

- `main.py`: The main entry point for the application.
- `scraper.py`: Contains the web scraping logic.
- `schemas.py`: Defines the Pydantic data models for the event data.
- `events.json`: The output file where the scraped event data is stored.
- `pyproject.toml`: Defines project metadata and dependencies.