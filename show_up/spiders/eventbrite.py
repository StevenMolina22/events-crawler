import scrapy
import json

HTML_FILE = "res_eventbrite.html"


class EventbriteSpider(scrapy.Spider):
    name = "eventbrite"
    allowed_domains = ["eventbrite.com.ar"]
    start_urls = ["https://www.eventbrite.com.ar/d/argentina--buenos-aires/tech/"]

    def extract_json_ld(self, response):
            """Helper function to extract and parse JSON-LD data"""
            json_ld_scripts = response.css('script[type="application/ld+json"]::text').getall()
            parsed_data = []

            for script in json_ld_scripts:
                try:
                    data = json.loads(script.strip())
                    parsed_data.append(data)
                except json.JSONDecodeError:
                    continue

            return parsed_data



    def parse(self, response):
        scripts = response.css('script::text').getall()

        with open("debug_scripts.jsonl", "a", encoding="utf-8") as debug_file:
            for idx, script in enumerate(scripts):
                if '"itemListElement"' in script:
                    try:
                        data = json.loads(script.strip())

                        # ✅ Save full JSON for raw debugging
                        debug_file.write(json.dumps(data, ensure_ascii=False) + "\n")

                        # ✅ Yield full raw data for structured archiving
                        yield {"raw_schema_org": data}

                        # ✅ Also yield each event inside the itemListElement
                        item_list = data.get("itemListElement", [])
                        for item in item_list:
                            item_data = item.get("item", {})
                            if isinstance(item_data, dict):
                                yield item_data
                            else:
                                self.logger.warning(f"item['item'] is not a dict in script #{idx}")

                    except json.JSONDecodeError:
                        self.logger.warning(f"❌ Could not parse JSON in script #{idx}")
