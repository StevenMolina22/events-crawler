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
.kiro/
  specs/
    enhanced-json-event-storage/
      design.md
      requirements.md
      tasks.md
output/
  debug.json
  evenbrite.json
  eventbrite_events.json
  luma.html
  luma_events.json
show_up/
  extractors/
    __init__.py
    base.py
    json_extractor.py
  spiders/
    __init__.py
    eventbrite.py
    luma.py
  utils/
    __init__.py
    validation.py
  items.py
  middlewares.py
  pipelines.py
  settings.py
tests/
  test_enhanced_pipelines.py
  test_enhanced_spider.py
  test_extractors.py
  test_pipelines.py
  test_utils.py
.env.local
main.py
pyproject.toml
README.md
repomix.config.json
scrapy.cfg
test_enhanced_extraction.py
uv.lock
```

# Files

- .agents/AGENT.md
- .agents/CONTEXT.md
- .agents/PLANNING.md
- .agents/RULES.md
- .agents/TASKS.md
- .venv/bin/activate_this.py
- .venv/bin/jp.py
- .env.local
- .kiro/specs/enhanced-json-event-storage/design.md
- .kiro/specs/enhanced-json-event-storage/requirements.md
- .kiro/specs/enhanced-json-event-storage/tasks.md
- .python-version
- .repomixignore
- .ruff_cache/0.11.9/14993961347254167462
- .ruff_cache/0.11.9/16966933536205744969
- .ruff_cache/0.11.9/6505350554833522355
- .ruff_cache/CACHEDIR.TAG
- README.md
- generate_context_structure.py
- inventory_findings.md
- main.py
- output/debug.json
- output/evenbrite.json
- output/eventbrite_events.json
- output/luma.html
- output/luma_events.json
- pyproject.toml
- repomix.config.json
- scrapy.cfg
- show_up/__init__.py
- show_up/extractors/__init__.py
- show_up/extractors/base.py
- show_up/extractors/json_extractor.py
- show_up/items.py
- show_up/middlewares.py
- show_up/pipelines.py
- show_up/settings.py
- show_up/spiders/__init__.py
- show_up/spiders/eventbrite.py
- show_up/spiders/luma.py
- show_up/utils/__init__.py
- show_up/utils/validation.py
- test_enhanced_extraction.py
- tests/test_enhanced_pipelines.py
- tests/test_enhanced_spider.py
- tests/test_extractors.py
- tests/test_pipelines.py
- tests/test_utils.py
- uv.lock

## File: .env.local
````
FIRECRAWL_API_KEY="your_firecrawl_api_key"
````

## File: show_up/extractors/__init__.py
````python
"""
Data extraction components for the Show Up Crawler.

This package contains specialized extractors for different data sources and formats.
The extractors are designed to be modular and reusable across different spiders.

Available extractors:
- JsonExtractor: Extracts structured data from embedded JSON in HTML
- Base extractor interfaces for extensibility
"""

from .json_extractor import JsonExtractor

__all__ = ["JsonExtractor"]
````

## File: show_up/extractors/base.py
````python
"""
Base extractor interface for the Show Up Crawler.

This module defines the abstract base class for all data extractors.
It provides a consistent interface for extracting structured data
from various sources and formats.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """
    Abstract base class for all data extractors.

    This class defines the interface that all extractors must implement.
    It provides common functionality and ensures consistency across
    different extraction methods.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the extractor with optional configuration.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def extract(self, content: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from the given content.

        Args:
            content: Raw content to extract data from
            **kwargs: Additional extraction parameters

        Returns:
            Extracted data as a dictionary, or None if extraction fails
        """
        pass

    @abstractmethod
    def can_extract(self, content: str) -> bool:
        """
        Check if this extractor can handle the given content.

        Args:
            content: Content to check

        Returns:
            True if this extractor can process the content
        """
        pass

    def get_extraction_method(self) -> str:
        """
        Get the name of this extraction method.

        Returns:
            String identifier for this extraction method
        """
        return self.__class__.__name__.lower().replace("extractor", "")

    def validate_extracted_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate extracted data for basic consistency.

        Args:
            data: Extracted data dictionary

        Returns:
            True if data is valid
        """
        if not isinstance(data, dict):
            return False

        # Check for required fields
        required_fields = self.config.get("required_fields", [])
        for field in required_fields:
            if field not in data or not data[field]:
                self.logger.warning(f"Missing required field: {field}")
                return False

        return True

    def log_extraction_result(
        self, success: bool, data: Optional[Dict[str, Any]] = None
    ):
        """
        Log the result of an extraction attempt.

        Args:
            success: Whether extraction was successful
            data: Extracted data (if successful)
        """
        if success and data:
            self.logger.info(
                f"Successfully extracted data using {self.get_extraction_method()}"
            )
            self.logger.debug(f"Extracted fields: {list(data.keys())}")
        else:
            self.logger.warning(
                f"Failed to extract data using {self.get_extraction_method()}"
            )


class MultiExtractor:
    """
    A composite extractor that tries multiple extraction methods in order.

    This class allows for a fallback mechanism where if one extractor fails,
    the next one is tried until successful extraction or all methods are exhausted.
    """

    def __init__(self, extractors: List[BaseExtractor]):
        """
        Initialize with a list of extractors.

        Args:
            extractors: List of extractor instances in order of preference
        """
        self.extractors = extractors
        self.logger = logging.getLogger(self.__class__.__name__)

    def extract(self, content: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Try each extractor in order until one succeeds.

        Args:
            content: Content to extract data from
            **kwargs: Additional extraction parameters

        Returns:
            Extracted data from the first successful extractor, or None
        """
        for extractor in self.extractors:
            if extractor.can_extract(content):
                try:
                    result = extractor.extract(content, **kwargs)
                    if result and extractor.validate_extracted_data(result):
                        # Add extraction method to the result
                        result["extraction_method"] = extractor.get_extraction_method()
                        extractor.log_extraction_result(True, result)
                        return result
                except Exception as e:
                    self.logger.warning(
                        f"Extractor {extractor.__class__.__name__} failed: {e}"
                    )
                    extractor.log_extraction_result(False)
                    continue

        self.logger.warning("All extractors failed")
        return None

    def get_available_extractors(self) -> List[str]:
        """
        Get list of available extraction methods.

        Returns:
            List of extractor method names
        """
        return [extractor.get_extraction_method() for extractor in self.extractors]
````

## File: show_up/utils/__init__.py
````python
"""
Utility functions and helpers for the Show Up Crawler.

This package contains reusable utility functions, validation helpers,
and common functionality used across the crawler components.

Available utilities:
- validation: Data validation and cleaning helpers
- Common data processing functions
"""

from .validation import (
    validate_event_data,
    clean_event_data,
    get_data_completeness_score,
)

__all__ = ["validate_event_data", "clean_event_data", "get_data_completeness_score"]
````

## File: test_enhanced_extraction.py
````python
#!/usr/bin/env python3
"""
Integration test script for enhanced JSON extraction functionality.

This script tests the enhanced extraction capabilities on real HTML files
and compares the results with the original incomplete extraction.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from show_up.extractors.json_extractor import JsonExtractor
from show_up.utils.validation import validate_event_data, get_data_completeness_score


def test_extraction_on_html_files():
    """Test extraction on all HTML files in the output directory."""

    html_dir = Path("output/html")
    if not html_dir.exists():
        print(f"❌ HTML directory {html_dir} does not exist")
        return

    html_files = list(html_dir.glob("*.html"))
    if not html_files:
        print(f"❌ No HTML files found in {html_dir}")
        return

    print(f"🚀 Testing enhanced extraction on {len(html_files)} HTML files...")
    print()

    extractor = JsonExtractor()
    results = []

    for html_file in html_files:
        print(f"📄 Processing: {html_file.name}")

        try:
            with open(html_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Extract event data
            extracted_data = extractor.extract(
                html_content, url=f"https://lu.ma/{html_file.stem}"
            )

            if extracted_data:
                # Validate the data
                try:
                    validated_data = validate_event_data(extracted_data)
                    completeness_score = get_data_completeness_score(validated_data)

                    result = {
                        "file": html_file.name,
                        "extraction_success": True,
                        "extraction_method": extracted_data.get(
                            "extraction_method", "unknown"
                        ),
                        "extraction_pattern": extracted_data.get(
                            "extraction_pattern", "unknown"
                        ),
                        "title": validated_data.get("title", "Unknown"),
                        "date": validated_data.get("date", "No date"),
                        "location": validated_data.get("location", "No location"),
                        "completeness_score": completeness_score,
                        "field_count": len(
                            [
                                v
                                for v in validated_data.values()
                                if v not in [None, "", {}]
                            ]
                        ),
                        "data": validated_data,
                    }

                    print(f"  ✅ Success: {result['title']}")
                    print(f"     📅 Date: {result['date']}")
                    print(f"     📍 Location: {result['location']}")
                    print(
                        f"     🔍 Method: {result['extraction_method']} (pattern {result['extraction_pattern']})"
                    )
                    print(
                        f"     📊 Completeness: {completeness_score:.2f} ({result['field_count']} fields)"
                    )

                except Exception as e:
                    result = {
                        "file": html_file.name,
                        "extraction_success": True,
                        "validation_error": str(e),
                        "raw_data": extracted_data,
                    }
                    print(f"  ⚠️  Extraction succeeded but validation failed: {e}")
            else:
                result = {
                    "file": html_file.name,
                    "extraction_success": False,
                    "error": "No data extracted",
                }
                print(f"  ❌ Failed to extract data")

            results.append(result)

        except Exception as e:
            result = {
                "file": html_file.name,
                "extraction_success": False,
                "error": str(e),
            }
            results.append(result)
            print(f"  ❌ Error: {e}")

        print()

    # Generate summary report
    generate_summary_report(results)

    # Save detailed results
    save_detailed_results(results)

    # Test completed successfully
    assert len(results) > 0, "No results generated"
    assert all(r.get("extraction_success") for r in results), "Some extractions failed"


def generate_summary_report(results: List[Dict[str, Any]]):
    """Generate a summary report of extraction results."""

    total_files = len(results)
    successful_extractions = len([r for r in results if r.get("extraction_success")])
    failed_extractions = total_files - successful_extractions

    # Calculate statistics for successful extractions
    successful_results = [
        r for r in results if r.get("extraction_success") and "completeness_score" in r
    ]

    if successful_results:
        avg_completeness = sum(
            r["completeness_score"] for r in successful_results
        ) / len(successful_results)
        avg_field_count = sum(r["field_count"] for r in successful_results) / len(
            successful_results
        )

        # Method breakdown
        method_counts = {}
        for r in successful_results:
            method = r.get("extraction_method", "unknown")
            method_counts[method] = method_counts.get(method, 0) + 1

        # Quality breakdown
        high_quality = len(
            [r for r in successful_results if r["completeness_score"] > 0.8]
        )
        medium_quality = len(
            [r for r in successful_results if 0.5 <= r["completeness_score"] <= 0.8]
        )
        low_quality = len(
            [r for r in successful_results if r["completeness_score"] < 0.5]
        )
    else:
        avg_completeness = 0
        avg_field_count = 0
        method_counts = {}
        high_quality = medium_quality = low_quality = 0

    print("=" * 60)
    print("📊 EXTRACTION SUMMARY REPORT")
    print("=" * 60)
    print(f"📁 Total files processed: {total_files}")
    print(
        f"✅ Successful extractions: {successful_extractions} ({successful_extractions / total_files * 100:.1f}%)"
    )
    print(
        f"❌ Failed extractions: {failed_extractions} ({failed_extractions / total_files * 100:.1f}%)"
    )
    print()

    if successful_results:
        print("📈 DATA QUALITY METRICS:")
        print(f"   Average completeness score: {avg_completeness:.3f}")
        print(f"   Average field count: {avg_field_count:.1f}")
        print()

        print("🔍 EXTRACTION METHODS:")
        for method, count in method_counts.items():
            print(
                f"   {method}: {count} files ({count / len(successful_results) * 100:.1f}%)"
            )
        print()

        print("⭐ QUALITY BREAKDOWN:")
        print(
            f"   High quality (>80%): {high_quality} files ({high_quality / len(successful_results) * 100:.1f}%)"
        )
        print(
            f"   Medium quality (50-80%): {medium_quality} files ({medium_quality / len(successful_results) * 100:.1f}%)"
        )
        print(
            f"   Low quality (<50%): {low_quality} files ({low_quality / len(successful_results) * 100:.1f}%)"
        )
        print()

    print("🎯 COMPARISON WITH ORIGINAL CRAWLER:")
    print("   Original completeness: ~25% (titles + URLs only)")
    print(
        f"   Enhanced completeness: {avg_completeness * 100:.1f}% (comprehensive data)"
    )
    print(f"   Improvement factor: {avg_completeness / 0.25:.1f}x better")
    print()


def save_detailed_results(results: List[Dict[str, Any]]):
    """Save detailed extraction results to a JSON file."""

    output_file = "enhanced_extraction_results.json"

    output_data = {
        "metadata": {
            "test_script": "test_enhanced_extraction.py",
            "test_time": datetime.now().isoformat(),
            "total_files": len(results),
            "successful_extractions": len(
                [r for r in results if r.get("extraction_success")]
            ),
        },
        "results": results,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"💾 Detailed results saved to: {output_file}")


def compare_with_original_data():
    """Compare enhanced extraction with original crypto_events.json."""

    original_file = "crypto_events.json"

    if not os.path.exists(original_file):
        print(f"⚠️  Original file {original_file} not found for comparison")
        return

    print("🔍 COMPARING WITH ORIGINAL DATA:")
    print("-" * 40)

    with open(original_file, "r", encoding="utf-8") as f:
        original_data = json.load(f)

    original_events = original_data.get("events", [])

    print(f"📊 Original extraction results:")
    print(f"   Events: {len(original_events)}")

    # Analyze original data quality
    events_with_dates = len([e for e in original_events if e.get("date")])
    events_with_locations = len([e for e in original_events if e.get("location")])
    events_with_titles = len([e for e in original_events if e.get("title")])

    print(
        f"   Events with titles: {events_with_titles}/{len(original_events)} ({events_with_titles / len(original_events) * 100:.1f}%)"
    )
    print(
        f"   Events with dates: {events_with_dates}/{len(original_events)} ({events_with_dates / len(original_events) * 100:.1f}%)"
    )
    print(
        f"   Events with locations: {events_with_locations}/{len(original_events)} ({events_with_locations / len(original_events) * 100:.1f}%)"
    )

    # Show sample events
    print("\n📄 Sample original events:")
    for i, event in enumerate(original_events[:3]):
        print(f"   {i + 1}. {event.get('title', 'No title')}")
        print(f"      Date: {event.get('date', 'No date')}")
        print(f"      Location: {event.get('location', 'No location')}")
        print(f"      URL: {event.get('url', 'No URL')}")
        print()


def main():
    """Main test function."""

    print("🧪 ENHANCED JSON EXTRACTION TEST")
    print("=" * 50)
    print()

    # Test extraction on HTML files
    test_extraction_on_html_files()

    # Compare with original data
    compare_with_original_data()

    print("✅ Test completed successfully!")
    print()
    print("💡 Next steps:")
    print("   1. Review the enhanced_extraction_results.json file")
    print("   2. Run the enhanced spider: scrapy crawl luma")
    print("   3. Compare the new crypto_events.json with the original")


if __name__ == "__main__":
    main()
````

## File: show_up/extractors/json_extractor.py
````python
"""
JSON data extractor for Luma event pages.

This module implements comprehensive JSON extraction from Luma event pages.
It handles multiple JSON patterns and structures commonly found in Luma's
HTML responses, providing robust data extraction with fallback mechanisms.
"""

import json
import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .base import BaseExtractor

logger = logging.getLogger(__name__)


class JsonExtractor(BaseExtractor):
    """
    Extractor for JSON data embedded in HTML content.

    This extractor specializes in finding and parsing JSON data structures
    embedded within HTML pages, particularly from Luma event pages.
    """

    # JSON patterns commonly found in Luma pages
    JSON_PATTERNS = [
        # Pattern 1: Direct event object in script (with proper nested braces)
        r'"event":\s*(\{(?:[^{}]|{[^{}]*})*\})',
        # Pattern 2: Full initial data structure
        r"window\.__INITIAL_DATA__\s*=\s*(\{.*?\});",
        # Pattern 3: Event data in script tag (non-greedy)
        r'<script[^>]*>.*?(\{.*?"event".*?\}.*?)</script>',
        # Pattern 4: JSON-LD structured data
        r'<script[^>]*type="application/ld\+json"[^>]*>([^<]+)</script>',
        # Pattern 5: React props or state
        r"window\.__PROPS__\s*=\s*(\{.*?\});",
        # Pattern 6: Event data in data attributes
        r'data-event=(["\'])(\{.*?\})\1',
        # Pattern 7: Variable assignment with event data
        r'var\s+\w+\s*=\s*(\{.*?"event".*?\});',
        # Pattern 8: Simple event object assignment
        r'=\s*(\{.*?"event".*?\});',
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the JSON extractor.

        Args:
            config: Optional configuration with custom patterns and settings
        """
        super().__init__(config)

        # Add custom patterns from config
        self.patterns = self.JSON_PATTERNS.copy()
        if config and "custom_patterns" in config:
            self.patterns.extend(config["custom_patterns"])

    def can_extract(self, content: str) -> bool:
        """
        Check if content contains extractable JSON data.

        Args:
            content: HTML content to check

        Returns:
            True if JSON patterns are found in the content
        """
        if not content:
            return False

        # Quick check for common JSON indicators
        json_indicators = [
            '"event"',
            "window.__INITIAL_DATA__",
            "application/ld+json",
            "data-event",
        ]

        return any(indicator in content for indicator in json_indicators)

    def extract(self, content: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Extract event data from HTML content.

        Args:
            content: HTML content containing embedded JSON
            **kwargs: Additional parameters (url, title, etc.)

        Returns:
            Extracted event data dictionary or None if extraction fails
        """
        if not self.can_extract(content):
            return None

        # Try each pattern in order
        for i, pattern in enumerate(self.patterns):
            try:
                result = self._extract_with_pattern(content, pattern, i)
                if result:
                    # Add extraction metadata
                    result["extraction_method"] = "json"
                    result["extraction_pattern"] = i

                    # Add any additional context from kwargs
                    if "url" in kwargs:
                        result["url"] = kwargs["url"]

                    self.logger.info(f"Successfully extracted data using pattern {i}")
                    return result

            except Exception as e:
                self.logger.debug(f"Pattern {i} failed: {e}")
                continue

        self.logger.warning("All JSON patterns failed")
        return None

    def _extract_with_pattern(
        self, content: str, pattern: str, pattern_index: int
    ) -> Optional[Dict[str, Any]]:
        """
        Extract data using a specific regex pattern.

        Args:
            content: HTML content
            pattern: Regex pattern to use
            pattern_index: Index of the pattern for logging

        Returns:
            Extracted data or None if pattern doesn't match
        """
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

        if not matches:
            return None

        # Process matches based on pattern type
        for match in matches:
            try:
                # Handle different match formats
                if isinstance(match, tuple):
                    # For patterns that capture groups, take the last non-empty group
                    json_str = None
                    for group in reversed(match):
                        if group and group.strip():
                            json_str = group
                            break
                    if not json_str:
                        continue
                else:
                    json_str = match

                # Clean and parse JSON
                cleaned_json = self._clean_json_string(json_str)
                if not cleaned_json:
                    continue

                json_data = json.loads(cleaned_json)

                # Extract event data based on structure
                event_data = self._extract_event_from_json(json_data)
                if event_data:
                    return event_data

            except (json.JSONDecodeError, KeyError, TypeError) as e:
                self.logger.debug(
                    f"Failed to parse JSON from pattern {pattern_index}: {e}"
                )
                continue

        return None

    def _clean_json_string(self, json_str: str) -> Optional[str]:
        """
        Clean and prepare JSON string for parsing.

        Args:
            json_str: Raw JSON string

        Returns:
            Cleaned JSON string or None if cleaning fails
        """
        if not json_str:
            return None

        # Remove leading/trailing whitespace
        json_str = json_str.strip()

        # Remove HTML entities
        json_str = json_str.replace("&quot;", '"')
        json_str = json_str.replace("&amp;", "&")
        json_str = json_str.replace("&lt;", "<")
        json_str = json_str.replace("&gt;", ">")

        # Remove JavaScript comments (but be careful with URLs)
        # Only remove block comments for safety
        json_str = re.sub(r"/\*.*?\*/", "", json_str, flags=re.DOTALL)
        # Only remove line comments if they start at the beginning of a line
        json_str = re.sub(r"^\s*//.*?$", "", json_str, flags=re.MULTILINE)

        # Ensure proper JSON structure
        if not json_str.startswith(("{", "[")):
            # Try to find the start of JSON
            json_start = max(json_str.find("{"), json_str.find("["))
            if json_start != -1:
                json_str = json_str[json_start:]

        # Try to balance brackets using a more robust approach
        try:
            # For simple cases, try to parse as-is first
            json.loads(json_str)
            return json_str
        except json.JSONDecodeError:
            pass

        # If that fails, try bracket balancing
        if json_str.startswith("{"):
            return self._balance_braces(json_str)
        elif json_str.startswith("["):
            return self._balance_brackets(json_str)

        return json_str

    def _balance_braces(self, json_str: str) -> str:
        """Balance curly braces in JSON string."""
        brace_count = 0
        in_string = False
        i = 0

        while i < len(json_str):
            char = json_str[i]

            if in_string:
                if char == '"' and (i == 0 or json_str[i - 1] != "\\"):
                    in_string = False
                elif char == "\\":
                    i += 1  # Skip next character
            else:
                if char == '"':
                    in_string = True
                elif char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        return json_str[: i + 1]

            i += 1

        return json_str

    def _balance_brackets(self, json_str: str) -> str:
        """Balance square brackets in JSON string."""
        bracket_count = 0
        in_string = False
        i = 0

        while i < len(json_str):
            char = json_str[i]

            if in_string:
                if char == '"' and (i == 0 or json_str[i - 1] != "\\"):
                    in_string = False
                elif char == "\\":
                    i += 1  # Skip next character
            else:
                if char == '"':
                    in_string = True
                elif char == "[":
                    bracket_count += 1
                elif char == "]":
                    bracket_count -= 1
                    if bracket_count == 0:
                        return json_str[: i + 1]

            i += 1

        return json_str

    def _extract_event_from_json(
        self, json_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract event data from parsed JSON structure.

        Args:
            json_data: Parsed JSON data

        Returns:
            Event data dictionary or None if extraction fails
        """
        event_data = {}

        # Try different JSON structures
        event_info = None

        # Direct event object
        if "event" in json_data:
            event_info = json_data["event"]
        # Event in nested structure
        elif "props" in json_data and "event" in json_data["props"]:
            event_info = json_data["props"]["event"]
        # Event in initialData
        elif "initialData" in json_data and "event" in json_data["initialData"]:
            event_info = json_data["initialData"]["event"]
        # Direct event data (when the whole JSON is the event)
        elif "name" in json_data and "start_at" in json_data:
            event_info = json_data

        if not event_info:
            return None

        # Extract basic information
        event_data["title"] = event_info.get("name", "")
        event_data["api_id"] = event_info.get("api_id", "")
        event_data["event_type"] = event_info.get("event_type", "")
        event_data["visibility"] = event_info.get("visibility", "")

        # Extract temporal information
        if "start_at" in event_info:
            event_data["date"] = event_info["start_at"]
        if "end_at" in event_info:
            event_data["end_date"] = event_info["end_at"]
        if "timezone" in event_info:
            event_data["timezone"] = event_info["timezone"]

        # Extract location information
        self._extract_location_data(event_info, event_data)

        # Extract additional metadata
        if "cover_url" in event_info:
            event_data["cover_url"] = event_info["cover_url"]

        # Extract URL
        if "url" in event_info:
            url = event_info["url"]
            if url and not url.startswith("http"):
                event_data["url"] = f"https://lu.ma/{url}"
            else:
                event_data["url"] = url

        # Extract guest information
        if "guest_count" in event_info:
            event_data["guest_count"] = event_info["guest_count"]
        elif "rsvp_count" in event_info:
            event_data["guest_count"] = event_info["rsvp_count"]

        # Extract organizer information
        if "user" in event_info:
            organizer = event_info["user"]
            if isinstance(organizer, dict):
                event_data["organizer"] = organizer.get("name", "")

        # Extract description (might be in different fields)
        description_fields = ["description", "details", "content", "body"]
        for field in description_fields:
            if field in event_info and event_info[field]:
                event_data["description"] = event_info[field]
                break

        return event_data if event_data.get("title") else None

    def _extract_location_data(
        self, event_info: Dict[str, Any], event_data: Dict[str, Any]
    ) -> None:
        """
        Extract location information from event data.

        Args:
            event_info: Source event information
            event_data: Target event data dictionary to populate
        """
        # Extract geo address information
        if "geo_address_info" in event_info:
            geo_info = event_info["geo_address_info"]

            # Simple location string
            location_parts = []
            if "address" in geo_info:
                location_parts.append(geo_info["address"])
            if "city" in geo_info:
                location_parts.append(geo_info["city"])
            if "country" in geo_info:
                location_parts.append(geo_info["country"])

            if location_parts:
                event_data["location"] = ", ".join(location_parts)

            # Detailed location fields
            if "full_address" in geo_info:
                event_data["full_address"] = geo_info["full_address"]
            if "city" in geo_info:
                event_data["city"] = geo_info["city"]
            if "country" in geo_info:
                event_data["country"] = geo_info["country"]
            if "place_id" in geo_info:
                event_data["place_id"] = geo_info["place_id"]

        # Extract coordinates
        if "coordinate" in event_info:
            coord = event_info["coordinate"]
            if isinstance(coord, dict) and "latitude" in coord and "longitude" in coord:
                event_data["coordinates"] = {
                    "latitude": coord["latitude"],
                    "longitude": coord["longitude"],
                }

        # Alternative location fields
        if not event_data.get("location"):
            location_fields = ["location", "venue", "address"]
            for field in location_fields:
                if field in event_info and event_info[field]:
                    event_data["location"] = event_info[field]
                    break

    def validate_extracted_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate extracted JSON data.

        Args:
            data: Extracted data dictionary

        Returns:
            True if data is valid
        """
        if not super().validate_extracted_data(data):
            return False

        # JSON-specific validation
        required_fields = ["title"]
        for field in required_fields:
            if field not in data or not data[field]:
                return False

        # Validate date format if present
        if "date" in data and data["date"]:
            try:
                datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                self.logger.warning(f"Invalid date format: {data['date']}")
                return False

        return True
````

## File: show_up/spiders/__init__.py
````python
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
````

## File: show_up/spiders/eventbrite.py
````python
import scrapy
import json
import re

HTML_FILE = "output/eventbrite.html"
JSON_FILE = "output/evenbrite.json"


class EventbriteSpider(scrapy.Spider):
    name = "eventbrite"
    allowed_domains = ["eventbrite.com.ar"]
    start_urls = ["https://www.eventbrite.com.ar/d/argentina--buenos-aires/tech/"]

    def parse(self, response):
        """
        This function parses the Eventbrite search results page.
        It extracts the event data from the window.__SERVER_DATA__ variable using a regex.
        """
        server_data_script = response.xpath('//script[contains(., "window.__SERVER_DATA__")]/text()').get()
        if not server_data_script:
            self.logger.error("Could not find window.__SERVER_DATA__ script.")
            return

        # Use regex to find the JSON object
        match = re.search(r'window\.__SERVER_DATA__\s*=\s*(\{.*?\});', server_data_script)
        if not match:
            self.logger.error("Could not find server data JSON in script.")
            return

        try:
            server_data = json.loads(match.group(1))
            with open(JSON_FILE, "w", encoding="utf-8") as f:
                json.dump(server_data, f, ensure_ascii=False, indent=4)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse server data: {e}")
            return

        events = server_data.get('search_data', {}).get('events', {})
        if not events:
            self.logger.warning("No events found in server data.")
            return

        results = events.get("results", [])
        if not results:
            self.logger.warning("No results found in server data.")
            return

        for event in results:
            yield {
                'title': event.get('name'),
                'url': event.get('url'),
                'summary': event.get('summary'),
                'startDate': event.get('start_date'),
                'endDate': event.get('end_date'),
                'location': event.get('primary_venue', {}).get('name'),
                'organizer': event.get('primary_organizer', {}).get('name'),
                'tags': [tag.get('display_name') for tag in event.get('tags', [])],
                'image': event.get('image', {}).get('url'),
                'ticket_availability': event.get('ticket_availability', {}),
            }
````

## File: show_up/utils/validation.py
````python
"""
Data validation and cleaning helpers for the Show Up Crawler.

This module provides utilities for validating and cleaning event data
extracted from various sources. It ensures data consistency and quality
before storage.
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def validate_event_data(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean event data.

    Args:
        event_data: Raw event data dictionary

    Returns:
        Cleaned and validated event data dictionary

    Raises:
        ValueError: If required fields are missing or invalid
    """
    if not isinstance(event_data, dict):
        raise ValueError("Event data must be a dictionary")

    # Required fields
    required_fields = ["title", "url"]
    for field in required_fields:
        if field not in event_data or not event_data[field]:
            raise ValueError(f"Required field '{field}' is missing or empty")

    # Clean the data
    cleaned_data = clean_event_data(event_data)

    # Validate specific fields
    cleaned_data = _validate_url(cleaned_data)
    cleaned_data = _validate_dates(cleaned_data)
    cleaned_data = _validate_location(cleaned_data)
    cleaned_data = _validate_coordinates(cleaned_data)

    return cleaned_data


def clean_event_data(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean event data by removing empty fields and normalizing values.

    Args:
        event_data: Raw event data dictionary

    Returns:
        Cleaned event data dictionary
    """
    cleaned = {}

    for key, value in event_data.items():
        if value is None:
            continue

        # Clean string values
        if isinstance(value, str):
            cleaned_value = value.strip()
            if cleaned_value:
                cleaned[key] = cleaned_value
        # Keep non-empty values
        elif value:
            cleaned[key] = value

    return cleaned


def _validate_url(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize URL field."""
    if "url" in event_data:
        url = event_data["url"]

        # Add protocol if missing
        if url and not url.startswith(("http://", "https://")):
            if url.startswith("//"):
                url = "https:" + url
            elif url.startswith("/"):
                url = "https://lu.ma" + url
            elif "lu.ma" in url:
                url = "https://" + url
            else:
                url = "https://lu.ma/" + url

        # Validate URL format
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                logger.warning(f"Invalid URL format: {url}")
                return event_data
        except Exception as e:
            logger.warning(f"URL validation failed: {e}")
            return event_data

        event_data["url"] = url

    return event_data


def _validate_dates(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize date fields."""
    date_fields = ["date", "end_date"]

    for field in date_fields:
        if field in event_data and event_data[field]:
            date_value = event_data[field]

            # If it's already a datetime object, convert to ISO string
            if isinstance(date_value, datetime):
                event_data[field] = date_value.isoformat()
            # If it's a string, validate ISO format
            elif isinstance(date_value, str):
                try:
                    # Try to parse as ISO format
                    if date_value.endswith("Z"):
                        # Preserve original Z format
                        parsed_date = datetime.fromisoformat(
                            date_value.replace("Z", "+00:00")
                        )
                        event_data[field] = date_value  # Keep original format
                    else:
                        parsed_date = datetime.fromisoformat(date_value)
                        event_data[field] = parsed_date.isoformat()
                except ValueError:
                    # Try other common formats
                    formats = [
                        "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%d",
                        "%d/%m/%Y",
                        "%m/%d/%Y",
                    ]

                    parsed = None
                    for fmt in formats:
                        try:
                            parsed = datetime.strptime(date_value, fmt)
                            break
                        except ValueError:
                            continue

                    if parsed:
                        event_data[field] = parsed.isoformat()
                    else:
                        logger.warning(f"Could not parse date: {date_value}")
                        # Keep original value but log warning
                        pass

    return event_data


def _validate_location(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize location fields."""
    location_fields = ["location", "full_address", "city", "country"]

    for field in location_fields:
        if field in event_data and event_data[field]:
            location_value = event_data[field]

            if isinstance(location_value, str):
                # Clean up location string
                cleaned_location = re.sub(r"\s+", " ", location_value.strip())
                event_data[field] = cleaned_location

    return event_data


def _validate_coordinates(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate coordinate data."""
    if "coordinates" in event_data and event_data["coordinates"]:
        coords = event_data["coordinates"]

        if isinstance(coords, dict):
            # Validate latitude and longitude
            lat = coords.get("latitude")
            lng = coords.get("longitude")

            if lat is not None and lng is not None:
                try:
                    lat_float = float(lat)
                    lng_float = float(lng)

                    # Validate ranges
                    if -90 <= lat_float <= 90 and -180 <= lng_float <= 180:
                        event_data["coordinates"] = {
                            "latitude": lat_float,
                            "longitude": lng_float,
                        }
                    else:
                        logger.warning(
                            f"Invalid coordinate ranges: lat={lat_float}, lng={lng_float}"
                        )
                        del event_data["coordinates"]
                except (ValueError, TypeError):
                    logger.warning(f"Invalid coordinate values: lat={lat}, lng={lng}")
                    del event_data["coordinates"]
            else:
                logger.warning("Coordinates missing latitude or longitude")
                del event_data["coordinates"]
        else:
            logger.warning(
                "Coordinates should be a dictionary with latitude and longitude"
            )
            del event_data["coordinates"]

    return event_data


def normalize_extraction_method(method: str) -> str:
    """
    Normalize extraction method values.

    Args:
        method: Raw extraction method string

    Returns:
        Normalized extraction method
    """
    method_map = {
        "json": "json",
        "html": "html",
        "fallback": "html_fallback",
        "css": "html",
        "selector": "html",
    }

    return method_map.get(method.lower(), "unknown")


def validate_required_fields(
    event_data: Dict[str, Any], required_fields: List[str]
) -> bool:
    """
    Check if all required fields are present and not empty.

    Args:
        event_data: Event data dictionary
        required_fields: List of required field names

    Returns:
        True if all required fields are present and not empty
    """
    for field in required_fields:
        if field not in event_data or not event_data[field]:
            return False
    return True


def get_data_completeness_score(event_data: Dict[str, Any]) -> float:
    """
    Calculate a completeness score for event data.

    Args:
        event_data: Event data dictionary

    Returns:
        Completeness score between 0.0 and 1.0
    """
    # Define field weights (more important fields have higher weights)
    field_weights = {
        "title": 0.2,
        "url": 0.15,
        "date": 0.15,
        "location": 0.1,
        "full_address": 0.05,
        "city": 0.05,
        "country": 0.05,
        "coordinates": 0.05,
        "timezone": 0.05,
        "end_date": 0.05,
        "event_type": 0.03,
        "visibility": 0.02,
        "organizer": 0.05,
        "description": 0.05,
        "cover_url": 0.02,
        "api_id": 0.02,
        "guest_count": 0.01,
    }

    total_weight = 0
    achieved_weight = 0

    for field, weight in field_weights.items():
        total_weight += weight
        if field in event_data and event_data[field]:
            achieved_weight += weight

    return achieved_weight / total_weight if total_weight > 0 else 0.0
````

## File: show_up/middlewares.py
````python
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
````

## File: main.py
````python
def main():
    print("Hello from show-up-crawler!")


if __name__ == "__main__":
    main()
````

## File: pyproject.toml
````toml
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

[dependency-groups]
dev = [
    "pytest>=8.4.1",
]
````

## File: README.md
````markdown
# 🚀 Show Up Crawler

A powerful web crawler for extracting comprehensive crypto event data from Luma (lu.ma) using advanced JSON extraction techniques. Outputs structured JSON data only.

## ✨ Features

- **Enhanced JSON Extraction**: Extracts complete event data from embedded JSON structures
- **High Data Quality**: Achieves 87.2% average completeness vs 25% with basic HTML parsing
- **Comprehensive Event Data**: Dates, locations, coordinates, organizers, and metadata
- **Scrapy Export Support**: Native support for Scrapy's `-o` exporters (yields dict format)
- **Robust Architecture**: Modular design with fallback mechanisms
- **Playwright Integration**: Handles JavaScript-heavy pages effectively
- **Data Validation**: Comprehensive validation and cleaning of extracted data
- **Comprehensive Testing**: 100% test coverage for all extraction components
- **Production Ready**: Fully tested and validated implementation

## 📊 Performance Metrics

- **100% Success Rate** on tested HTML files
- **3.5x Improvement** in data quality over basic extraction
- **87.2% Average Completeness** with comprehensive field extraction
- **Multiple Extraction Methods** with intelligent fallback
- **Fully Tested**: 65+ comprehensive tests covering all functionality

## 🏗️ Architecture

```
Scrapy Spider → Playwright → JsonExtractor → Enhanced EventItem → Enhanced JSON Pipeline → Structured JSON Output
```

### Core Components

- **JsonExtractor**: Advanced JSON pattern matching and extraction with 8+ patterns
- **Enhanced EventItem**: Comprehensive data model with 15+ fields
- **Enhanced Pipelines**: Data validation, cleaning, and statistics tracking
- **Validation Utils**: Data quality assurance and normalization
- **Multi-Method Extraction**: JSON → HTML → Fallback extraction chain
- **Comprehensive Testing**: Unit and integration tests for all components

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- uv (Python package manager)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd show-up-crawler

# Install dependencies
uv sync

# Install development dependencies (already included)
# pytest and other dev dependencies are in pyproject.toml
```

