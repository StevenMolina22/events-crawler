import json
import os
from datetime import datetime
from typing import Dict, List, Any

OUTPUT_FILE = "output/events.json"

class JsonPipeline:
    """Simple pipeline for storing scraped items as JSON."""

    def __init__(self, output_file: str = OUTPUT_FILE):
        self.output_file = output_file
        self.items: List[Dict[str, Any]] = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            output_file=crawler.settings.get("JSON_OUTPUT_FILE", OUTPUT_FILE)
        )

    def open_spider(self, spider):
        spider.logger.info(f"JsonPipeline writing to: {self.output_file}")

    def close_spider(self, spider):
        # Create output directory if needed
        output_dir = os.path.dirname(self.output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Write events to JSON file
        output = {
            "events": self.items,
            "count": len(self.items),
            "scraped_at": datetime.now().isoformat()
        }

        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        spider.logger.info(f"Saved {len(self.items)} events to {self.output_file}")

    def process_item(self, item, spider):
        # Convert item to dict and add to items list
        item_dict = dict(item)
        self.items.append(item_dict)
        return item
