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
show_up/
  extractors/
    __init__.py
    base.py
    json_extractor.py
  spiders/
    __init__.py
    luma.py
  utils/
    __init__.py
    validation.py
  items.py
  middlewares.py
  pipelines.py
  settings.py
tests/
  test_extractors.py
  test_pipelines.py
  test_utils.py
.env.local
enhanced_extraction_results.json
main.py
pyproject.toml
README.md
test_enhanced_extraction.py
```

# Files

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

__all__ = ['JsonExtractor']
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
        return self.__class__.__name__.lower().replace('extractor', '')

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
        required_fields = self.config.get('required_fields', [])
        for field in required_fields:
            if field not in data or not data[field]:
                self.logger.warning(f"Missing required field: {field}")
                return False

        return True

    def log_extraction_result(self, success: bool, data: Optional[Dict[str, Any]] = None):
        """
        Log the result of an extraction attempt.

        Args:
            success: Whether extraction was successful
            data: Extracted data (if successful)
        """
        if success and data:
            self.logger.info(f"Successfully extracted data using {self.get_extraction_method()}")
            self.logger.debug(f"Extracted fields: {list(data.keys())}")
        else:
            self.logger.warning(f"Failed to extract data using {self.get_extraction_method()}")


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
                        result['extraction_method'] = extractor.get_extraction_method()
                        extractor.log_extraction_result(True, result)
                        return result
                except Exception as e:
                    self.logger.warning(f"Extractor {extractor.__class__.__name__} failed: {e}")
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
from typing import Dict, Any, Optional, List, Union
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
        r'window\.__INITIAL_DATA__\s*=\s*(\{.*?\});',

        # Pattern 3: Event data in script tag (non-greedy)
        r'<script[^>]*>.*?(\{.*?"event".*?\}.*?)</script>',

        # Pattern 4: JSON-LD structured data
        r'<script[^>]*type="application/ld\+json"[^>]*>([^<]+)</script>',

        # Pattern 5: React props or state
        r'window\.__PROPS__\s*=\s*(\{.*?\});',

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
        if config and 'custom_patterns' in config:
            self.patterns.extend(config['custom_patterns'])

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
            'window.__INITIAL_DATA__',
            'application/ld+json',
            'data-event',
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
                    result['extraction_method'] = 'json'
                    result['extraction_pattern'] = i

                    # Add any additional context from kwargs
                    if 'url' in kwargs:
                        result['url'] = kwargs['url']

                    self.logger.info(f"Successfully extracted data using pattern {i}")
                    return result

            except Exception as e:
                self.logger.debug(f"Pattern {i} failed: {e}")
                continue

        self.logger.warning("All JSON patterns failed")
        return None

    def _extract_with_pattern(self, content: str, pattern: str, pattern_index: int) -> Optional[Dict[str, Any]]:
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
                self.logger.debug(f"Failed to parse JSON from pattern {pattern_index}: {e}")
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
        json_str = json_str.replace('&quot;', '"')
        json_str = json_str.replace('&amp;', '&')
        json_str = json_str.replace('&lt;', '<')
        json_str = json_str.replace('&gt;', '>')

        # Remove JavaScript comments (but be careful with URLs)
        # Only remove block comments for safety
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        # Only remove line comments if they start at the beginning of a line
        json_str = re.sub(r'^\s*//.*?$', '', json_str, flags=re.MULTILINE)

        # Ensure proper JSON structure
        if not json_str.startswith(('{', '[')):
            # Try to find the start of JSON
            json_start = max(json_str.find('{'), json_str.find('['))
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
        if json_str.startswith('{'):
            return self._balance_braces(json_str)
        elif json_str.startswith('['):
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
                if char == '"' and (i == 0 or json_str[i-1] != '\\'):
                    in_string = False
                elif char == '\\':
                    i += 1  # Skip next character
            else:
                if char == '"':
                    in_string = True
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        return json_str[:i+1]

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
                if char == '"' and (i == 0 or json_str[i-1] != '\\'):
                    in_string = False
                elif char == '\\':
                    i += 1  # Skip next character
            else:
                if char == '"':
                    in_string = True
                elif char == '[':
                    bracket_count += 1
                elif char == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        return json_str[:i+1]

            i += 1

        return json_str

    def _extract_event_from_json(self, json_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
        if 'event' in json_data:
            event_info = json_data['event']
        # Event in nested structure
        elif 'props' in json_data and 'event' in json_data['props']:
            event_info = json_data['props']['event']
        # Event in initialData
        elif 'initialData' in json_data and 'event' in json_data['initialData']:
            event_info = json_data['initialData']['event']
        # Direct event data (when the whole JSON is the event)
        elif 'name' in json_data and 'start_at' in json_data:
            event_info = json_data

        if not event_info:
            return None

        # Extract basic information
        event_data['title'] = event_info.get('name', '')
        event_data['api_id'] = event_info.get('api_id', '')
        event_data['event_type'] = event_info.get('event_type', '')
        event_data['visibility'] = event_info.get('visibility', '')

        # Extract temporal information
        if 'start_at' in event_info:
            event_data['date'] = event_info['start_at']
        if 'end_at' in event_info:
            event_data['end_date'] = event_info['end_at']
        if 'timezone' in event_info:
            event_data['timezone'] = event_info['timezone']

        # Extract location information
        self._extract_location_data(event_info, event_data)

        # Extract additional metadata
        if 'cover_url' in event_info:
            event_data['cover_url'] = event_info['cover_url']

        # Extract URL
        if 'url' in event_info:
            url = event_info['url']
            if url and not url.startswith('http'):
                event_data['url'] = f"https://lu.ma/{url}"
            else:
                event_data['url'] = url

        # Extract guest information
        if 'guest_count' in event_info:
            event_data['guest_count'] = event_info['guest_count']
        elif 'rsvp_count' in event_info:
            event_data['guest_count'] = event_info['rsvp_count']

        # Extract organizer information
        if 'user' in event_info:
            organizer = event_info['user']
            if isinstance(organizer, dict):
                event_data['organizer'] = organizer.get('name', '')

        # Extract description (might be in different fields)
        description_fields = ['description', 'details', 'content', 'body']
        for field in description_fields:
            if field in event_info and event_info[field]:
                event_data['description'] = event_info[field]
                break

        return event_data if event_data.get('title') else None

    def _extract_location_data(self, event_info: Dict[str, Any], event_data: Dict[str, Any]) -> None:
        """
        Extract location information from event data.

        Args:
            event_info: Source event information
            event_data: Target event data dictionary to populate
        """
        # Extract geo address information
        if 'geo_address_info' in event_info:
            geo_info = event_info['geo_address_info']

            # Simple location string
            location_parts = []
            if 'address' in geo_info:
                location_parts.append(geo_info['address'])
            if 'city' in geo_info:
                location_parts.append(geo_info['city'])
            if 'country' in geo_info:
                location_parts.append(geo_info['country'])

            if location_parts:
                event_data['location'] = ', '.join(location_parts)

            # Detailed location fields
            if 'full_address' in geo_info:
                event_data['full_address'] = geo_info['full_address']
            if 'city' in geo_info:
                event_data['city'] = geo_info['city']
            if 'country' in geo_info:
                event_data['country'] = geo_info['country']
            if 'place_id' in geo_info:
                event_data['place_id'] = geo_info['place_id']

        # Extract coordinates
        if 'coordinate' in event_info:
            coord = event_info['coordinate']
            if isinstance(coord, dict) and 'latitude' in coord and 'longitude' in coord:
                event_data['coordinates'] = {
                    'latitude': coord['latitude'],
                    'longitude': coord['longitude']
                }

        # Alternative location fields
        if not event_data.get('location'):
            location_fields = ['location', 'venue', 'address']
            for field in location_fields:
                if field in event_info and event_info[field]:
                    event_data['location'] = event_info[field]
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
        required_fields = ['title']
        for field in required_fields:
            if field not in data or not data[field]:
                return False

        # Validate date format if present
        if 'date' in data and data['date']:
            try:
                datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                self.logger.warning(f"Invalid date format: {data['date']}")
                return False

        return True
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

from .validation import validate_event_data, clean_event_data

__all__ = ['validate_event_data', 'clean_event_data']
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
from typing import Dict, Any, Optional, List, Union
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
    required_fields = ['title', 'url']
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
    if 'url' in event_data:
        url = event_data['url']

        # Add protocol if missing
        if url and not url.startswith(('http://', 'https://')):
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = 'https://lu.ma' + url
            elif 'lu.ma' in url:
                url = 'https://' + url
            else:
                url = 'https://lu.ma/' + url

        # Validate URL format
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                logger.warning(f"Invalid URL format: {url}")
                return event_data
        except Exception as e:
            logger.warning(f"URL validation failed: {e}")
            return event_data

        event_data['url'] = url

    return event_data


def _validate_dates(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize date fields."""
    date_fields = ['date', 'end_date']

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
                    if date_value.endswith('Z'):
                        # Preserve original Z format
                        parsed_date = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                        event_data[field] = date_value  # Keep original format
                    else:
                        parsed_date = datetime.fromisoformat(date_value)
                        event_data[field] = parsed_date.isoformat()
                except ValueError:
                    # Try other common formats
                    formats = [
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%d',
                        '%d/%m/%Y',
                        '%m/%d/%Y',
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
    location_fields = ['location', 'full_address', 'city', 'country']

    for field in location_fields:
        if field in event_data and event_data[field]:
            location_value = event_data[field]

            if isinstance(location_value, str):
                # Clean up location string
                cleaned_location = re.sub(r'\s+', ' ', location_value.strip())
                event_data[field] = cleaned_location

    return event_data


def _validate_coordinates(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate coordinate data."""
    if 'coordinates' in event_data and event_data['coordinates']:
        coords = event_data['coordinates']

        if isinstance(coords, dict):
            # Validate latitude and longitude
            lat = coords.get('latitude')
            lng = coords.get('longitude')

            if lat is not None and lng is not None:
                try:
                    lat_float = float(lat)
                    lng_float = float(lng)

                    # Validate ranges
                    if -90 <= lat_float <= 90 and -180 <= lng_float <= 180:
                        event_data['coordinates'] = {
                            'latitude': lat_float,
                            'longitude': lng_float
                        }
                    else:
                        logger.warning(f"Invalid coordinate ranges: lat={lat_float}, lng={lng_float}")
                        del event_data['coordinates']
                except (ValueError, TypeError):
                    logger.warning(f"Invalid coordinate values: lat={lat}, lng={lng}")
                    del event_data['coordinates']
            else:
                logger.warning("Coordinates missing latitude or longitude")
                del event_data['coordinates']
        else:
            logger.warning("Coordinates should be a dictionary with latitude and longitude")
            del event_data['coordinates']

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
        'json': 'json',
        'html': 'html',
        'fallback': 'html_fallback',
        'css': 'html',
        'selector': 'html'
    }

    return method_map.get(method.lower(), 'unknown')


def validate_required_fields(event_data: Dict[str, Any], required_fields: List[str]) -> bool:
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
        'title': 0.2,
        'url': 0.15,
        'date': 0.15,
        'location': 0.1,
        'full_address': 0.05,
        'city': 0.05,
        'country': 0.05,
        'coordinates': 0.05,
        'timezone': 0.05,
        'end_date': 0.05,
        'event_type': 0.03,
        'visibility': 0.02,
        'organizer': 0.05,
        'description': 0.05,
        'cover_url': 0.02,
        'api_id': 0.02,
        'guest_count': 0.01
    }

    total_weight = 0
    achieved_weight = 0

    for field, weight in field_weights.items():
        total_weight += weight
        if field in event_data and event_data[field]:
            achieved_weight += weight

    return achieved_weight / total_weight if total_weight > 0 else 0.0
````

## File: tests/test_extractors.py
````python
"""
Comprehensive tests for JSON extractor functionality.

This module tests the JSON extraction logic for Luma event data,
including pattern matching, data parsing, and error handling.
"""

import unittest
import json
from unittest.mock import Mock, patch
from show_up.extractors.json_extractor import JsonExtractor
from show_up.extractors.base import BaseExtractor, MultiExtractor


class TestJsonExtractor(unittest.TestCase):
    """Test the JsonExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.extractor = JsonExtractor()

        # Sample event data that would be found in Luma pages
        self.sample_event_data = {
            "api_id": "evt-test123",
            "name": "Test Event",
            "start_at": "2025-07-21T22:30:00.000Z",
            "end_at": "2025-07-22T01:00:00.000Z",
            "timezone": "America/Buenos_Aires",
            "event_type": "independent",
            "visibility": "public",
            "url": "test-event",
            "cover_url": "https://example.com/cover.jpg",
            "geo_address_info": {
                "address": "Test Address 123",
                "city": "Buenos Aires",
                "country": "Argentina",
                "full_address": "Test Address 123, Buenos Aires, Argentina",
                "place_id": "ChIJ_test123"
            },
            "coordinate": {
                "latitude": -34.6037,
                "longitude": -58.3816
            },
            "user": {
                "name": "Test Organizer"
            },
            "description": "Test event description"
        }

    def test_can_extract_with_json_indicators(self):
        """Test can_extract returns True for content with JSON indicators."""
        html_with_json = '''
        <html>
            <body>
                <script>
                    window.__INITIAL_DATA__ = {"event": {"name": "Test"}};
                </script>
            </body>
        </html>
        '''

        self.assertTrue(self.extractor.can_extract(html_with_json))

    def test_can_extract_without_json_indicators(self):
        """Test can_extract returns False for content without JSON indicators."""
        html_without_json = '''
        <html>
            <body>
                <h1>Test Page</h1>
                <p>No JSON data here</p>
            </body>
        </html>
        '''

        self.assertFalse(self.extractor.can_extract(html_without_json))

    def test_can_extract_with_empty_content(self):
        """Test can_extract handles empty content gracefully."""
        self.assertFalse(self.extractor.can_extract(""))
        self.assertFalse(self.extractor.can_extract(None))

    def test_extract_with_direct_event_pattern(self):
        """Test extraction with direct event object pattern."""
        html_content = f'''
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(self.sample_event_data)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content, url="https://lu.ma/test")

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], "Test Event")
        self.assertEqual(result['date'], "2025-07-21T22:30:00.000Z")
        self.assertEqual(result['location'], "Test Address 123, Buenos Aires, Argentina")
        self.assertEqual(result['extraction_method'], 'json')

    def test_extract_with_initial_data_pattern(self):
        """Test extraction with window.__INITIAL_DATA__ pattern."""
        html_content = f'''
        <html>
            <body>
                <script>
                    window.__INITIAL_DATA__ = {{"event": {json.dumps(self.sample_event_data)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content, url="https://lu.ma/test")

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], "Test Event")
        self.assertEqual(result['api_id'], "evt-test123")
        self.assertEqual(result['event_type'], "independent")

    def test_extract_with_nested_event_data(self):
        """Test extraction with nested event data structure."""
        nested_data = {
            "props": {
                "event": self.sample_event_data
            }
        }

        html_content = f'''
        <html>
            <body>
                <script>
                    window.__INITIAL_DATA__ = {json.dumps(nested_data)};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], "Test Event")
        self.assertEqual(result['timezone'], "America/Buenos_Aires")

    def test_extract_location_data(self):
        """Test comprehensive location data extraction."""
        html_content = f'''
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(self.sample_event_data)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        self.assertEqual(result['location'], "Test Address 123, Buenos Aires, Argentina")
        self.assertEqual(result['full_address'], "Test Address 123, Buenos Aires, Argentina")
        self.assertEqual(result['city'], "Buenos Aires")
        self.assertEqual(result['country'], "Argentina")
        self.assertEqual(result['place_id'], "ChIJ_test123")

        # Check coordinates
        self.assertIn('coordinates', result)
        self.assertEqual(result['coordinates']['latitude'], -34.6037)
        self.assertEqual(result['coordinates']['longitude'], -58.3816)

    def test_extract_with_url_construction(self):
        """Test URL construction from event data."""
        html_content = f'''
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(self.sample_event_data)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        self.assertEqual(result['url'], "https://lu.ma/test-event")

    def test_extract_with_malformed_json(self):
        """Test handling of malformed JSON."""
        html_content = '''
        <html>
            <body>
                <script>
                    var data = {"event": {"name": "Test Event", "invalid": }};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNone(result)

    def test_extract_with_no_event_data(self):
        """Test extraction when no event data is present."""
        html_content = '''
        <html>
            <body>
                <script>
                    var data = {"user": {"name": "Test User"}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNone(result)

    def test_clean_json_string(self):
        """Test JSON string cleaning functionality."""
        # Test HTML entity cleaning
        dirty_json = '{"name": "Test &quot;Event&quot;", "location": "Test &amp; Place"}'
        cleaned = self.extractor._clean_json_string(dirty_json)
        self.assertIn('"Test "Event""', cleaned)
        self.assertIn('"Test & Place"', cleaned)

        # Test whitespace removal
        whitespace_json = '  {"name": "Test"}  '
        cleaned = self.extractor._clean_json_string(whitespace_json)
        self.assertEqual(cleaned, '{"name": "Test"}')

        # Test comment removal
        comment_json = '{"name": "Test", /* comment */ "id": 1}'
        cleaned = self.extractor._clean_json_string(comment_json)
        self.assertNotIn('/*', cleaned)
        self.assertNotIn('*/', cleaned)

    def test_validate_extracted_data(self):
        """Test validation of extracted data."""
        # Valid data
        valid_data = {
            'title': 'Test Event',
            'date': '2025-07-21T22:30:00.000Z',
            'location': 'Test Location'
        }

        self.assertTrue(self.extractor.validate_extracted_data(valid_data))

        # Invalid data - missing title
        invalid_data = {
            'date': '2025-07-21T22:30:00.000Z',
            'location': 'Test Location'
        }

        self.assertFalse(self.extractor.validate_extracted_data(invalid_data))

        # Invalid data - malformed date
        invalid_date_data = {
            'title': 'Test Event',
            'date': 'invalid-date-format',
            'location': 'Test Location'
        }

        self.assertFalse(self.extractor.validate_extracted_data(invalid_date_data))

    def test_get_extraction_method(self):
        """Test extraction method name."""
        self.assertEqual(self.extractor.get_extraction_method(), 'json')

    def test_custom_patterns_in_config(self):
        """Test custom patterns from configuration."""
        custom_patterns = [
            r'customPattern:\s*({.*?})',
            r'specialData\s*=\s*({.*?});'
        ]

        extractor = JsonExtractor(config={'custom_patterns': custom_patterns})

        # Check that custom patterns are added
        self.assertEqual(len(extractor.patterns), len(JsonExtractor.JSON_PATTERNS) + 2)
        self.assertIn(custom_patterns[0], extractor.patterns)
        self.assertIn(custom_patterns[1], extractor.patterns)

    def test_extraction_with_minimal_event_data(self):
        """Test extraction with minimal event data."""
        minimal_event = {
            "name": "Minimal Event",
            "start_at": "2025-07-21T22:30:00.000Z"
        }

        html_content = f'''
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(minimal_event)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], "Minimal Event")
        self.assertEqual(result['date'], "2025-07-21T22:30:00.000Z")
        self.assertEqual(result['extraction_method'], 'json')

    def test_extraction_with_alternative_organizer_field(self):
        """Test extraction with alternative organizer field names."""
        event_data = self.sample_event_data.copy()
        event_data['organizer'] = {'name': 'Alternative Organizer'}
        del event_data['user']

        html_content = f'''
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(event_data)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        # Should not extract organizer from this structure in current implementation
        self.assertNotIn('organizer', result)

    def test_extraction_with_guest_count_alternatives(self):
        """Test extraction with different guest count field names."""
        event_data = self.sample_event_data.copy()
        event_data['rsvp_count'] = 42

        html_content = f'''
        <html>
            <body>
                <script>
                    var data = {{"event": {json.dumps(event_data)}}};
                </script>
            </body>
        </html>
        '''

        result = self.extractor.extract(html_content)

        self.assertIsNotNone(result)
        self.assertEqual(result['guest_count'], 42)


class TestBaseExtractor(unittest.TestCase):
    """Test the BaseExtractor abstract class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a concrete implementation for testing
        class TestExtractor(BaseExtractor):
            def extract(self, content, **kwargs):
                if "test_data" in content:
                    return {"title": "Test Event", "extraction_method": "test"}
                return None

            def can_extract(self, content):
                return "test_data" in content

        self.extractor = TestExtractor()

    def test_get_extraction_method(self):
        """Test extraction method name generation."""
        self.assertEqual(self.extractor.get_extraction_method(), 'test')

    def test_validate_extracted_data_with_valid_data(self):
        """Test validation with valid data."""
        valid_data = {"title": "Test Event", "url": "https://test.com"}
        self.assertTrue(self.extractor.validate_extracted_data(valid_data))

    def test_validate_extracted_data_with_invalid_data(self):
        """Test validation with invalid data."""
        invalid_data = "not a dictionary"
        self.assertFalse(self.extractor.validate_extracted_data(invalid_data))

    def test_validate_extracted_data_with_required_fields(self):
        """Test validation with required fields configuration."""
        # Use the concrete TestExtractor instead of abstract BaseExtractor
        class TestExtractorWithConfig(BaseExtractor):
            def extract(self, content, **kwargs):
                return {"title": "Test Event"}

            def can_extract(self, content):
                return True

        extractor = TestExtractorWithConfig(config={'required_fields': ['title', 'url']})

        # Valid data with all required fields
        valid_data = {"title": "Test Event", "url": "https://test.com"}
        self.assertTrue(extractor.validate_extracted_data(valid_data))

        # Invalid data missing required field
        invalid_data = {"title": "Test Event"}
        self.assertFalse(extractor.validate_extracted_data(invalid_data))

    def test_log_extraction_result(self):
        """Test extraction result logging."""
        with patch.object(self.extractor, 'logger') as mock_logger:
            # Test successful extraction
            self.extractor.log_extraction_result(True, {"title": "Test"})
            mock_logger.info.assert_called()

            # Test failed extraction
            self.extractor.log_extraction_result(False)
            mock_logger.warning.assert_called()


class TestMultiExtractor(unittest.TestCase):
    """Test the MultiExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock extractors
        self.mock_extractor1 = Mock(spec=BaseExtractor)
        self.mock_extractor2 = Mock(spec=BaseExtractor)

        self.multi_extractor = MultiExtractor([self.mock_extractor1, self.mock_extractor2])

    def test_extract_with_first_extractor_success(self):
        """Test extraction when first extractor succeeds."""
        # Configure first extractor to succeed
        self.mock_extractor1.can_extract.return_value = True
        self.mock_extractor1.extract.return_value = {"title": "Test Event"}
        self.mock_extractor1.validate_extracted_data.return_value = True
        self.mock_extractor1.get_extraction_method.return_value = "test1"
        self.mock_extractor1.log_extraction_result = Mock()

        # Second extractor should not be called
        self.mock_extractor2.can_extract.return_value = False

        result = self.multi_extractor.extract("test content")

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], "Test Event")
        self.assertEqual(result['extraction_method'], "test1")

        # Verify only first extractor was used
        self.mock_extractor1.can_extract.assert_called_once()
        self.mock_extractor1.extract.assert_called_once()
        self.mock_extractor2.can_extract.assert_not_called()

    def test_extract_with_fallback_to_second_extractor(self):
        """Test extraction falling back to second extractor."""
        # Configure first extractor to fail
        self.mock_extractor1.can_extract.return_value = True
        self.mock_extractor1.extract.return_value = None
        self.mock_extractor1.validate_extracted_data.return_value = False
        self.mock_extractor1.get_extraction_method.return_value = "test1"
        self.mock_extractor1.log_extraction_result = Mock()

        # Configure second extractor to succeed
        self.mock_extractor2.can_extract.return_value = True
        self.mock_extractor2.extract.return_value = {"title": "Test Event 2"}
        self.mock_extractor2.validate_extracted_data.return_value = True
        self.mock_extractor2.get_extraction_method.return_value = "test2"
        self.mock_extractor2.log_extraction_result = Mock()

        result = self.multi_extractor.extract("test content")

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], "Test Event 2")
        self.assertEqual(result['extraction_method'], "test2")

        # Verify both extractors were tried
        self.mock_extractor1.can_extract.assert_called_once()
        self.mock_extractor1.extract.assert_called_once()
        self.mock_extractor2.can_extract.assert_called_once()
        self.mock_extractor2.extract.assert_called_once()

    def test_extract_with_all_extractors_failing(self):
        """Test extraction when all extractors fail."""
        # Configure both extractors to fail
        self.mock_extractor1.can_extract.return_value = False
        self.mock_extractor2.can_extract.return_value = False

        result = self.multi_extractor.extract("test content")

        self.assertIsNone(result)

    def test_extract_with_extractor_exception(self):
        """Test extraction when extractor raises exception."""
        # Configure first extractor to raise exception
        self.mock_extractor1.can_extract.return_value = True
        self.mock_extractor1.extract.side_effect = Exception("Test error")
        self.mock_extractor1.log_extraction_result = Mock()

        # Configure second extractor to succeed
        self.mock_extractor2.can_extract.return_value = True
        self.mock_extractor2.extract.return_value = {"title": "Test Event 2"}
        self.mock_extractor2.validate_extracted_data.return_value = True
        self.mock_extractor2.get_extraction_method.return_value = "test2"
        self.mock_extractor2.log_extraction_result = Mock()

        result = self.multi_extractor.extract("test content")

        self.assertIsNotNone(result)
        self.assertEqual(result['title'], "Test Event 2")

        # Verify exception was handled and second extractor was used
        self.mock_extractor1.log_extraction_result.assert_called_with(False)
        self.mock_extractor2.extract.assert_called_once()

    def test_get_available_extractors(self):
        """Test getting list of available extractors."""
        self.mock_extractor1.get_extraction_method.return_value = "test1"
        self.mock_extractor2.get_extraction_method.return_value = "test2"

        extractors = self.multi_extractor.get_available_extractors()

        self.assertEqual(extractors, ["test1", "test2"])


if __name__ == '__main__':
    unittest.main()
````

## File: tests/test_utils.py
````python
"""
Comprehensive tests for validation utilities.

This module tests the data validation and cleaning functions used
throughout the Show Up Crawler, ensuring data quality and consistency.
"""

import unittest
from datetime import datetime
from show_up.utils.validation import (
    validate_event_data, clean_event_data, normalize_extraction_method,
    validate_required_fields, get_data_completeness_score
)


class TestValidateEventData(unittest.TestCase):
    """Test the validate_event_data function."""

    def test_validate_valid_event_data(self):
        """Test validation with valid event data."""
        valid_data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test-event',
            'date': '2025-07-21T22:30:00.000Z',
            'location': 'Test Location',
            'city': 'Buenos Aires',
            'country': 'Argentina'
        }

        result = validate_event_data(valid_data)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['title'], 'Test Event')
        self.assertEqual(result['url'], 'https://lu.ma/test-event')

    def test_validate_with_missing_required_fields(self):
        """Test validation with missing required fields."""
        invalid_data = {
            'date': '2025-07-21T22:30:00.000Z',
            'location': 'Test Location'
        }

        with self.assertRaises(ValueError) as context:
            validate_event_data(invalid_data)

        self.assertIn('Required field', str(context.exception))

    def test_validate_with_empty_required_fields(self):
        """Test validation with empty required fields."""
        invalid_data = {
            'title': '',
            'url': 'https://lu.ma/test-event',
            'date': '2025-07-21T22:30:00.000Z'
        }

        with self.assertRaises(ValueError) as context:
            validate_event_data(invalid_data)

        self.assertIn('title', str(context.exception))

    def test_validate_with_non_dict_input(self):
        """Test validation with non-dictionary input."""
        with self.assertRaises(ValueError) as context:
            validate_event_data("not a dictionary")

        self.assertIn('must be a dictionary', str(context.exception))

    def test_validate_with_coordinates(self):
        """Test validation with coordinate data."""
        data_with_coords = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test-event',
            'coordinates': {
                'latitude': -34.6037,
                'longitude': -58.3816
            }
        }

        result = validate_event_data(data_with_coords)

        self.assertIn('coordinates', result)
        self.assertEqual(result['coordinates']['latitude'], -34.6037)
        self.assertEqual(result['coordinates']['longitude'], -58.3816)

    def test_validate_with_invalid_coordinates(self):
        """Test validation with invalid coordinate data."""
        data_with_invalid_coords = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test-event',
            'coordinates': {
                'latitude': 999,  # Invalid latitude
                'longitude': -58.3816
            }
        }

        result = validate_event_data(data_with_invalid_coords)

        # Invalid coordinates should be removed
        self.assertNotIn('coordinates', result)

    def test_validate_with_malformed_url(self):
        """Test validation with malformed URLs."""
        data_with_partial_url = {
            'title': 'Test Event',
            'url': '/test-event',  # Partial URL
            'date': '2025-07-21T22:30:00.000Z'
        }

        result = validate_event_data(data_with_partial_url)

        # URL should be normalized
        self.assertEqual(result['url'], 'https://lu.ma/test-event')

    def test_validate_with_datetime_object(self):
        """Test validation with datetime objects."""
        data_with_datetime = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test-event',
            'date': datetime(2025, 7, 21, 22, 30, 0)
        }

        result = validate_event_data(data_with_datetime)

        # Datetime should be converted to ISO string
        self.assertIsInstance(result['date'], str)
        self.assertIn('2025-07-21T22:30:00', result['date'])


class TestCleanEventData(unittest.TestCase):
    """Test the clean_event_data function."""

    def test_clean_with_empty_strings(self):
        """Test cleaning with empty strings."""
        dirty_data = {
            'title': 'Test Event',
            'empty_field': '',
            'whitespace_field': '   ',
            'null_field': None,
            'valid_field': 'Valid Value'
        }

        result = clean_event_data(dirty_data)

        self.assertIn('title', result)
        self.assertIn('valid_field', result)
        self.assertNotIn('empty_field', result)
        self.assertNotIn('whitespace_field', result)
        self.assertNotIn('null_field', result)

    def test_clean_with_whitespace_strings(self):
        """Test cleaning with whitespace in strings."""
        dirty_data = {
            'title': '  Test Event  ',
            'location': '\n  Test Location  \t'
        }

        result = clean_event_data(dirty_data)

        self.assertEqual(result['title'], 'Test Event')
        self.assertEqual(result['location'], 'Test Location')

    def test_clean_with_non_string_values(self):
        """Test cleaning with non-string values."""
        dirty_data = {
            'title': 'Test Event',
            'guest_count': 42,
            'coordinates': {'lat': -34.6037, 'lng': -58.3816},
            'tags': ['crypto', 'blockchain'],
            'zero_value': 0,
            'false_value': False
        }

        result = clean_event_data(dirty_data)

        self.assertEqual(result['title'], 'Test Event')
        self.assertEqual(result['guest_count'], 42)
        self.assertEqual(result['coordinates'], {'lat': -34.6037, 'lng': -58.3816})
        self.assertEqual(result['tags'], ['crypto', 'blockchain'])
        # Zero and False should be removed as they're falsy
        self.assertNotIn('zero_value', result)
        self.assertNotIn('false_value', result)

    def test_clean_preserves_empty_dict(self):
        """Test that cleaning handles empty dictionaries."""
        result = clean_event_data({})
        self.assertEqual(result, {})


class TestNormalizeExtractionMethod(unittest.TestCase):
    """Test the normalize_extraction_method function."""

    def test_normalize_known_methods(self):
        """Test normalization of known extraction methods."""
        test_cases = [
            ('json', 'json'),
            ('JSON', 'json'),
            ('html', 'html'),
            ('HTML', 'html'),
            ('fallback', 'html_fallback'),
            ('css', 'html'),
            ('selector', 'html')
        ]

        for input_method, expected in test_cases:
            result = normalize_extraction_method(input_method)
            self.assertEqual(result, expected)

    def test_normalize_unknown_method(self):
        """Test normalization of unknown extraction methods."""
        result = normalize_extraction_method('unknown_method')
        self.assertEqual(result, 'unknown')

    def test_normalize_empty_method(self):
        """Test normalization of empty extraction method."""
        result = normalize_extraction_method('')
        self.assertEqual(result, 'unknown')


class TestValidateRequiredFields(unittest.TestCase):
    """Test the validate_required_fields function."""

    def test_validate_with_all_required_fields_present(self):
        """Test validation when all required fields are present."""
        data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'date': '2025-07-21T22:30:00.000Z'
        }

        result = validate_required_fields(data, ['title', 'url'])
        self.assertTrue(result)

    def test_validate_with_missing_required_fields(self):
        """Test validation when required fields are missing."""
        data = {
            'title': 'Test Event',
            'date': '2025-07-21T22:30:00.000Z'
        }

        result = validate_required_fields(data, ['title', 'url'])
        self.assertFalse(result)

    def test_validate_with_empty_required_fields(self):
        """Test validation when required fields are empty."""
        data = {
            'title': '',
            'url': 'https://lu.ma/test'
        }

        result = validate_required_fields(data, ['title', 'url'])
        self.assertFalse(result)

    def test_validate_with_no_required_fields(self):
        """Test validation when no fields are required."""
        data = {'title': 'Test Event'}
        result = validate_required_fields(data, [])
        self.assertTrue(result)


class TestGetDataCompletenessScore(unittest.TestCase):
    """Test the get_data_completeness_score function."""

    def test_completeness_score_with_minimal_data(self):
        """Test completeness score with minimal data."""
        minimal_data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test'
        }

        score = get_data_completeness_score(minimal_data)
        self.assertGreater(score, 0)
        self.assertLess(score, 1)

    def test_completeness_score_with_comprehensive_data(self):
        """Test completeness score with comprehensive data."""
        comprehensive_data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'date': '2025-07-21T22:30:00.000Z',
            'end_date': '2025-07-22T01:00:00.000Z',
            'timezone': 'America/Buenos_Aires',
            'location': 'Test Location',
            'full_address': 'Test Address 123, Buenos Aires, Argentina',
            'city': 'Buenos Aires',
            'country': 'Argentina',
            'coordinates': {'latitude': -34.6037, 'longitude': -58.3816},
            'event_type': 'independent',
            'visibility': 'public',
            'organizer': 'Test Organizer',
            'description': 'Test event description',
            'cover_url': 'https://example.com/cover.jpg',
            'api_id': 'evt-test123',
            'guest_count': 42
        }

        score = get_data_completeness_score(comprehensive_data)
        self.assertGreater(score, 0.8)  # Should be high score
        self.assertLessEqual(score, 1.0)

    def test_completeness_score_with_empty_data(self):
        """Test completeness score with empty data."""
        empty_data = {}
        score = get_data_completeness_score(empty_data)
        self.assertEqual(score, 0.0)

    def test_completeness_score_with_weighted_fields(self):
        """Test that higher-weight fields contribute more to score."""
        # Data with only high-weight fields
        high_weight_data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'date': '2025-07-21T22:30:00.000Z',
            'location': 'Test Location'
        }

        # Data with only low-weight fields
        low_weight_data = {
            'api_id': 'evt-test123',
            'guest_count': 42,
            'cover_url': 'https://example.com/cover.jpg'
        }

        high_score = get_data_completeness_score(high_weight_data)
        low_score = get_data_completeness_score(low_weight_data)

        self.assertGreater(high_score, low_score)


class TestUrlValidation(unittest.TestCase):
    """Test URL validation and normalization."""

    def test_url_with_missing_protocol(self):
        """Test URL normalization when protocol is missing."""
        data = {
            'title': 'Test Event',
            'url': 'lu.ma/test-event'
        }

        result = validate_event_data(data)
        self.assertEqual(result['url'], 'https://lu.ma/test-event')

    def test_url_with_relative_path(self):
        """Test URL normalization with relative paths."""
        data = {
            'title': 'Test Event',
            'url': '/test-event'
        }

        result = validate_event_data(data)
        self.assertEqual(result['url'], 'https://lu.ma/test-event')

    def test_url_with_protocol_relative(self):
        """Test URL normalization with protocol-relative URLs."""
        data = {
            'title': 'Test Event',
            'url': '//lu.ma/test-event'
        }

        result = validate_event_data(data)
        self.assertEqual(result['url'], 'https://lu.ma/test-event')

    def test_url_with_complete_url(self):
        """Test that complete URLs are preserved."""
        data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test-event'
        }

        result = validate_event_data(data)
        self.assertEqual(result['url'], 'https://lu.ma/test-event')


class TestDateValidation(unittest.TestCase):
    """Test date validation and normalization."""

    def test_date_with_iso_format(self):
        """Test date validation with ISO format."""
        data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'date': '2025-07-21T22:30:00.000Z'
        }

        result = validate_event_data(data)
        self.assertEqual(result['date'], '2025-07-21T22:30:00.000Z')

    def test_date_with_alternative_formats(self):
        """Test date validation with alternative formats."""
        test_cases = [
            ('2025-07-21 22:30:00', '2025-07-21T22:30:00'),
            ('2025-07-21', '2025-07-21T00:00:00'),
            ('21/07/2025', '2025-07-21T00:00:00'),
            ('07/21/2025', '2025-07-21T00:00:00')
        ]

        for input_date, expected_start in test_cases:
            data = {
                'title': 'Test Event',
                'url': 'https://lu.ma/test',
                'date': input_date
            }

            result = validate_event_data(data)
            self.assertTrue(result['date'].startswith(expected_start))

    def test_date_with_invalid_format(self):
        """Test date validation with invalid format."""
        data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'date': 'invalid-date-format'
        }

        # Should not raise exception, just keep original value
        result = validate_event_data(data)
        self.assertEqual(result['date'], 'invalid-date-format')


class TestLocationValidation(unittest.TestCase):
    """Test location validation and normalization."""

    def test_location_with_extra_whitespace(self):
        """Test location cleaning with extra whitespace."""
        data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'location': '  Buenos Aires,    Argentina  ',
            'full_address': '\n\n  Test Address 123  \t\t'
        }

        result = validate_event_data(data)
        self.assertEqual(result['location'], 'Buenos Aires, Argentina')
        self.assertEqual(result['full_address'], 'Test Address 123')

    def test_location_with_multiple_spaces(self):
        """Test location cleaning with multiple spaces."""
        data = {
            'title': 'Test Event',
            'url': 'https://lu.ma/test',
            'location': 'Buenos  Aires,     Argentina'
        }

        result = validate_event_data(data)
        self.assertEqual(result['location'], 'Buenos Aires, Argentina')


if __name__ == '__main__':
    unittest.main()
````

## File: enhanced_extraction_results.json
````json
{
  "metadata": {
    "test_script": "test_enhanced_extraction.py",
    "test_time": "2025-07-17T23:56:06.520732",
    "total_files": 8,
    "successful_extractions": 8
  },
  "results": [
    {
      "file": "AllstarsAR_-_La_Plata_-__Staking_y_Consenso.html",
      "extraction_success": true,
      "extraction_method": "json",
      "extraction_pattern": 0,
      "title": "AllstarsAR - La Plata -  Staking y Consenso",
      "date": "2025-07-25T23:00:00.000Z",
      "location": "Bye Henry Diagonal, La Plata, Argentina",
      "completeness_score": 0.9,
      "field_count": 16,
      "data": {
        "title": "AllstarsAR - La Plata -  Staking y Consenso",
        "api_id": "evt-QLMUhrholYZT2zw",
        "event_type": "independent",
        "visibility": "public",
        "date": "2025-07-25T23:00:00.000Z",
        "end_date": "2025-07-26T01:30:00.000Z",
        "timezone": "America/Buenos_Aires",
        "location": "Bye Henry Diagonal, La Plata, Argentina",
        "full_address": "Bye Henry Diagonal, Diag. 74 1629, B1900 La Plata, Provincia de Buenos Aires, Argentina",
        "city": "La Plata",
        "country": "Argentina",
        "place_id": "ChIJ6wt6Jg7nopURLl3iyRC8txM",
        "coordinates": {
          "latitude": -34.9181589,
          "longitude": -57.95503979999999
        },
        "cover_url": "https://images.lumacdn.com/event-covers/o3/f67cbc02-1487-48ca-a7f2-0c1a5a161c17.png",
        "url": "https://lu.ma/AllstarsAR_-_La_Plata_-__Staking_y_Consenso",
        "extraction_method": "json"
      }
    },
    {
      "file": "Workshop_AllstarsAR__Artistas.html",
      "extraction_success": true,
      "extraction_method": "json",
      "extraction_pattern": 0,
      "title": "Workshop AllstarsAR + Artistas",
      "date": "2025-07-31T23:00:00.000Z",
      "location": "Centro Cultural Musicleta, Buenos Aires, Argentina",
      "completeness_score": 0.9,
      "field_count": 16,
      "data": {
        "title": "Workshop AllstarsAR + Artistas",
        "api_id": "evt-Xr14BchvJKJJOPN",
        "event_type": "independent",
        "visibility": "public",
        "date": "2025-07-31T23:00:00.000Z",
        "end_date": "2025-08-01T01:30:00.000Z",
        "timezone": "America/Buenos_Aires",
        "location": "Centro Cultural Musicleta, Buenos Aires, Argentina",
        "full_address": "Centro Cultural Musicleta, Aguirre 489, C1414ASI Cdad. Autónoma de Buenos Aires, Argentina",
        "city": "Buenos Aires",
        "country": "Argentina",
        "place_id": "ChIJFXcpCHTKvJURSfZ9ubzK988",
        "coordinates": {
          "latitude": -34.59793459999999,
          "longitude": -58.43524559999999
        },
        "cover_url": "https://images.lumacdn.com/event-covers/34/6c558543-ef10-4df1-8e14-6c1c349aa06d.png",
        "url": "https://lu.ma/Workshop_AllstarsAR__Artistas",
        "extraction_method": "json"
      }
    },
    {
      "file": "The_Path_to_Solana_-_CoWorking_Day.html",
      "extraction_success": true,
      "extraction_method": "json",
      "extraction_pattern": 0,
      "title": "The Path to Solana - CoWorking Day",
      "date": "2025-07-18T13:00:00.000Z",
      "location": "No location",
      "completeness_score": 0.6727272727272727,
      "field_count": 11,
      "data": {
        "title": "The Path to Solana - CoWorking Day",
        "api_id": "evt-uhOaYrJQWCvzDEL",
        "event_type": "independent",
        "visibility": "public",
        "date": "2025-07-18T13:00:00.000Z",
        "end_date": "2025-07-18T21:00:00.000Z",
        "timezone": "America/Buenos_Aires",
        "coordinates": {
          "latitude": -34.59,
          "longitude": -58.44
        },
        "cover_url": "https://images.lumacdn.com/event-covers/2r/cc13699c-44e9-40bb-8b93-d14ef6170284.png",
        "url": "https://lu.ma/The_Path_to_Solana_-_CoWorking_Day",
        "extraction_method": "json"
      }
    },
    {
      "file": "Aprendé_a_usar_Bitcoin_desde_cero.html",
      "extraction_success": true,
      "extraction_method": "json",
      "extraction_pattern": 0,
      "title": "Aprendé a usar Bitcoin desde cero",
      "date": "2025-07-29T21:00:00.000Z",
      "location": "Espacio Cultural Bitcoin, AAC, Argentina",
      "completeness_score": 0.9,
      "field_count": 16,
      "data": {
        "title": "Aprendé a usar Bitcoin desde cero",
        "api_id": "evt-FGpkH3XLbiopkEI",
        "event_type": "independent",
        "visibility": "public",
        "date": "2025-07-29T21:00:00.000Z",
        "end_date": "2025-08-12T21:00:00.000Z",
        "timezone": "America/Buenos_Aires",
        "location": "Espacio Cultural Bitcoin, AAC, Argentina",
        "full_address": "Espacio Cultural Bitcoin, Marcelo Torcuato de Alvear 405, C1058 AAC, Cdad. Autónoma de Buenos Aires, Argentina",
        "city": "AAC",
        "country": "Argentina",
        "place_id": "ChIJ2awZlcrKvJURgXJHvt5f80A",
        "coordinates": {
          "latitude": -34.5961172,
          "longitude": -58.3732859
        },
        "cover_url": "https://images.lumacdn.com/event-covers/pj/94b71cc8-d566-44ed-a485-70e30c1ac091.png",
        "url": "https://lu.ma/Aprendé_a_usar_Bitcoin_desde_cero",
        "extraction_method": "json"
      }
    },
    {
      "file": "ZKsync_LATAM_Coworking_Day__Aleph_Hub.html",
      "extraction_success": true,
      "extraction_method": "json",
      "extraction_pattern": 0,
      "title": "ZKsync LATAM Coworking Day @ Aleph Hub",
      "date": "2025-07-17T13:30:00.000Z",
      "location": "Aleph Hub, C1426DGG, Argentina",
      "completeness_score": 0.9,
      "field_count": 16,
      "data": {
        "title": "ZKsync LATAM Coworking Day @ Aleph Hub",
        "api_id": "evt-4cHxxyOeqLLF6b9",
        "event_type": "independent",
        "visibility": "public",
        "date": "2025-07-17T13:30:00.000Z",
        "end_date": "2025-07-17T20:00:00.000Z",
        "timezone": "America/Buenos_Aires",
        "location": "Aleph Hub, C1426DGG, Argentina",
        "full_address": "Aleph Hub, Concepción Arenal 2989, C1426DGG C1426DGG, Cdad. Autónoma de Buenos Aires, Argentina",
        "city": "C1426DGG",
        "country": "Argentina",
        "place_id": "ChIJKUdKagC1vJUR7Pc_T5nXIjo",
        "coordinates": {
          "latitude": -34.5790647,
          "longitude": -58.4426517
        },
        "cover_url": "https://images.lumacdn.com/event-covers/wi/5ef56dc7-56c0-4a6e-bf29-98fbad7d03e9.png",
        "url": "https://lu.ma/ZKsync_LATAM_Coworking_Day__Aleph_Hub",
        "extraction_method": "json"
      }
    },
    {
      "file": "21MeetUp__JULIO.html",
      "extraction_success": true,
      "extraction_method": "json",
      "extraction_pattern": 0,
      "title": "21MeetUp | JULIO 🧡🚀",
      "date": "2025-07-21T22:30:00.000Z",
      "location": "Club de la Birra Colegiales, Buenos Aires, Argentina",
      "completeness_score": 0.9,
      "field_count": 16,
      "data": {
        "title": "21MeetUp | JULIO 🧡🚀",
        "api_id": "evt-yKMLCEcEELikdzY",
        "event_type": "independent",
        "visibility": "public",
        "date": "2025-07-21T22:30:00.000Z",
        "end_date": "2025-07-22T01:00:00.000Z",
        "timezone": "America/Buenos_Aires",
        "location": "Club de la Birra Colegiales, Buenos Aires, Argentina",
        "full_address": "Club de la Birra Colegiales, Zapiola 131, C1426 Cdad. Autónoma de Buenos Aires, Argentina",
        "city": "Buenos Aires",
        "country": "Argentina",
        "place_id": "ChIJ_VCXXm-1vJURJHX-OCx4Pc8",
        "coordinates": {
          "latitude": -34.5788554,
          "longitude": -58.44275679999999
        },
        "cover_url": "https://images.lumacdn.com/event-covers/2z/ac80bc38-0dd7-4e58-90e8-5abd82c6023e.png",
        "url": "https://lu.ma/21MeetUp__JULIO",
        "extraction_method": "json"
      }
    },
    {
      "file": "Ethereum_10_Years_Meetup.html",
      "extraction_success": true,
      "extraction_method": "json",
      "extraction_pattern": 0,
      "title": "Ethereum 10 Years Meetup",
      "date": "2025-07-30T13:00:00.000Z",
      "location": "Aleph Hub, C1426DGG, Argentina",
      "completeness_score": 0.9,
      "field_count": 16,
      "data": {
        "title": "Ethereum 10 Years Meetup",
        "api_id": "evt-nikGYuxmOXOI6oz",
        "event_type": "independent",
        "visibility": "public",
        "date": "2025-07-30T13:00:00.000Z",
        "end_date": "2025-07-30T23:00:00.000Z",
        "timezone": "America/Buenos_Aires",
        "location": "Aleph Hub, C1426DGG, Argentina",
        "full_address": "Aleph Hub, Concepción Arenal 2989, C1426DGG C1426DGG, Cdad. Autónoma de Buenos Aires, Argentina",
        "city": "C1426DGG",
        "country": "Argentina",
        "place_id": "ChIJKUdKagC1vJUR7Pc_T5nXIjo",
        "coordinates": {
          "latitude": -34.579065,
          "longitude": -58.442652
        },
        "cover_url": "https://images.lumacdn.com/event-covers/80/e2984de2-97e2-4ce3-b5d9-54d8f5962fdf.jpg",
        "url": "https://lu.ma/Ethereum_10_Years_Meetup",
        "extraction_method": "json"
      }
    },
    {
      "file": "THE_CREATOR_ECONOMY_VOL_III.html",
      "extraction_success": true,
      "extraction_method": "json",
      "extraction_pattern": 0,
      "title": "THE CREATOR ECONOMY VOL. III",
      "date": "2025-07-18T18:00:00.000Z",
      "location": "Aleph Hub, C1426DGG, Argentina",
      "completeness_score": 0.9,
      "field_count": 16,
      "data": {
        "title": "THE CREATOR ECONOMY VOL. III",
        "api_id": "evt-tNJWiWgfIiFUtTS",
        "event_type": "independent",
        "visibility": "public",
        "date": "2025-07-18T18:00:00.000Z",
        "end_date": "2025-07-18T23:30:00.000Z",
        "timezone": "America/Argentina/Buenos_Aires",
        "location": "Aleph Hub, C1426DGG, Argentina",
        "full_address": "Aleph Hub, Concepción Arenal 2989, C1426DGG C1426DGG, Cdad. Autónoma de Buenos Aires, Argentina",
        "city": "C1426DGG",
        "country": "Argentina",
        "place_id": "ChIJKUdKagC1vJUR7Pc_T5nXIjo",
        "coordinates": {
          "latitude": -34.579065,
          "longitude": -58.442652
        },
        "cover_url": "https://images.lumacdn.com/event-covers/f0/320f4772-8544-4099-9f1e-eef0381c2ca9.jpg",
        "url": "https://lu.ma/THE_CREATOR_ECONOMY_VOL_III",
        "extraction_method": "json"
      }
    }
  ]
}
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
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Extract event data
            extracted_data = extractor.extract(html_content, url=f"https://lu.ma/{html_file.stem}")

            if extracted_data:
                # Validate the data
                try:
                    validated_data = validate_event_data(extracted_data)
                    completeness_score = get_data_completeness_score(validated_data)

                    result = {
                        'file': html_file.name,
                        'extraction_success': True,
                        'extraction_method': extracted_data.get('extraction_method', 'unknown'),
                        'extraction_pattern': extracted_data.get('extraction_pattern', 'unknown'),
                        'title': validated_data.get('title', 'Unknown'),
                        'date': validated_data.get('date', 'No date'),
                        'location': validated_data.get('location', 'No location'),
                        'completeness_score': completeness_score,
                        'field_count': len([v for v in validated_data.values() if v not in [None, '', {}]]),
                        'data': validated_data
                    }

                    print(f"  ✅ Success: {result['title']}")
                    print(f"     📅 Date: {result['date']}")
                    print(f"     📍 Location: {result['location']}")
                    print(f"     🔍 Method: {result['extraction_method']} (pattern {result['extraction_pattern']})")
                    print(f"     📊 Completeness: {completeness_score:.2f} ({result['field_count']} fields)")

                except Exception as e:
                    result = {
                        'file': html_file.name,
                        'extraction_success': True,
                        'validation_error': str(e),
                        'raw_data': extracted_data
                    }
                    print(f"  ⚠️  Extraction succeeded but validation failed: {e}")
            else:
                result = {
                    'file': html_file.name,
                    'extraction_success': False,
                    'error': 'No data extracted'
                }
                print(f"  ❌ Failed to extract data")

            results.append(result)

        except Exception as e:
            result = {
                'file': html_file.name,
                'extraction_success': False,
                'error': str(e)
            }
            results.append(result)
            print(f"  ❌ Error: {e}")

        print()

    # Generate summary report
    generate_summary_report(results)

    # Save detailed results
    save_detailed_results(results)

    return results


def generate_summary_report(results: List[Dict[str, Any]]):
    """Generate a summary report of extraction results."""

    total_files = len(results)
    successful_extractions = len([r for r in results if r.get('extraction_success')])
    failed_extractions = total_files - successful_extractions

    # Calculate statistics for successful extractions
    successful_results = [r for r in results if r.get('extraction_success') and 'completeness_score' in r]

    if successful_results:
        avg_completeness = sum(r['completeness_score'] for r in successful_results) / len(successful_results)
        avg_field_count = sum(r['field_count'] for r in successful_results) / len(successful_results)

        # Method breakdown
        method_counts = {}
        for r in successful_results:
            method = r.get('extraction_method', 'unknown')
            method_counts[method] = method_counts.get(method, 0) + 1

        # Quality breakdown
        high_quality = len([r for r in successful_results if r['completeness_score'] > 0.8])
        medium_quality = len([r for r in successful_results if 0.5 <= r['completeness_score'] <= 0.8])
        low_quality = len([r for r in successful_results if r['completeness_score'] < 0.5])
    else:
        avg_completeness = 0
        avg_field_count = 0
        method_counts = {}
        high_quality = medium_quality = low_quality = 0

    print("=" * 60)
    print("📊 EXTRACTION SUMMARY REPORT")
    print("=" * 60)
    print(f"📁 Total files processed: {total_files}")
    print(f"✅ Successful extractions: {successful_extractions} ({successful_extractions/total_files*100:.1f}%)")
    print(f"❌ Failed extractions: {failed_extractions} ({failed_extractions/total_files*100:.1f}%)")
    print()

    if successful_results:
        print("📈 DATA QUALITY METRICS:")
        print(f"   Average completeness score: {avg_completeness:.3f}")
        print(f"   Average field count: {avg_field_count:.1f}")
        print()

        print("🔍 EXTRACTION METHODS:")
        for method, count in method_counts.items():
            print(f"   {method}: {count} files ({count/len(successful_results)*100:.1f}%)")
        print()

        print("⭐ QUALITY BREAKDOWN:")
        print(f"   High quality (>80%): {high_quality} files ({high_quality/len(successful_results)*100:.1f}%)")
        print(f"   Medium quality (50-80%): {medium_quality} files ({medium_quality/len(successful_results)*100:.1f}%)")
        print(f"   Low quality (<50%): {low_quality} files ({low_quality/len(successful_results)*100:.1f}%)")
        print()

    print("🎯 COMPARISON WITH ORIGINAL CRAWLER:")
    print("   Original completeness: ~25% (titles + URLs only)")
    print(f"   Enhanced completeness: {avg_completeness*100:.1f}% (comprehensive data)")
    print(f"   Improvement factor: {avg_completeness/0.25:.1f}x better")
    print()


def save_detailed_results(results: List[Dict[str, Any]]):
    """Save detailed extraction results to a JSON file."""

    output_file = "enhanced_extraction_results.json"

    output_data = {
        'metadata': {
            'test_script': 'test_enhanced_extraction.py',
            'test_time': datetime.now().isoformat(),
            'total_files': len(results),
            'successful_extractions': len([r for r in results if r.get('extraction_success')]),
        },
        'results': results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
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

    with open(original_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    original_events = original_data.get('events', [])

    print(f"📊 Original extraction results:")
    print(f"   Events: {len(original_events)}")

    # Analyze original data quality
    events_with_dates = len([e for e in original_events if e.get('date')])
    events_with_locations = len([e for e in original_events if e.get('location')])
    events_with_titles = len([e for e in original_events if e.get('title')])

    print(f"   Events with titles: {events_with_titles}/{len(original_events)} ({events_with_titles/len(original_events)*100:.1f}%)")
    print(f"   Events with dates: {events_with_dates}/{len(original_events)} ({events_with_dates/len(original_events)*100:.1f}%)")
    print(f"   Events with locations: {events_with_locations}/{len(original_events)} ({events_with_locations/len(original_events)*100:.1f}%)")

    # Show sample events
    print("\n📄 Sample original events:")
    for i, event in enumerate(original_events[:3]):
        print(f"   {i+1}. {event.get('title', 'No title')}")
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
    results = test_extraction_on_html_files()

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

## File: tests/test_pipelines.py
````python
import unittest
import tempfile
import os
import shutil
import sys
import json
from unittest.mock import Mock, patch
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from show_up.pipelines import RawHtmlFilePipeline, EnhancedJsonPipeline
from show_up.items import EventItem


class TestRawHtmlFilePipeline(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.pipeline = RawHtmlFilePipeline()
        self.pipeline.output_dir = self.test_dir

        # Create a mock spider
        self.spider = Mock()
        self.spider.name = "test_spider"

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_open_spider_creates_directory(self):
        # Test that the pipeline creates the output directory
        self.pipeline.open_spider(self.spider)
        self.assertTrue(os.path.exists(self.test_dir))

    def test_process_item_saves_raw_html(self):
        # Arrange
        item = EventItem()
        item['title'] = "Test Event"
        item['raw_html'] = "<html><head><title>Test</title></head><body><h1>Test Event</h1></body></html>"

        self.pipeline.open_spider(self.spider)

        # Act
        result = self.pipeline.process_item(item, self.spider)

        # Assert
        expected_filename = "Test_Event_raw.html"
        expected_filepath = os.path.join(self.test_dir, expected_filename)

        self.assertTrue(os.path.exists(expected_filepath))

        with open(expected_filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertEqual(content, item['raw_html'])
        self.assertEqual(result, item)

    def test_process_item_sanitizes_filename(self):
        # Test that special characters in title are sanitized
        item = EventItem()
        item['title'] = "Test Event! @#$%^&*()+=[]{}|;:',.<>?/~`"
        item['raw_html'] = "<html><body>Test content</body></html>"

        self.pipeline.open_spider(self.spider)
        result = self.pipeline.process_item(item, self.spider)

        # Should sanitize to only alphanumeric, spaces, and hyphens
        expected_filename = "Test_Event_raw.html"
        expected_filepath = os.path.join(self.test_dir, expected_filename)

        self.assertTrue(os.path.exists(expected_filepath))

    def test_process_item_without_title_or_raw_html(self):
        # Test that items without title or raw_html are handled gracefully
        item = EventItem()
        item['url'] = "https://example.com"

        self.pipeline.open_spider(self.spider)
        result = self.pipeline.process_item(item, self.spider)

        # Should return the item unchanged and not create any files
        self.assertEqual(result, item)
        self.assertEqual(len(os.listdir(self.test_dir)), 0)

    def test_process_item_with_empty_title(self):
        # Test handling of empty title
        item = EventItem()
        item['title'] = ""
        item['raw_html'] = "<html><body>Content</body></html>"

        self.pipeline.open_spider(self.spider)
        result = self.pipeline.process_item(item, self.spider)

        # Should create a file with sanitized empty name
        expected_filename = "_raw.html"
        expected_filepath = os.path.join(self.test_dir, expected_filename)

        self.assertTrue(os.path.exists(expected_filepath))