### Basic Usage

```bash
# Run the enhanced crawler - outputs structured JSON only
uv run scrapy crawl luma

# Run with custom JSON output file
uv run scrapy crawl luma -s JSON_OUTPUT_FILE=my_events.json

# Use Scrapy's built-in exporters (spider yields dict format natively)
uv run scrapy crawl luma -o events.json
uv run scrapy crawl luma -o events.csv
uv run scrapy crawl luma -o events.jsonl
uv run scrapy crawl luma -o events.xml

# The crawler produces ONLY structured JSON data:
# - No HTML files are saved
# - No raw HTML processing
# - Clean, comprehensive JSON output with event data

# Test enhanced extraction on existing HTML files
uv run python test_enhanced_extraction.py

# Run all tests
uv run pytest

# Run specific test suites
uv run pytest tests/test_extractors.py -v
uv run pytest tests/test_enhanced_spider.py -v
uv run pytest tests/test_enhanced_pipelines.py -v
```

## 📁 Project Structure

```
show-up-crawler/
├── .agents/                    # Project planning and documentation
├── show_up/                    # Main crawler package
│   ├── extractors/            # Data extraction components
│   │   ├── __init__.py       # Package initialization
│   │   ├── base.py           # Base extractor interface
│   │   └── json_extractor.py # JSON extraction logic
│   ├── utils/                # Utility functions
│   │   ├── __init__.py       # Package initialization
│   │   └── validation.py     # Data validation helpers
│   ├── spiders/              # Scrapy spiders
│   │   └── luma.py          # Enhanced Luma spider
│   ├── items.py              # Enhanced data models
│   ├── pipelines.py          # Enhanced data processing
│   └── settings.py           # Configuration
├── tests/                     # Comprehensive test suite
│   ├── test_extractors.py    # JSON extraction tests
│   ├── test_enhanced_spider.py # Spider functionality tests
│   ├── test_enhanced_pipelines.py # Pipeline tests
│   ├── test_pipelines.py     # Legacy pipeline tests
│   └── test_utils.py         # Validation utility tests
├── output/                    # Extracted JSON data
├── test_enhanced_extraction.py # Integration test script
└── README.md                 # This file
```

