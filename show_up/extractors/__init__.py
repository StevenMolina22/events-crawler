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