if __name__ == '__main__':
    unittest.main()

class TestEnhancedJsonPipeline(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory and file for testing
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_events.json")
        self.pipeline = EnhancedJsonPipeline(output_file=self.test_file)

        # Create a mock spider
        self.spider = Mock()
        self.spider.name = "test_spider"
        self.spider.start_urls = ["https://example.com"]

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_from_crawler(self):
        # Test that the pipeline reads settings from crawler
        mock_crawler = Mock()
        mock_settings = {
            'JSON_OUTPUT_FILE': 'custom_output.json',
            'JSON_INDENT': 4,
            'JSON_ENSURE_ASCII': True
        }
        mock_crawler.settings.get = lambda key, default: mock_settings.get(key, default)
        mock_crawler.settings.getint = lambda key, default: mock_settings.get(key, default)
        mock_crawler.settings.getbool = lambda key, default: mock_settings.get(key, default)

        pipeline = EnhancedJsonPipeline.from_crawler(mock_crawler)
        
        self.assertEqual(pipeline.output_file, 'custom_output.json')
        self.assertEqual(pipeline.indent, 4)
        self.assertEqual(pipeline.ensure_ascii, True)

    def test_open_spider_initializes_metadata(self):
        # Test that open_spider initializes metadata correctly
        self.pipeline.open_spider(self.spider)
        
        self.assertIn('spider_name', self.pipeline.metadata)
        self.assertEqual(self.pipeline.metadata['spider_name'], 'test_spider')
        self.assertIn('start_time', self.pipeline.metadata)
        self.assertIn('source', self.pipeline.metadata)
        self.assertEqual(self.pipeline.metadata['source'], 'https://example.com')

    def test_process_item_adds_to_items_list(self):
        # Test that process_item adds items to the items list
        item = EventItem()
        item['title'] = "Test Event"
        item['date'] = "2025-08-01"
        item['location'] = "Test Location"
        item['url'] = "https://example.com/event"
        item['html_content'] = "<html><body>Test content</body></html>"
        item['raw_html'] = "<html><body>Raw test content</body></html>"

        self.pipeline.open_spider(self.spider)
        result = self.pipeline.process_item(item, self.spider)

        # Check that HTML fields are removed
        self.assertEqual(len(self.pipeline.items), 1)
        self.assertNotIn('html_content', self.pipeline.items[0])
        self.assertNotIn('raw_html', self.pipeline.items[0])
        
        # Check that other fields are preserved
        self.assertEqual(self.pipeline.items[0]['title'], "Test Event")
        self.assertEqual(self.pipeline.items[0]['date'], "2025-08-01")
        self.assertEqual(self.pipeline.items[0]['location'], "Test Location")
        self.assertEqual(self.pipeline.items[0]['url'], "https://example.com/event")
        
        # Check that the original item is returned unchanged
        self.assertEqual(result, item)

    def test_process_item_handles_missing_fields(self):
        # Test that process_item handles missing fields
        item = EventItem()
        item['url'] = "https://example.com/event"
        
        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)
        
        # Check that missing fields are added with default values
        self.assertEqual(len(self.pipeline.items), 1)
        self.assertIn('title', self.pipeline.items[0])
        self.assertIn('date', self.pipeline.items[0])
        self.assertIn('location', self.pipeline.items[0])
        self.assertEqual(self.pipeline.items[0]['url'], "https://example.com/event")

    def test_process_item_handles_non_serializable_values(self):
        # Test that process_item handles non-serializable values
        class NonSerializable:
            def __str__(self):
                return "Non-serializable object"
        
        item = EventItem()
        item['title'] = "Test Event"
        item['date'] = NonSerializable()
        item['url'] = "https://example.com/event"
        
        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)
        
        # Check that non-serializable values are converted to strings
        self.assertEqual(len(self.pipeline.items), 1)
        self.assertEqual(self.pipeline.items[0]['title'], "Test Event")
        self.assertEqual(self.pipeline.items[0]['date'], "Non-serializable object")
        self.assertEqual(self.pipeline.items[0]['url'], "https://example.com/event")

    def test_close_spider_writes_json_file(self):
        # Test that close_spider writes a properly formatted JSON file
        item1 = EventItem()
        item1['title'] = "Test Event 1"
        item1['date'] = "2025-08-01"
        item1['url'] = "https://example.com/event1"
        
        item2 = EventItem()
        item2['title'] = "Test Event 2"
        item2['date'] = "2025-08-02"
        item2['url'] = "https://example.com/event2"
        
        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item1, self.spider)
        self.pipeline.process_item(item2, self.spider)
        self.pipeline.close_spider(self.spider)
        
        # Check that the JSON file was created
        self.assertTrue(os.path.exists(self.test_file))
        
        # Check that the JSON file contains the expected structure
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('metadata', data)
        self.assertIn('events', data)
        self.assertIn('end_time', data)
        self.assertIn('event_count', data)
        
        self.assertEqual(data['metadata']['spider_name'], 'test_spider')
        self.assertEqual(len(data['events']), 2)
        self.assertEqual(data['event_count'], 2)
        
        self.assertEqual(data['events'][0]['title'], "Test Event 1")
        self.assertEqual(data['events'][1]['title'], "Test Event 2")

    def test_close_spider_creates_directory_if_needed(self):
        # Test that close_spider creates the output directory if it doesn't exist
        nested_dir = os.path.join(self.test_dir, "nested", "dir")
        nested_file = os.path.join(nested_dir, "test_events.json")
        
        self.pipeline.output_file = nested_file
        
        item = EventItem()
        item['title'] = "Test Event"
        item['url'] = "https://example.com/event"
        
        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item, self.spider)
        self.pipeline.close_spider(self.spider)
        
        # Check that the directory and file were created
        self.assertTrue(os.path.exists(nested_dir))
        self.assertTrue(os.path.exists(nested_file))

    def test_close_spider_handles_file_write_errors(self):
        # Test that close_spider handles file write errors gracefully
        with patch('builtins.open') as mock_open:
            mock_open.side_effect = PermissionError("Permission denied")
            
            item = EventItem()
            item['title'] = "Test Event"
            item['url'] = "https://example.com/event"
            
            self.pipeline.open_spider(self.spider)
            self.pipeline.process_item(item, self.spider)
            
            # This should not raise an exception
            self.pipeline.close_spider(self.spider)