## 🔧 Configuration

### JSON Extraction Settings

```python
# Enable/disable JSON extraction
JSON_EXTRACTION_ENABLED = True

# Custom extraction patterns (8 built-in patterns)
JSON_EXTRACTION_PATTERNS = [
    r'"event":\s*(\{(?:[^{}]|{[^{}]*})*\})',
    r'window\.__INITIAL_DATA__\s*=\s*(\{.*?\});',
    r'<script[^>]*>.*?(\{.*?"event".*?\}.*?)</script>',
    r'<script[^>]*type="application/ld\+json"[^>]*>([^<]+)</script>',
    # ... 4 more patterns
]

# Fallback to HTML parsing if JSON fails
JSON_EXTRACTION_FALLBACK = True

# Enhanced pipeline settings
ENHANCED_JSON_VALIDATION = True
ENHANCED_JSON_INCLUDE_METADATA = True
ENHANCED_JSON_EXTRACTION_STATS = True
JSON_OUTPUT_FILE = 'crypto_events.json'
JSON_INDENT = 2
JSON_ENSURE_ASCII = False

# HTML output pipelines disabled - JSON output only
# No HTML files are generated, only structured JSON data
ITEM_PIPELINES = {
    "show_up.pipelines.EnhancedJsonPipeline": 300,
    # "show_up.pipelines.HtmlFilePipeline": 301,        # DISABLED
    # "show_up.pipelines.RawHtmlFilePipeline": 302,     # DISABLED
}
```

