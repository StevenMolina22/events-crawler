"""
JSON data extractor for Luma event pages.

This module implements comprehensive JSON extraction from Luma event pages.
It handles multiple JSON patterns and structures commonly found in Luma's
HTML responses, providing robust data extraction with fallback mechanisms.
"""

import json
import re
import logging
from typing import Any, Optional, Dict
from datetime import datetime

from .base import BaseExtractor, EventData

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
        r'data-event=(["\"])(.*?)\1',
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

    def extract(self, content: str, **kwargs) -> Optional[EventData]:
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
    ) -> Optional[EventData]:
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
    ) -> Optional[EventData]:
        """
        Extract event data from parsed JSON structure.

        Args:
            json_data: Parsed JSON data

        Returns:
            Event data dictionary or None if extraction fails
        """
        event_info = self._find_event_info(json_data)
        if not event_info:
            return None

        event_data: EventData = {}
        self._extract_basic_info(event_info, event_data)
        self._extract_temporal_info(event_info, event_data)
        self._extract_location_data(event_info, event_data)
        self._extract_metadata(event_info, event_data)

        return event_data if event_data.get("title") else None

    def _find_event_info(self, json_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the nested event dictionary within the JSON data."""
        if "event" in json_data:
            return json_data["event"]
        if "props" in json_data and "event" in json_data["props"]:
            return json_data["props"]["event"]
        if "initialData" in json_data and "event" in json_data["initialData"]:
            return json_data["initialData"]["event"]
        if "name" in json_data and "start_at" in json_data:
            return json_data
        return None

    def _extract_basic_info(
        self, event_info: Dict[str, Any], event_data: EventData
    ) -> None:
        """Extract basic event information."""
        event_data["title"] = event_info.get("name", "")
        event_data["api_id"] = event_info.get("api_id", "")
        event_data["event_type"] = event_info.get("event_type", "")
        event_data["visibility"] = event_info.get("visibility", "")

        description_fields = ["description", "details", "content", "body"]
        for field in description_fields:
            if event_info.get(field):
                event_data["description"] = event_info[field]
                break

    def _extract_temporal_info(
        self, event_info: Dict[str, Any], event_data: EventData
    ) -> None:
        """Extract temporal event information."""
        if "start_at" in event_info:
            event_data["date"] = event_info["start_at"]
        if "end_at" in event_info:
            event_data["end_date"] = event_info["end_at"]
        if "timezone" in event_info:
            event_data["timezone"] = event_info["timezone"]

    def _extract_location_data(
        self, event_info: Dict[str, Any], event_data: EventData
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

    def _extract_metadata(
        self, event_info: Dict[str, Any], event_data: EventData
    ) -> None:
        """Extract metadata from event information."""
        if "cover_url" in event_info:
            event_data["cover_url"] = event_info["cover_url"]

        if "url" in event_info:
            url = event_info["url"]
            if url and not url.startswith("http"):
                event_data["url"] = f"https://lu.ma/{url}"
            else:
                event_data["url"] = url

        if "guest_count" in event_info:
            event_data["guest_count"] = event_info["guest_count"]
        elif "rsvp_count" in event_info:
            event_data["guest_count"] = event_info["rsvp_count"]

        if "user" in event_info:
            organizer = event_info["user"]
            if isinstance(organizer, dict):
                event_data["organizer"] = organizer.get("name", "")

    def validate_extracted_data(self, data: EventData) -> bool:
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
