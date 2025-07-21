"""Pydantic models for API request and response schemas.

This module defines the data models used for API endpoints, including
event response models and crawl request/response schemas.
"""

from pydantic import BaseModel, Field
from typing import Any


class EventOut(BaseModel):
    """Response model for event data, mirroring EventItem with modern type hints.
    
    This model represents the structure of event data returned by the API,
    using modern Python generics and Optional typing conventions.
    """
    
    # Basic fields
    title: str | None = None
    url: str | None = None
    description: str | None = None
    
    # Temporal fields
    date: str | None = None  # Start date (ISO format)
    end_date: str | None = None  # End date (ISO format)
    timezone: str | None = None  # Event timezone (e.g., "America/Buenos_Aires")
    
    # Location fields
    location: str | None = None  # Simple location string for backward compatibility
    full_address: str | None = None  # Complete formatted address
    city: str | None = None  # City name
    country: str | None = None  # Country name
    coordinates: dict[str, float] | None = None  # Dict with 'latitude' and 'longitude'
    place_id: str | None = None  # Google Place ID or similar
    
    # Metadata fields
    event_type: str | None = None  # Event type (e.g., "independent", "series")
    visibility: str | None = None  # Visibility (e.g., "public", "private")
    api_id: str | None = None  # Platform-specific API ID
    cover_url: str | None = None  # Cover image URL
    organizer: str | None = None  # Event organizer information
    guest_count: int | None = None  # Number of guests/attendees
    
    # Technical fields
    html_content: str | None = None  # Processed HTML content
    raw_html: str | None = None  # Raw HTML response
    extraction_method: str | None = None  # How data was extracted ("json", "html", "fallback")
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class CrawlRequest(BaseModel):
    """Request model for crawl operations.
    
    Contains the parameters needed to initiate a crawl operation,
    including target URLs and spider selection.
    """
    
    urls: list[str] | None = Field(
        default=None,
        description="List of URLs to crawl. If None, spider will use default URLs."
    )
    spider: str = Field(
        default="luma",
        description="Name of the spider to use for crawling"
    )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "urls": [
                    "https://lu.ma/event/example-event-id",
                    "https://lu.ma/discover"
                ],
                "spider": "luma"
            }
        }


class CrawlResponse(BaseModel):
    """Response model for crawl operations.
    
    Contains information about the initiated crawl job,
    including job identifier and status.
    """
    
    job_id: str = Field(
        description="Unique identifier for the crawl job"
    )
    status: str = Field(
        description="Current status of the crawl job (e.g., 'pending', 'running', 'completed', 'failed')"
    )
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "job_id": "crawl_20240101_123456_luma",
                "status": "pending"
            }
        }