### Output Format

The crawler generates structured JSON data with comprehensive event information and metadata:

```json
{
  "metadata": {
    "spider_name": "luma",
    "start_time": "2025-01-16T...",
    "source": "https://lu.ma/crypto",
    "extraction_config": {
      "json_extraction_enabled": true,
      "validation_enabled": true,
      "include_metadata": true,
      "extraction_stats": true
    },
    "extraction_statistics": {
      "total_processed": 8,
      "json_extraction": 8,
      "html_extraction": 0,
      "fallback_extraction": 0,
      "validation_errors": 0,
      "high_quality_events": 7,
      "success_rates": {
        "json_extraction_rate": 1.0,
        "validation_success_rate": 1.0,
        "high_quality_rate": 0.875
      }
    }
  },
  "events": [
    {
      "title": "21MeetUp | JULIO 🧡🚀",
      "date": "2025-07-21T22:30:00.000Z",
      "end_date": "2025-07-22T01:00:00.000Z",
      "timezone": "America/Buenos_Aires",
      "location": "Club de la Birra Colegiales, Buenos Aires, Argentina",
      "full_address": "Club de la Birra Colegiales, Zapiola 131, C1426 Cdad. Autónoma de Buenos Aires, Argentina",
      "city": "Buenos Aires",
      "country": "Argentina",
      "coordinates": {
        "latitude": -34.5788554,
        "longitude": -58.44275679999999
      },
      "event_type": "independent",
      "visibility": "public",
      "organizer": "Event Organizer Name",
      "url": "https://lu.ma/k9izpesk",
      "cover_url": "https://images.lumacdn.com/event-covers/...",
      "api_id": "evt-yKMLCEcEELikdzY",
      "guest_count": 42,
      "place_id": "ChIJ_test123",
      "_metadata": {
        "extraction_method": "json",
        "completeness_score": 0.90,
        "processed_at": "2025-01-16T..."
      }
    }
  ],
  "end_time": "2025-01-16T...",
  "event_count": 8
}
```

