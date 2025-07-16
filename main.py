from datetime import date
from dotenv import load_dotenv
from firecrawl import FirecrawlApp, JsonConfig
from pydantic import BaseModel
import os

load_dotenv()

assert os.getenv("FIRECRAWL_API_KEY")
app = FirecrawlApp(os.getenv("FIRECRAWL_API_KEY"))


class EventSchema(BaseModel):
    data: date
    name: str
    organizer: str
    location: str
    image: str

json_config = JsonConfig(
    schema=EventSchema
)

def main():
    print("Hello from show-up-crawler!")
    # scrape_result = app.scrape_url('lu.ma/crypto', formats=['markdown', 'html'])

    llm_extraction_result = app.scrape_url(
        'lu.ma/crypto',
        formats=["json"],
        json_options=json_config,
        only_main_content=True,
        timeout=60000
    )

    print(llm_extraction_result.json)


if __name__ == "__main__":
    main()