````

## File: .env.local
````
FIRECRAWL_API_KEY="your_firecrawl_api_key"
````

## File: show_up/spiders/__init__.py
````python
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
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

## File: README.md
````markdown
# 🚀 Show Up Crawler

A powerful web crawler for extracting comprehensive crypto event data from Luma (lu.ma) using advanced JSON extraction techniques.

## ✨ Features

- **Enhanced JSON Extraction**: Extracts complete event data from embedded JSON structures
- **High Data Quality**: Achieves 87.2% average completeness vs 25% with basic HTML parsing
- **Comprehensive Event Data**: Dates, locations, coordinates, organizers, and metadata
- **Robust Architecture**: Modular design with fallback mechanisms
- **Playwright Integration**: Handles JavaScript-heavy pages effectively
- **Data Validation**: Comprehensive validation and cleaning of extracted data

## 📊 Performance Metrics

- **100% Success Rate** on tested HTML files
- **3.5x Improvement** in data quality over basic extraction
- **87.2% Average Completeness** with comprehensive field extraction
- **Multiple Extraction Methods** with intelligent fallback

## 🏗️ Architecture

```
Scrapy Spider → Playwright → JsonExtractor → Enhanced EventItem → Enhanced JSON Pipeline → Complete Events JSON
```

### Core Components

