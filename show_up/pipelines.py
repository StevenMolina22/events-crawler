import json
import os
import re
from datetime import datetime
from typing import Optional, Dict, List, Any
from show_up.utils.validation import validate_event_data, clean_event_data, get_data_completeness_score


class EnhancedJsonPipeline:
    """
    Pipeline for storing scraped items in a structured JSON file with metadata.

    This pipeline provides several improvements over the legacy JsonWriterPipeline:
    - Stores events in a properly structured JSON array with metadata
    - Configurable output file path and formatting options
    - Comprehensive error handling and logging
    - Basic validation of event data

    Configuration settings (in settings.py):
    - JSON_OUTPUT_FILE: Path to the output JSON file (default: 'crypto_events.json')
    - JSON_INDENT: Number of spaces for indentation (default: 2)
    - JSON_ENSURE_ASCII: Whether to escape non-ASCII characters (default: False)
    """

    def __init__(self, output_file: str = 'crypto_events.json', indent: int = 2, ensure_ascii: bool = False):
        self.output_file = output_file
        self.indent = indent
        self.ensure_ascii = ensure_ascii
        self.items: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self.extraction_stats: Dict[str, int] = {
            'total_processed': 0,
            'json_extraction': 0,
            'html_extraction': 0,
            'fallback_extraction': 0,
            'validation_errors': 0,
            'high_quality_events': 0
        }

    @classmethod
    def from_crawler(cls, crawler):
        # Get settings from crawler
        output_file = crawler.settings.get('JSON_OUTPUT_FILE', 'crypto_events.json')
        indent = crawler.settings.getint('JSON_INDENT', 2)
        ensure_ascii = crawler.settings.getbool('JSON_ENSURE_ASCII', False)
        pipeline = cls(output_file=output_file, indent=indent, ensure_ascii=ensure_ascii)

        # Store settings reference for configuration
        pipeline.settings = crawler.settings
        return pipeline

    def open_spider(self, spider):
        # Initialize metadata
        self.metadata = {
            'spider_name': spider.name,
            'start_time': datetime.now().isoformat(),
            'source': spider.start_urls[0] if spider.start_urls else None,
            'extraction_config': {
                'json_extraction_enabled': getattr(self, 'settings', {}).get('JSON_EXTRACTION_ENABLED', True),
                'validation_enabled': getattr(self, 'settings', {}).get('ENHANCED_JSON_VALIDATION', True),
                'include_metadata': getattr(self, 'settings', {}).get('ENHANCED_JSON_INCLUDE_METADATA', True),
                'extraction_stats': getattr(self, 'settings', {}).get('ENHANCED_JSON_EXTRACTION_STATS', True)
            }
        }
        spider.logger.info(f"EnhancedJsonPipeline initialized. Output file: {self.output_file}")
        spider.logger.info(f"Extraction configuration: {self.metadata['extraction_config']}")

    def close_spider(self, spider):
        # Add extraction statistics to metadata
        if getattr(self, 'settings', {}).get('ENHANCED_JSON_EXTRACTION_STATS', True):
            self.metadata['extraction_statistics'] = self.extraction_stats.copy()

            # Calculate success rates
            total = self.extraction_stats['total_processed']
            if total > 0:
                self.metadata['extraction_statistics']['success_rates'] = {
                    'json_extraction_rate': self.extraction_stats['json_extraction'] / total,
                    'html_extraction_rate': self.extraction_stats['html_extraction'] / total,
                    'fallback_rate': self.extraction_stats['fallback_extraction'] / total,
                    'validation_success_rate': 1 - (self.extraction_stats['validation_errors'] / total),
                    'high_quality_rate': self.extraction_stats['high_quality_events'] / total
                }

        # Create the final JSON structure
        output = {
            'metadata': self.metadata,
            'events': self.items,
            'end_time': datetime.now().isoformat(),
            'event_count': len(self.items),
        }

        try:
            # Ensure the directory exists
            output_dir = os.path.dirname(self.output_file)
            if output_dir and not os.path.exists(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    spider.logger.info(f"Created directory: {output_dir}")
                except OSError as e:
                    spider.logger.error(f"Failed to create directory {output_dir}: {e}")
                    # Try to use current directory as fallback
                    self.output_file = os.path.basename(self.output_file)
                    spider.logger.warning(f"Falling back to current directory: {self.output_file}")

            # Write the JSON file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=self.indent, ensure_ascii=self.ensure_ascii)
            spider.logger.info(f"Successfully wrote {len(self.items)} events to {self.output_file}")
        except PermissionError:
            spider.logger.error(f"Permission denied when writing to {self.output_file}")
        except IsADirectoryError:
            spider.logger.error(f"Cannot write to {self.output_file} because it is a directory")
        except FileNotFoundError:
            spider.logger.error(f"Directory for {self.output_file} does not exist and could not be created")
        except Exception as e:
            spider.logger.error(f"Failed to write JSON file: {e}")

    def process_item(self, item, spider):
        try:
            # Update extraction statistics
            self.extraction_stats['total_processed'] += 1

            # Create a copy of the item and remove HTML fields
            item_copy = dict(item)
            html_content = item_copy.pop('html_content', None)
            raw_html = item_copy.pop('raw_html', None)

            # Track extraction method
            extraction_method = item_copy.get('extraction_method', 'unknown')
            if extraction_method == 'json':
                self.extraction_stats['json_extraction'] += 1
            elif extraction_method == 'html_fallback':
                self.extraction_stats['html_extraction'] += 1
            elif extraction_method == 'fallback':
                self.extraction_stats['fallback_extraction'] += 1

            # Validate and clean data if enabled
            if getattr(self, 'settings', {}).get('ENHANCED_JSON_VALIDATION', True):
                try:
                    item_copy = validate_event_data(item_copy)
                    item_copy = clean_event_data(item_copy)

                    # Calculate data quality score
                    completeness_score = get_data_completeness_score(item_copy)
                    if completeness_score > 0.7:  # High quality threshold
                        self.extraction_stats['high_quality_events'] += 1

                    # Add quality metadata if configured
                    if getattr(self, 'settings', {}).get('ENHANCED_JSON_INCLUDE_METADATA', True):
                        item_copy['_metadata'] = {
                            'extraction_method': extraction_method,
                            'completeness_score': completeness_score,
                            'processed_at': datetime.now().isoformat()
                        }

                except Exception as e:
                    spider.logger.warning(f"Data validation failed: {e}")
                    self.extraction_stats['validation_errors'] += 1
                    # Continue with unvalidated data

            # Ensure required fields are present
            required_fields = ['title', 'url']
            for field in required_fields:
                if field not in item_copy or not item_copy[field]:
                    spider.logger.warning(f"Item missing required field: {field}")
                    # Provide default values for required fields
                    if field == 'title':
                        item_copy[field] = f"Untitled Event ({datetime.now().isoformat()})"
                    elif field == 'url':
                        item_copy[field] = "unknown_url"

            # Ensure all standard fields have values (even if empty)
            standard_fields = [
                'date', 'end_date', 'timezone', 'location', 'full_address',
                'city', 'country', 'coordinates', 'place_id', 'event_type',
                'visibility', 'api_id', 'cover_url', 'organizer', 'guest_count',
                'description'
            ]

            for field in standard_fields:
                if field not in item_copy:
                    item_copy[field] = None
                    spider.logger.debug(f"Added missing field with null value: {field}")

            # Test JSON serialization to catch any issues early
            try:
                json.dumps(item_copy)
            except (TypeError, OverflowError) as e:
                spider.logger.warning(f"Item contains non-serializable values: {e}")
                # Attempt to fix non-serializable values
                for key, value in list(item_copy.items()):
                    try:
                        json.dumps({key: value})
                    except (TypeError, OverflowError):
                        spider.logger.warning(f"Converting non-serializable value in field '{key}' to string")
                        item_copy[key] = str(value)

            # Add to items list
            self.items.append(item_copy)

            # Log successful processing
            spider.logger.info(f"Successfully processed item: {item_copy.get('title', 'Unknown')} "
                             f"(method: {extraction_method})")

        except Exception as e:
            spider.logger.error(f"Error processing item in EnhancedJsonPipeline: {e}")
            self.extraction_stats['validation_errors'] += 1

        return item


# Legacy pipeline kept for backward compatibility
class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('crypto_events.json', 'w')
        spider.logger.warning("Using deprecated JsonWriterPipeline. Consider switching to EnhancedJsonPipeline.")

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
        if 'html_content' in item and 'title' in item and item['html_content'] is not None:
            title = item['title']
            # Sanitize the title to create a valid filename
            filename = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
            filepath = os.path.join(self.output_dir, f"{filename}.html")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(item['html_content'])
        else:
            spider.logger.warning(f"Skipping HTML file creation for item: {item['title']} - html_content is None")
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
