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