- **JsonExtractor**: Advanced JSON pattern matching and extraction
- **Enhanced EventItem**: Comprehensive data model with 15+ fields
- **Enhanced Pipelines**: Data validation, cleaning, and statistics
- **Validation Utils**: Data quality assurance and normalization

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

# Install development dependencies
uv add pytest --dev
```

### Basic Usage

```bash
# Run the crawler
uv run scrapy crawl luma

# Run with custom settings
uv run scrapy crawl luma -s JSON_OUTPUT_FILE=my_events.json

# Test enhanced extraction on existing HTML files
uv run python test_enhanced_extraction.py
```

## 📁 Project Structure

```
show-up-crawler/
├── .agents/                    # Project planning and documentation
├── show_up/                    # Main crawler package
│   ├── extractors/            # Data extraction components
│   │   ├── base.py           # Base extractor interface
│   │   └── json_extractor.py # JSON extraction logic
│   ├── utils/                # Utility functions
│   │   └── validation.py     # Data validation helpers
│   ├── spiders/              # Scrapy spiders
│   │   └── luma.py          # Enhanced Luma spider
│   ├── items.py              # Enhanced data models
│   ├── pipelines.py          # Enhanced data processing
│   └── settings.py           # Configuration
├── tests/                     # Test suite
├── output/                    # Extracted data and HTML files
└── README.md                 # This file
```

## 🔧 Configuration

### JSON Extraction Settings

```python
# Enable/disable JSON extraction
JSON_EXTRACTION_ENABLED = True