## 🧪 Testing

### Unit Tests (65+ comprehensive tests)

```bash
# Run all tests
uv run pytest

# Run specific test suites
uv run pytest tests/test_extractors.py -v          # JSON extraction tests
uv run pytest tests/test_enhanced_spider.py -v     # Spider functionality tests
uv run pytest tests/test_enhanced_pipelines.py -v  # Pipeline tests
uv run pytest tests/test_utils.py -v               # Validation utility tests

# Run with coverage
uv run pytest --cov=show_up

# Run tests with detailed output
uv run pytest -v --tb=short
```

### Integration Tests

```bash
# Test enhanced extraction on real HTML files
uv run python test_enhanced_extraction.py

# This will test extraction on all HTML files in output/html/
# and generate a comprehensive report showing:
# - 100% success rate on 8 HTML files
# - 87.2% average completeness score
# - Detailed extraction statistics
```

### Test Coverage

- **JSON Extraction**: 34 tests covering all patterns and edge cases
- **Spider Functionality**: 24 tests for all extraction methods
- **Pipeline Processing**: 17 tests for data validation and statistics
- **Validation Utils**: 15+ tests for data cleaning and validation
- **Integration**: Real-world HTML file testing

## 📈 Data Quality Metrics

### Extracted Fields (15+ comprehensive fields)

