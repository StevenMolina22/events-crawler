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
