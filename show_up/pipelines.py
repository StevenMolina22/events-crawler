import json
import os
from datetime import datetime
from typing import Dict, List, Any
from show_up.db import get_db

OUTPUT_FILE = "output/events.json"


class JsonPipeline:
    """Simple pipeline for storing scraped items as JSON."""

    def __init__(self, output_file: str = OUTPUT_FILE):
        self.output_file = output_file
        self.items: List[Dict[str, Any]] = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(output_file=crawler.settings.get("JSON_OUTPUT_FILE", OUTPUT_FILE))

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
            "scraped_at": datetime.now().isoformat(),
        }

        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        spider.logger.info(f"Saved {len(self.items)} events to {self.output_file}")

    def process_item(self, item, spider):
        # Convert item to dict and add to items list
        item_dict = dict(item)
        self.items.append(item_dict)
        return item


class MongoDBPipeline:
    """Pipeline for storing scraped items in MongoDB."""

    def open_spider(self, spider):
        self.collection = get_db()["events"]
        # Create unique index on "url" if it doesn't exist
        self.collection.create_index("url", unique=True, background=True)

    def process_item(self, item, spider):
        self.collection.update_one(
            {"url": item["url"]}, {"$set": dict(item)}, upsert=True
        )
        return item