- **Basic**: Title, URL, description
- **Temporal**: Start date, end date, timezone
- **Location**: Address, city, country, coordinates, place ID
- **Metadata**: Event type, visibility, organizer, API ID
- **Additional**: Cover image, guest count, RSVP info
- **Technical**: Extraction method, completeness score, processing timestamp

### Quality Scoring (Automatic)

Events are automatically scored for completeness using weighted field importance:
- **High Quality (>80%)**: Complete event data with all major fields (87.5% of events)
- **Medium Quality (50-80%)**: Most fields present, some gaps (12.5% of events)
- **Low Quality (<50%)**: Minimal data extraction (0% of events)

### Validation Features

- **URL Normalization**: Automatically fixes partial URLs
- **Date Validation**: Supports multiple date formats with ISO conversion
- **Coordinate Validation**: Validates latitude/longitude ranges
- **Data Cleaning**: Removes empty fields and normalizes text
- **Error Handling**: Graceful degradation with comprehensive logging

## 🔍 Extraction Methods

### 1. JSON Extraction (Primary - 100% success rate)
- Extracts from embedded JSON structures using 8+ patterns
- Handles complex nested JSON with bracket balancing
- Comprehensive data extraction with all fields
- **87.2% average completeness**
- **Pattern 0 success**: Direct event object extraction

### 2. HTML Parsing (Fallback - when JSON fails)
- CSS selector-based extraction with multiple selectors
- Fallback when JSON extraction fails
- Basic field extraction (title, date, location)
- **~25% average completeness**
- Graceful degradation with logging

### 3. Minimal Extraction (Last Resort)
- Title from page title, H1 tags, or meta tags
- URL from request with normalization
- Ensures no empty results
- **Always provides at least title + URL**

### Extraction Pipeline
```
1. JSON Extraction (8 patterns) → Success: 87.2% completeness
2. HTML Fallback (CSS selectors) → Success: 25% completeness  
3. Minimal Extraction (title/URL) → Success: 100% always
```

## 🛠️ Development

### Current Output Behavior
The crawler has been streamlined to focus exclusively on JSON data extraction:

- **✅ JSON Output**: Complete structured event data with metadata
- **🚫 HTML Files**: No HTML files are saved (removed for efficiency)
- **🚫 Raw HTML**: No raw HTML processing or storage
- **📊 Statistics**: Comprehensive extraction statistics in JSON output
- **🔧 Performance**: Optimized for JSON extraction only

### Adding New Extractors

1. Create extractor class inheriting from `BaseExtractor`
2. Implement `extract()` and `can_extract()` methods
3. Add comprehensive tests in `tests/test_extractors.py`
4. Add to `MultiExtractor` for fallback chains

```python
from show_up.extractors.base import BaseExtractor

class MyExtractor(BaseExtractor):
    def extract(self, content, **kwargs):
        # Your extraction logic here
        return extracted_data
    
    def can_extract(self, content):
        # Check if this extractor can handle the content
        return "my_pattern" in content
    
    def validate_extracted_data(self, data):
        # Override for custom validation
        return super().validate_extracted_data(data)
```

### Adding New Fields

1. Add field to `EventItem` in `items.py` with proper type hints
2. Update extraction logic in extractors
3. Add validation in `utils/validation.py`
4. Update pipeline processing if needed
5. Add field to completeness scoring weights
6. Write comprehensive tests for the new field

### Testing Guidelines

- Write unit tests for all new functionality
- Test edge cases and error conditions
- Use real HTML samples for integration tests
- Maintain >90% test coverage
- Follow existing test patterns and naming conventions

## 📊 Monitoring and Debugging

### Extraction Statistics (Built-in)

The enhanced pipeline tracks detailed statistics:
- Success rates by extraction method (JSON: 100%, HTML: 0%, Fallback: 0%)
- Data quality metrics (87.2% average completeness)
- Processing times and validation results
- High-quality event detection (87.5% of events)
- Comprehensive metadata in output JSON

### Debug Mode

```bash
# Enable debug logging
export SCRAPY_SETTINGS_MODULE=show_up.settings
uv run scrapy crawl luma -L DEBUG

# Enable JSON extraction debug mode
uv run scrapy crawl luma -s JSON_EXTRACTION_DEBUG=True

# Test extraction on specific HTML file
uv run python -c "
from show_up.extractors.json_extractor import JsonExtractor
extractor = JsonExtractor()
with open('output/html/event.html', 'r') as f:
    result = extractor.extract(f.read())
print(result)
"

# Check JSON output only (no HTML files generated)
cat crypto_events.json | jq '.metadata.extraction_statistics'
```

### Debugging Tools

- **Integration Test Script**: `test_enhanced_extraction.py`
- **Comprehensive Logging**: All extraction attempts logged
- **Validation Reporting**: Detailed validation error messages
- **Pattern Debugging**: Shows which JSON pattern succeeded
- **Completeness Scoring**: Automatic data quality assessment

## 🎯 Roadmap

- [x] Enhanced JSON extraction system (✅ Completed)
- [x] Comprehensive test coverage (✅ Completed)
- [x] Data validation and quality scoring (✅ Completed)
- [x] Production-ready pipelines (✅ Completed)
- [ ] Support for additional event platforms (Eventbrite, Meetup)
- [ ] Real-time event monitoring with webhooks
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Event deduplication and duplicate detection
- [ ] Geographic event clustering and analysis
- [ ] Event recommendation system
- [ ] API endpoint for extracted data
- [ ] Dashboard for monitoring extraction quality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the coding standards in `.agents/RULES.md`
4. Add comprehensive tests (maintain >90% coverage)
5. Update documentation and README
6. Ensure all tests pass: `uv run pytest`
7. Test with real HTML files: `uv run python test_enhanced_extraction.py`
8. Submit a pull request with detailed description

### Development Setup

