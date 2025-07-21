"""
Base extractor interface for the Show Up Crawler.

This module defines the abstract base class for all data extractors.
It provides a consistent interface for extracting structured data
from various sources and formats.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, TypedDict
import logging

logger = logging.getLogger(__name__)


class EventData(TypedDict, total=False):
    """A dictionary containing extracted event data."""

    title: str
    url: str
    description: str
    date: str
    end_date: str
    timezone: str
    location: str
    full_address: str
    city: str
    country: str
    coordinates: Dict[str, float]
    place_id: str
    event_type: str
    visibility: str
    api_id: str
    cover_url: str
    organizer: str
    guest_count: int
    extraction_method: str
    extraction_pattern: int


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
    def extract(self, content: str, **kwargs) -> Optional[EventData]:
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

    def validate_extracted_data(self, data: EventData) -> bool:
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

    def log_extraction_result(self, success: bool, data: Optional[EventData] = None):
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

    def extract(self, content: str, **kwargs) -> Optional[EventData]:
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
