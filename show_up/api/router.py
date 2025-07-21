"""FastAPI router definitions for the Show Up API.

This module contains all route definitions for the event crawler API.
Routes include health checks, event data endpoints, and crawler status.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Any
from fastapi.responses import JSONResponse
from pymongo.collection import Collection
from show_up.db import get_db
from show_up.api.models import EventOut
from show_up.api.crawler import crawler_router

# Create the main API router
api_router = APIRouter()

# Include crawler endpoints
api_router.include_router(crawler_router, tags=["crawler"])


@api_router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint to verify API is running."""
    return {"status": "healthy", "service": "show-up-api"}


@api_router.get("/")
async def root() -> dict[str, str]:
    """Root endpoint providing basic API information."""
    return {
        "name": "Show Up API",
        "description": "Event crawler and data API",
        "version": "0.1.0",
    }


@api_router.get("/events")
async def get_events(
    limit: int = Query(
        default=10, ge=1, le=100, description="Maximum number of events to return"
    ),
    skip: int = Query(
        default=0, ge=0, description="Number of events to skip for pagination"
    ),
    city: str | None = Query(default=None, description="Filter by city name"),
    country: str | None = Query(default=None, description="Filter by country name"),
    event_type: str | None = Query(default=None, description="Filter by event type"),
    organizer: str | None = Query(default=None, description="Filter by organizer name"),
) -> JSONResponse:
    """List events from the database with pagination and filters.

    Args:
        limit: Maximum number of events to return (1-100)
        skip: Number of events to skip for pagination
        city: Optional filter by city name
        country: Optional filter by country name
        event_type: Optional filter by event type
        organizer: Optional filter by organizer name

    Returns:
        JSONResponse with events list and pagination headers
    """
    db: Collection = get_db()["events"]
    filters = {}

    # Build filters based on query parameters
    if city:
        filters["city"] = {"$regex": city, "$options": "i"}  # Case-insensitive regex
    if country:
        filters["country"] = {"$regex": country, "$options": "i"}
    if event_type:
        filters["event_type"] = event_type
    if organizer:
        filters["organizer"] = {"$regex": organizer, "$options": "i"}

    total_events = db.count_documents(filters)
    events_cursor = db.find(filters).skip(skip).limit(limit)
    events = []

    for event in events_cursor:
        # Handle MongoDB ObjectId field
        if "_id" in event:
            del event["_id"]

        try:
            event_out = EventOut(**event)
            events.append(event_out.model_dump())
        except Exception:
            # Skip events that can't be serialized, log in production
            continue

    response = JSONResponse(content={"events": events})
    response.headers["X-Total-Count"] = str(total_events)
    response.headers["X-Limit"] = str(limit)
    response.headers["X-Skip"] = str(skip)
    if total_events > skip + limit:
        response.headers["X-Has-More"] = "true"
    else:
        response.headers["X-Has-More"] = "false"

    return response


@api_router.get("/events/{api_id}")
async def get_event(api_id: str) -> dict[str, Any]:
    """Get a specific event by API ID.

    Args:
        api_id: Platform-specific API identifier for the event

    Returns:
        Event data dictionary

    Raises:
        HTTPException: If event not found
    """
    db: Collection = get_db()["events"]

    # Try to find by api_id first, then fallback to other unique identifiers
    event = db.find_one({"api_id": api_id})

    # If not found by api_id, try finding by title as fallback for older data
    if event is None:
        # Try to find by title if the api_id looks like it could be a URL-encoded title
        event = db.find_one(
            {"title": {"$regex": api_id.replace("-", "\\s+"), "$options": "i"}}
        )

    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    # Handle MongoDB ObjectId field
    if "_id" in event:
        del event["_id"]

    try:
        event_out = EventOut(**event)
        return event_out.model_dump()
    except Exception as e:
        # Log the error in production, for now return a more detailed error
        raise HTTPException(
            status_code=500, detail=f"Error processing event data: {str(e)}"
        )


@api_router.get("/sources")
async def get_sources() -> dict[str, Any]:
    """Get available event sources and their status.

    Returns:
        Dictionary containing source information and statistics
    """
    return {
        "sources": [
            {"name": "eventbrite", "status": "active", "last_crawled": None},
            {"name": "luma", "status": "active", "last_crawled": None},
        ],
        "total": 2,
    }