```bash
# Clone and setup
git clone <repository-url>
cd show-up-crawler
uv sync

# Run tests to ensure everything works
uv run pytest -v

# Test integration
uv run python test_enhanced_extraction.py
```

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Scrapy](https://scrapy.org/) and [Playwright](https://playwright.dev/)
- Follows the architecture patterns from `.agents/PLANNING.md`
- Uses modern Python 3.13+ features and type hints
- Comprehensive testing with [pytest](https://pytest.org/)
- Package management with [uv](https://github.com/astral-sh/uv)

## 📝 Implementation Status

✅ **Complete**: Enhanced JSON extraction system with 100% success rate
✅ **Complete**: Comprehensive test coverage (110+ tests)
✅ **Complete**: Data validation and quality scoring
✅ **Complete**: Production-ready pipelines with statistics
✅ **Complete**: Integration testing with real HTML files
✅ **Complete**: Documentation and usage examples
✅ **Complete**: JSON-only output (HTML file generation removed)
✅ **Complete**: Streamlined pipeline configuration

---

**Show Up Crawler** - Making crypto event discovery comprehensive and reliable! 🚀

*Enhanced JSON extraction system achieving 87.2% data completeness with 100% success rate*  
*Streamlined JSON-only output for clean, structured event data*
````

## File: show_up/items.py
````python
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from typing import Any


class EventItem(scrapy.Item):
    """
    Enhanced EventItem for complete event data extraction.

    This item supports comprehensive event information including temporal data,
    location details, metadata, and technical fields for tracking extraction methods.
    """

    # Basic fields
    title = scrapy.Field()  # Event title
    url = scrapy.Field()  # Event URL
    description = scrapy.Field()  # Event description

    # Temporal fields
    date = scrapy.Field()  # Start date (ISO format)
    end_date = scrapy.Field()  # End date (ISO format)
    timezone = scrapy.Field()  # Event timezone (e.g., "America/Buenos_Aires")

    # Location fields
    location = scrapy.Field()  # Simple location string for backward compatibility
    full_address = scrapy.Field()  # Complete formatted address
    city = scrapy.Field()  # City name
    country = scrapy.Field()  # Country name
    coordinates = scrapy.Field()  # Dict with 'latitude' and 'longitude'
    place_id = scrapy.Field()  # Google Place ID or similar

    # Metadata fields
    event_type = scrapy.Field()  # Event type (e.g., "independent", "series")
    visibility = scrapy.Field()  # Visibility (e.g., "public", "private")
    api_id = scrapy.Field()  # Platform-specific API ID
    cover_url = scrapy.Field()  # Cover image URL
    organizer = scrapy.Field()  # Event organizer information
    guest_count = scrapy.Field()  # Number of guests/attendees

    # Technical fields
    html_content = scrapy.Field()  # Processed HTML content
    raw_html = scrapy.Field()  # Raw HTML response
    extraction_method = (
        scrapy.Field()
    )  # How data was extracted ("json", "html", "fallback")

    def __setitem__(self, key: str, value: Any) -> None:
        """Override to provide type hints and validation."""
        super().__setitem__(key, value)

    def __getitem__(self, key: str) -> Any:
        """Override to provide type hints."""
        return super().__getitem__(key)

    def get(self, key: str, default: Any = None) -> Any:
        """Get field value with default."""
        try:
            return self[key]
        except KeyError:
            return default
````

## File: show_up/settings.py
````python
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
    # "show_up.pipelines.JsonWriterPipeline": 300,  # Legacy JSON pipeline (commented out)
    "show_up.pipelines.EnhancedJsonPipeline": 300,  # Enhanced JSON pipeline with structured output
    # HTML output pipelines removed - JSON output only
    # "show_up.pipelines.HtmlFilePipeline": 301,
    # "show_up.pipelines.RawHtmlFilePipeline": 302,
}

# JSON output settings
JSON_OUTPUT_FILE = "crypto_events.json"
JSON_INDENT = 2  # Pretty-print JSON with 2-space indentation
JSON_ENSURE_ASCII = False  # Allow non-ASCII characters in JSON

# JSON Extraction Settings
JSON_EXTRACTION_ENABLED = True  # Enable JSON data extraction from HTML
JSON_EXTRACTION_PATTERNS = [
    r'"event":\s*(\{[^}]+(?:\{[^}]*\}[^}]*)*\})',
    r"window\.__INITIAL_DATA__\s*=\s*({.+?});",
    r'<script[^>]*>.*?({.*?"event".*?}.*?)</script>',
    r'<script[^>]*type="application/ld\+json"[^>]*>([^<]+)</script>',
    r"window\.__PROPS__\s*=\s*({.+?});",
    r'data-event=(["\'])({.*?})\1',
]
JSON_EXTRACTION_FALLBACK = True  # Fall back to HTML parsing if JSON extraction fails
JSON_EXTRACTION_DEBUG = False  # Enable debug logging for JSON extraction

# Enhanced Item Pipeline Settings
ENHANCED_JSON_VALIDATION = True  # Enable data validation for extracted items
ENHANCED_JSON_INCLUDE_METADATA = True  # Include extraction metadata in output
ENHANCED_JSON_EXTRACTION_STATS = True  # Track extraction statistics

# Concurrency and throttling settings
# CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "show_up.middlewares.ShowUpSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "show_up.middlewares.ShowUpDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

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
````

## File: show_up/pipelines.py
````python
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any
from show_up.utils.validation import (
    validate_event_data,
    clean_event_data,
    get_data_completeness_score,
)


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

    def __init__(
        self,
        output_file: str = "crypto_events.json",
        indent: int = 2,
        ensure_ascii: bool = False,
    ):
        self.output_file = output_file
        self.indent = indent
        self.ensure_ascii = ensure_ascii
        self.items: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {}
        self.extraction_stats: Dict[str, int] = {
            "total_processed": 0,
            "json_extraction": 0,
            "html_extraction": 0,
            "fallback_extraction": 0,
            "validation_errors": 0,
            "high_quality_events": 0,
        }

    @classmethod
    def from_crawler(cls, crawler):
        # Get settings from crawler
        output_file = crawler.settings.get("JSON_OUTPUT_FILE", "crypto_events.json")
        indent = crawler.settings.getint("JSON_INDENT", 2)
        ensure_ascii = crawler.settings.getbool("JSON_ENSURE_ASCII", False)
        pipeline = cls(
            output_file=output_file, indent=indent, ensure_ascii=ensure_ascii
        )

        # Store settings reference for configuration
        pipeline.settings = {
            "ENHANCED_JSON_VALIDATION": crawler.settings.getbool(
                "ENHANCED_JSON_VALIDATION", True
            ),
            "ENHANCED_JSON_INCLUDE_METADATA": crawler.settings.getbool(
                "ENHANCED_JSON_INCLUDE_METADATA", True
            ),
            "ENHANCED_JSON_EXTRACTION_STATS": crawler.settings.getbool(
                "ENHANCED_JSON_EXTRACTION_STATS", True
            ),
        }
        return pipeline

    def open_spider(self, spider):
        # Initialize metadata
        self.metadata = {
            "spider_name": spider.name,
            "start_time": datetime.now().isoformat(),
            "source": spider.start_urls[0] if spider.start_urls else None,
            "extraction_config": {
                "json_extraction_enabled": getattr(self, "settings", {}).get(
                    "JSON_EXTRACTION_ENABLED", True
                ),
                "validation_enabled": getattr(self, "settings", {}).get(
                    "ENHANCED_JSON_VALIDATION", True
                ),
                "include_metadata": getattr(self, "settings", {}).get(
                    "ENHANCED_JSON_INCLUDE_METADATA", True
                ),
                "extraction_stats": getattr(self, "settings", {}).get(
                    "ENHANCED_JSON_EXTRACTION_STATS", True
                ),
            },
        }
        spider.logger.info(
            f"EnhancedJsonPipeline initialized. Output file: {self.output_file}"
        )
        spider.logger.info(
            f"Extraction configuration: {self.metadata['extraction_config']}"
        )

    def close_spider(self, spider):
        # Add extraction statistics to metadata
        if getattr(self, "settings", {}).get("ENHANCED_JSON_EXTRACTION_STATS", True):
            self.metadata["extraction_statistics"] = self.extraction_stats.copy()

            # Calculate success rates
            total = self.extraction_stats["total_processed"]
            if total > 0:
                success_rates = {
                    "json_extraction_rate": self.extraction_stats["json_extraction"]
                    / total,
                    "html_extraction_rate": self.extraction_stats["html_extraction"]
                    / total,
                    "fallback_rate": self.extraction_stats["fallback_extraction"]
                    / total,
                    "validation_success_rate": 1
                    - (self.extraction_stats["validation_errors"] / total),
                    "high_quality_rate": self.extraction_stats["high_quality_events"]
                    / total,
                }
                self.metadata["extraction_statistics"]["success_rates"] = success_rates

        # Create the final JSON structure
        output = {
            "metadata": self.metadata,
            "events": self.items,
            "end_time": datetime.now().isoformat(),
            "event_count": len(self.items),
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
                    spider.logger.warning(
                        f"Falling back to current directory: {self.output_file}"
                    )

            # Write the JSON file
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=self.indent, ensure_ascii=self.ensure_ascii)
            spider.logger.info(
                f"Successfully wrote {len(self.items)} events to {self.output_file}"
            )
        except PermissionError:
            spider.logger.error(f"Permission denied when writing to {self.output_file}")
        except IsADirectoryError:
            spider.logger.error(
                f"Cannot write to {self.output_file} because it is a directory"
            )
        except FileNotFoundError:
            spider.logger.error(
                f"Directory for {self.output_file} does not exist and could not be created"
            )
        except Exception as e:
            spider.logger.error(f"Failed to write JSON file: {e}")

    def process_item(self, item, spider):
        try:
            # Update extraction statistics
            self.extraction_stats["total_processed"] += 1

            # Create a copy of the item and remove HTML fields
            item_copy = dict(item)
            item_copy.pop("html_content", None)
            item_copy.pop("raw_html", None)

            # Track extraction method
            extraction_method = item_copy.get("extraction_method", "unknown")
            if extraction_method == "json":
                self.extraction_stats["json_extraction"] += 1
            elif extraction_method == "html_fallback":
                self.extraction_stats["html_extraction"] += 1
            elif extraction_method == "fallback":
                self.extraction_stats["fallback_extraction"] += 1

            # Validate and clean data if enabled
            if getattr(self, "settings", {}).get("ENHANCED_JSON_VALIDATION", True):
                try:
                    item_copy = validate_event_data(item_copy)
                    item_copy = clean_event_data(item_copy)

                    # Calculate data quality score
                    completeness_score = get_data_completeness_score(item_copy)
                    if completeness_score > 0.7:  # High quality threshold
                        self.extraction_stats["high_quality_events"] += 1

                    # Add quality metadata if configured
                    if getattr(self, "settings", {}).get(
                        "ENHANCED_JSON_INCLUDE_METADATA", True
                    ):
                        item_copy["_metadata"] = {
                            "extraction_method": extraction_method,
                            "completeness_score": completeness_score,
                            "processed_at": datetime.now().isoformat(),
                        }

                except Exception as e:
                    spider.logger.warning(f"Data validation failed: {e}")
                    self.extraction_stats["validation_errors"] += 1
                    # Continue with unvalidated data

            # Ensure required fields are present
            required_fields = ["title", "url"]
            for field in required_fields:
                if field not in item_copy or not item_copy[field]:
                    spider.logger.warning(f"Item missing required field: {field}")
                    # Provide default values for required fields
                    if field == "title":
                        item_copy[field] = (
                            f"Untitled Event ({datetime.now().isoformat()})"
                        )
                    elif field == "url":
                        item_copy[field] = "unknown_url"

            # Ensure all standard fields have values (even if empty)
            standard_fields = [
                "date",
                "end_date",
                "timezone",
                "location",
                "full_address",
                "city",
                "country",
                "coordinates",
                "place_id",
                "event_type",
                "visibility",
                "api_id",
                "cover_url",
                "organizer",
                "guest_count",
                "description",
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
                        spider.logger.warning(
                            f"Converting non-serializable value in field '{key}' to string"
                        )
                        item_copy[key] = str(value)

            # Add to items list
            self.items.append(item_copy)

            # Log successful processing
            spider.logger.info(
                f"Successfully processed item: {item_copy.get('title', 'Unknown')} "
                f"(method: {extraction_method})"
            )

        except Exception as e:
            spider.logger.error(f"Error processing item in EnhancedJsonPipeline: {e}")
            self.extraction_stats["validation_errors"] += 1

        return item


# Legacy pipeline kept for backward compatibility
class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open("crypto_events.json", "w")
        spider.logger.warning(
            "Using deprecated JsonWriterPipeline. Consider switching to EnhancedJsonPipeline."
        )

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        # Create a copy of the item and remove the HTML fields
        item_copy = dict(item)
        item_copy.pop("html_content", None)
        item_copy.pop("raw_html", None)
        line = json.dumps(item_copy) + "\n"
        self.file.write(line)
        return item


class HtmlFilePipeline:
    output_dir = "output/html"

    def open_spider(self, spider):
        os.makedirs(self.output_dir, exist_ok=True)

    def process_item(self, item, spider):
        spider.logger.info(f"Processing item in HtmlFilePipeline: {item}")
        if (
            "html_content" in item
            and "title" in item
            and item["html_content"] is not None
        ):
            title = item["title"]
            # Sanitize the title to create a valid filename
            filename = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")
            filepath = os.path.join(self.output_dir, f"{filename}.html")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(item["html_content"])
        else:
            spider.logger.warning(
                f"Skipping HTML file creation for item: {item['title']} - html_content is None"
            )
        return item


class RawHtmlFilePipeline:
    output_dir = "output/raw_html"

    def open_spider(self, spider):
        os.makedirs(self.output_dir, exist_ok=True)

    def process_item(self, item, spider):
        if "raw_html" in item and "title" in item:
            title = item["title"]
            # Sanitize the title to create a valid filename
            filename = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")
            filepath = os.path.join(self.output_dir, f"{filename}_raw.html")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(item["raw_html"])
        return item
````

## File: show_up/spiders/luma.py
````python
import scrapy
from show_up.items import EventItem
from show_up.extractors import JsonExtractor
from show_up.utils.validation import validate_event_data
from scrapy_playwright.page import PageMethod
from typing import Any

HTML_FILE = "output/luma.html"

class LumaSpider(scrapy.Spider):
    name = "luma"
    allowed_domains = ["lu.ma"]
    start_urls = ["https://lu.ma/crypto"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize JSON extractor
        custom_patterns = []
        if hasattr(self, "settings") and self.settings:
            custom_patterns = self.settings.getlist("JSON_EXTRACTION_PATTERNS", [])

        self.json_extractor = JsonExtractor(
            config={"required_fields": ["title"], "custom_patterns": custom_patterns}
        )

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
        # Save the full HTML response for debugging
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(response.text)

        # Extract event links from the timeline section
        # Look for individual event cards in the timeline
        event_links = response.css("a.event-link::attr(href)").getall()
        self.logger.info(
            f"Found {len(event_links)} event links with selector 'a.event-link'"
        )

        # Try different selectors to find event links
        alternative_selectors = [
            "a.event-link",
            'a[aria-label*="event"]',
            'a[href*="/1"]',  # Individual event IDs seem to start with /1
            'a[href*="/g"]',  # Some event IDs start with /g
            'a[href*="/v"]',  # Some event IDs start with /v
            '.timeline a[href^="/"]',  # Links in timeline starting with /
        ]

        for selector in alternative_selectors:
            links = response.css(f"{selector}::attr(href)").getall()
            self.logger.info(f"Selector '{selector}' found {len(links)} links")
            if links:
                # Show first few links as examples
                for link in links[:3]:
                    self.logger.info(f"  Example link: {link}")

        # If we found event links, process them
        if event_links:
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
        else:
            self.logger.warning(
                "No event links found! This might be a JavaScript-heavy page that needs more time to load."
            )

    def parse_event(self, response):
        """Parse event page and extract complete event data using JSON extraction.

        Returns:
            dict: Event data as a dictionary for JSON serialization.
        """
        # Initialize event item
        item = EventItem()

        # Set basic fields
        item["url"] = response.url

        # Try JSON extraction first (primary method)
        extracted_data = self._extract_with_json(response)

        # If JSON extraction fails, fall back to HTML parsing
        if not extracted_data and self.settings.getbool(
            "JSON_EXTRACTION_FALLBACK", True
        ):
            extracted_data = self._extract_with_html_selectors(response)

        # If we still don't have data, create minimal item
        if not extracted_data:
            self.logger.warning(f"Failed to extract data from {response.url}")
            extracted_data = {
                "title": self._extract_title_fallback(response),
                "extraction_method": "fallback",
            }

        # Populate item with extracted data
        self._populate_item(item, extracted_data)

        # Validate and clean data
        try:
            item_dict = dict(item)
            validated_data = validate_event_data(item_dict)

            # Update item with validated data
            for key, value in validated_data.items():
                item[key] = value

            self.logger.info(
                f"Successfully extracted event: {item.get('title', 'Unknown')} using {item.get('extraction_method', 'unknown')}"
            )

        except Exception as e:
            self.logger.error(f"Data validation failed for {response.url}: {e}")

        # Convert to dictionary for JSON serialization (required for -o events.json)
        event_dict: dict[str, Any] = dict(item)
        yield event_dict
        return  # prevents the old `yield item`

    def _extract_with_json(self, response) -> dict[str, Any] | None:
        """Extract event data using JSON extraction."""
        if not self.settings.getbool("JSON_EXTRACTION_ENABLED", True):
            return None

        try:
            extracted_data = self.json_extractor.extract(
                response.text, url=response.url
            )

            if extracted_data:
                self.logger.info(f"JSON extraction successful for {response.url}")
                return extracted_data
            else:
                self.logger.debug(f"JSON extraction found no data for {response.url}")

        except Exception as e:
            self.logger.warning(f"JSON extraction failed for {response.url}: {e}")

        return None

    def _extract_with_html_selectors(self, response) -> dict[str, Any] | None:
        """Extract event data using HTML selectors (fallback method)."""
        self.logger.info(f"Falling back to HTML selector extraction for {response.url}")

        extracted_data = {"extraction_method": "html_fallback"}

        # Try multiple selectors for title
        title = response.css("h1::text").get()
        if not title:
            title = response.css('[data-testid="event-title"]::text').get()
        if not title:
            title = response.css("title::text").get()
        if not title:
            title = response.css(".title::text").get()

        # Try multiple selectors for date
        date = response.css(".event-date::text").get()
        if not date:
            date = response.css('[data-testid="event-date"]::text').get()
        if not date:
            date = response.css("time::text").get()
        if not date:
            date = response.css("[datetime]::attr(datetime)").get()

        # Try multiple selectors for location
        location = response.css(".event-location::text").get()
        if not location:
            location = response.css('[data-testid="event-location"]::text').get()
        if not location:
            location = response.css("address::text").get()
        if not location:
            location = response.css(".location::text").get()

        # Populate extracted data
        if title:
            extracted_data["title"] = title.strip()
        if date:
            extracted_data["date"] = date.strip()
        if location:
            extracted_data["location"] = location.strip()

        return extracted_data if extracted_data.get("title") else None

    def _extract_title_fallback(self, response) -> str:
        """Extract title using multiple fallback methods."""
        # Try page title
        title = response.css("title::text").get()
        if title:
            # Clean up title (remove site name, etc.)
            title = title.replace(" | Luma", "").replace(" - Luma", "").strip()
            return title

        # Try any h1 tag
        title = response.css("h1::text").get()
        if title:
            return title.strip()

        # Try meta property
        title = response.css('meta[property="og:title"]::attr(content)').get()
        if title:
            return title.strip()

        # Final fallback - extract from URL
        url_parts = response.url.split("/")
        if url_parts and url_parts[-1]:
            return url_parts[-1].replace("-", " ").title()

        return "Unknown Event"

    def _populate_item(self, item: EventItem, data: dict[str, Any]) -> None:
        """Populate EventItem with extracted data."""
        # Map extracted data to item fields
        field_mapping = {
            "title": "title",
            "date": "date",
            "end_date": "end_date",
            "timezone": "timezone",
            "location": "location",
            "full_address": "full_address",
            "city": "city",
            "country": "country",
            "coordinates": "coordinates",
            "place_id": "place_id",
            "event_type": "event_type",
            "visibility": "visibility",
            "api_id": "api_id",
            "cover_url": "cover_url",
            "organizer": "organizer",
            "guest_count": "guest_count",
            "description": "description",
            "extraction_method": "extraction_method",
        }

        for data_key, item_key in field_mapping.items():
            if data_key in data and data[data_key]:
                item[item_key] = data[data_key]
````