# Custom extraction patterns
JSON_EXTRACTION_PATTERNS = [
    r'"event":\s*(\{(?:[^{}]|{[^{}]*})*\})',
    r'window\.__INITIAL_DATA__\s*=\s*(\{.*?\});',
    # ... more patterns
]

# Fallback to HTML parsing if JSON fails
JSON_EXTRACTION_FALLBACK = True

# Enhanced pipeline settings
ENHANCED_JSON_VALIDATION = True
ENHANCED_JSON_INCLUDE_METADATA = True
ENHANCED_JSON_EXTRACTION_STATS = True
```

### Output Format

The crawler generates structured JSON with comprehensive event data:

```json
{
  "metadata": {
    "spider_name": "luma",
    "start_time": "2025-01-16T...",
    "extraction_statistics": {
      "total_processed": 8,
      "json_extraction": 8,
      "success_rates": {
        "json_extraction_rate": 1.0,
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
      "_metadata": {
        "extraction_method": "json",
        "completeness_score": 0.90
      }
    }
  ],
  "event_count": 8
}
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
uv run pytest

# Run specific test suites
uv run pytest tests/test_extractors.py -v
uv run pytest tests/test_utils.py -v

# Run with coverage
uv run pytest --cov=show_up
```

### Integration Tests

```bash
# Test enhanced extraction on real HTML files
uv run python test_enhanced_extraction.py
```

## 📈 Data Quality Metrics

### Extracted Fields

- **Basic**: Title, URL, description
- **Temporal**: Start date, end date, timezone
- **Location**: Address, city, country, coordinates, place ID
- **Metadata**: Event type, visibility, organizer, API ID
- **Additional**: Cover image, guest count, RSVP info

### Quality Scoring

Events are automatically scored for completeness:
- **High Quality (>80%)**: Complete event data with all major fields
- **Medium Quality (50-80%)**: Most fields present, some gaps
- **Low Quality (<50%)**: Minimal data extraction

## 🔍 Extraction Methods

### 1. JSON Extraction (Primary)
- Extracts from embedded JSON structures
- Handles multiple JSON patterns
- Comprehensive data extraction
- **87.2% average completeness**

### 2. HTML Parsing (Fallback)
- CSS selector-based extraction
- Fallback when JSON extraction fails
- Basic field extraction
- **~25% average completeness**

### 3. Minimal Extraction (Last Resort)
- Title from page title or meta tags
- URL from request
- Ensures no empty results

## 🛠️ Development

### Adding New Extractors

1. Create extractor class inheriting from `BaseExtractor`
2. Implement `extract()` and `can_extract()` methods
3. Add to `MultiExtractor` for fallback chains

```python
from show_up.extractors.base import BaseExtractor

class MyExtractor(BaseExtractor):
    def extract(self, content, **kwargs):
        # Your extraction logic here
        return extracted_data
    
    def can_extract(self, content):
        # Check if this extractor can handle the content
        return "my_pattern" in content
```

### Adding New Fields

1. Add field to `EventItem` in `items.py`
2. Update extraction logic in extractors
3. Add validation in `utils/validation.py`
4. Update pipeline processing if needed

## 📊 Monitoring and Debugging

### Extraction Statistics

The enhanced pipeline tracks detailed statistics:
- Success rates by extraction method
- Data quality metrics
- Processing times
- Validation results

### Debug Mode

```bash
# Enable debug logging
export SCRAPY_SETTINGS_MODULE=show_up.settings
uv run scrapy crawl luma -L DEBUG

# Save debug HTML files
JSON_EXTRACTION_DEBUG = True
```

## 🎯 Roadmap

- [ ] Support for additional event platforms
- [ ] Real-time event monitoring
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Event deduplication
- [ ] Geographic event clustering
- [ ] Event recommendation system

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the coding standards in `.agents/RULES.md`
4. Add comprehensive tests
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Scrapy](https://scrapy.org/) and [Playwright](https://playwright.dev/)
- Follows the architecture patterns from `.agents/PLANNING.md`
- Uses modern Python 3.13+ features and type hints

---

**Show Up Crawler** - Making crypto event discovery comprehensive and reliable! 🚀
````

## File: show_up/items.py
````python
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from typing import Optional, Dict, Any


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
    extraction_method = scrapy.Field()  # How data was extracted ("json", "html", "fallback")

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

## File: show_up/pipelines.py
````python
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
   "show_up.pipelines.HtmlFilePipeline": 301,
   "show_up.pipelines.RawHtmlFilePipeline": 302,
}

# JSON output settings
JSON_OUTPUT_FILE = 'crypto_events.json'
JSON_INDENT = 2  # Pretty-print JSON with 2-space indentation
JSON_ENSURE_ASCII = False  # Allow non-ASCII characters in JSON

# JSON Extraction Settings
JSON_EXTRACTION_ENABLED = True  # Enable JSON data extraction from HTML
JSON_EXTRACTION_PATTERNS = [
    r'"event":\s*(\{[^}]+(?:\{[^}]*\}[^}]*)*\})',
    r'window\.__INITIAL_DATA__\s*=\s*({.+?});',
    r'<script[^>]*>.*?({.*?"event".*?}.*?)</script>',
    r'<script[^>]*type="application/ld\+json"[^>]*>([^<]+)</script>',
    r'window\.__PROPS__\s*=\s*({.+?});',
    r'data-event=(["\'])({.*?})\1',
]
JSON_EXTRACTION_FALLBACK = True  # Fall back to HTML parsing if JSON extraction fails
JSON_EXTRACTION_DEBUG = False  # Enable debug logging for JSON extraction

# Enhanced Item Pipeline Settings
ENHANCED_JSON_VALIDATION = True  # Enable data validation for extracted items
ENHANCED_JSON_INCLUDE_METADATA = True  # Include extraction metadata in output
ENHANCED_JSON_EXTRACTION_STATS = True  # Track extraction statistics

# Concurrency and throttling settings
#CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "show_up.middlewares.ShowUpSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "show_up.middlewares.ShowUpDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

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

## File: show_up/spiders/luma.py
````python
import scrapy
from show_up.items import EventItem
from show_up.extractors import JsonExtractor
from show_up.utils.validation import validate_event_data, clean_event_data
from scrapy_playwright.page import PageMethod
from typing import Dict, Any, Optional


class LumaSpider(scrapy.Spider):
    name = "luma"
    allowed_domains = ["lu.ma"]
    start_urls = ["https://lu.ma/crypto"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize JSON extractor
        self.json_extractor = JsonExtractor(config={
            'required_fields': ['title'],
            'custom_patterns': self.settings.getlist('JSON_EXTRACTION_PATTERNS', [])
        })

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
        with open('debug_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        # Debug: print the length of the response
        self.logger.info(f"Response length: {len(response.text)}")

        # Extract event links from the timeline section
        # Look for individual event cards in the timeline
        event_links = response.css('a.event-link::attr(href)').getall()
        self.logger.info(f"Found {len(event_links)} event links with selector 'a.event-link'")

        # Try different selectors to find event links
        alternative_selectors = [
            'a.event-link',
            'a[aria-label*="event"]',
            'a[href*="/1"]',  # Individual event IDs seem to start with /1
            'a[href*="/g"]',  # Some event IDs start with /g
            'a[href*="/v"]',  # Some event IDs start with /v
            '.timeline a[href^="/"]',  # Links in timeline starting with /
        ]

        for selector in alternative_selectors:
            links = response.css(f'{selector}::attr(href)').getall()
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
            self.logger.warning("No event links found! This might be a JavaScript-heavy page that needs more time to load.")

    def parse_event(self, response):
        """Parse event page and extract complete event data using JSON extraction."""
        # Initialize event item
        item = EventItem()

        # Set basic fields
        item['url'] = response.url
        item['raw_html'] = response.text

        # Try JSON extraction first (primary method)
        extracted_data = self._extract_with_json(response)

        # If JSON extraction fails, fall back to HTML parsing
        if not extracted_data and self.settings.getbool('JSON_EXTRACTION_FALLBACK', True):
            extracted_data = self._extract_with_html_selectors(response)

        # If we still don't have data, create minimal item
        if not extracted_data:
            self.logger.warning(f"Failed to extract data from {response.url}")
            extracted_data = {
                'title': self._extract_title_fallback(response),
                'extraction_method': 'fallback'
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

            self.logger.info(f"Successfully extracted event: {item.get('title', 'Unknown')} using {item.get('extraction_method', 'unknown')}")

        except Exception as e:
            self.logger.error(f"Data validation failed for {response.url}: {e}")
            # Continue with unvalidated data

        yield item

    def _extract_with_json(self, response) -> Optional[Dict[str, Any]]:
        """Extract event data using JSON extraction."""
        if not self.settings.getbool('JSON_EXTRACTION_ENABLED', True):
            return None

        try:
            extracted_data = self.json_extractor.extract(
                response.text,
                url=response.url
            )

            if extracted_data:
                self.logger.info(f"JSON extraction successful for {response.url}")
                return extracted_data
            else:
                self.logger.debug(f"JSON extraction found no data for {response.url}")

        except Exception as e:
            self.logger.warning(f"JSON extraction failed for {response.url}: {e}")

        return None

    def _extract_with_html_selectors(self, response) -> Optional[Dict[str, Any]]:
        """Extract event data using HTML selectors (fallback method)."""
        self.logger.info(f"Falling back to HTML selector extraction for {response.url}")

        extracted_data = {
            'extraction_method': 'html_fallback'
        }

        # Try multiple selectors for title
        title = response.css('h1::text').get()
        if not title:
            title = response.css('[data-testid="event-title"]::text').get()
        if not title:
            title = response.css('title::text').get()
        if not title:
            title = response.css('.title::text').get()

        # Try multiple selectors for date
        date = response.css('.event-date::text').get()
        if not date:
            date = response.css('[data-testid="event-date"]::text').get()
        if not date:
            date = response.css('time::text').get()
        if not date:
            date = response.css('[datetime]::attr(datetime)').get()

        # Try multiple selectors for location
        location = response.css('.event-location::text').get()
        if not location:
            location = response.css('[data-testid="event-location"]::text').get()
        if not location:
            location = response.css('address::text').get()
        if not location:
            location = response.css('.location::text').get()

        # Populate extracted data
        if title:
            extracted_data['title'] = title.strip()
        if date:
            extracted_data['date'] = date.strip()
        if location:
            extracted_data['location'] = location.strip()

        return extracted_data if extracted_data.get('title') else None

    def _extract_title_fallback(self, response) -> str:
        """Extract title using multiple fallback methods."""
        # Try page title
        title = response.css('title::text').get()
        if title:
            # Clean up title (remove site name, etc.)
            title = title.replace(' | Luma', '').replace(' - Luma', '').strip()
            return title

        # Try any h1 tag
        title = response.css('h1::text').get()
        if title:
            return title.strip()

        # Try meta property
        title = response.css('meta[property="og:title"]::attr(content)').get()
        if title:
            return title.strip()

        # Final fallback - extract from URL
        url_parts = response.url.split('/')
        if url_parts:
            return url_parts[-1].replace('-', ' ').title()

        return 'Unknown Event'

    def _populate_item(self, item: EventItem, data: Dict[str, Any]) -> None:
        """Populate EventItem with extracted data."""
        # Map extracted data to item fields
        field_mapping = {
            'title': 'title',
            'date': 'date',
            'end_date': 'end_date',
            'timezone': 'timezone',
            'location': 'location',
            'full_address': 'full_address',
            'city': 'city',
            'country': 'country',
            'coordinates': 'coordinates',
            'place_id': 'place_id',
            'event_type': 'event_type',
            'visibility': 'visibility',
            'api_id': 'api_id',
            'cover_url': 'cover_url',
            'organizer': 'organizer',
            'guest_count': 'guest_count',
            'description': 'description',
            'extraction_method': 'extraction_method'
        }

        for data_key, item_key in field_mapping.items():
            if data_key in data and data[data_key]:
                item[item_key] = data[data_key]

        # Set HTML content
        html_content = self._get_html_content(item)
        if html_content:
            item['html_content'] = html_content

    def _get_html_content(self, item: EventItem) -> Optional[str]:
        """Extract HTML content for the item."""
        raw_html = item.get('raw_html', '')
        if not raw_html:
            return None

        # Try to extract main content
        from scrapy import Selector
        selector = Selector(text=raw_html)

        # Try different selectors for main content
        main_content = selector.css('main').get()
        if not main_content:
            main_content = selector.css('body').get()
        if not main_content:
            main_content = raw_html

        return main_content
````
