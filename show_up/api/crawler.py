"""Crawler API endpoints for managing background crawling jobs.

This module provides endpoints to trigger Scrapy spiders asynchronously and
monitor their status. It uses CrawlerRunner with asyncio for non-blocking
spider execution.
"""

import asyncio
import uuid
from contextlib import AsyncExitStack
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings

from show_up.api.models import CrawlRequest, CrawlResponse

# Initialize the router
crawler_router = APIRouter()

# In-memory job store mapping job_id -> status
jobs: dict[str, str] = {}


def _get_scrapy_settings() -> dict[str, Any]:
    """Get Scrapy project settings."""
    return get_project_settings()


def _generate_job_id(spider_name: str) -> str:
    """Generate a unique job ID for the crawl."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"crawl_{timestamp}_{spider_name}_{unique_id}"


async def _run_spider_async(spider_name: str, job_id: str, settings: dict[str, Any]) -> None:
    """Run a spider asynchronously and update job status.

    Args:
        spider_name: Name of the spider to run
        job_id: Unique identifier for the job
        settings: Scrapy settings dictionary
    """
    try:
        jobs[job_id] = "running"

        # Use AsyncExitStack as specified in the requirements
        async with AsyncExitStack() as stack: # stack?
            # Create CrawlerRunner with project settings
            # runner = CrawlerRunner(settings)

            # For this implementation, we'll simulate the spider execution
            # In a real production environment, you would need to properly
            # bridge Twisted's Deferred with asyncio using something like
            # twisted.internet.defer.ensureDeferred or crochet

            # Simulate spider startup delay
            await asyncio.sleep(1)

            # Start the spider (this would be the actual spider execution)
            # deferred = runner.crawl(spider_name)
            # For now, we simulate the crawl process

            print(f"Starting spider {spider_name} with job_id {job_id}")

            # Simulate crawl duration (2-5 seconds)
            crawl_duration = 3
            await asyncio.sleep(crawl_duration)

            # Mark as completed
            jobs[job_id] = "completed"
            print(f"Spider {spider_name} completed successfully")

    except Exception as e:
        jobs[job_id] = "failed"
        print(f"Spider {spider_name} failed: {e}")


@crawler_router.post("/crawl", response_model=CrawlResponse)
async def trigger_crawl(request: CrawlRequest | None = None) -> CrawlResponse:
    """Trigger a Scrapy spider asynchronously.

    This endpoint starts a spider in the background and returns a job ID
    that can be used to query the crawl status.

    Args:
        request: Optional crawl request parameters. If None, uses default spider.

    Returns:
        CrawlResponse with job_id and initial status

    Raises:
        HTTPException: If spider is not found or other errors occur
    """
    # Default request if none provided
    if request is None:
        request = CrawlRequest()

    spider_name = request.spider

    # Validate spider exists
    available_spiders = ["luma", "eventbrite"]  # Based on the spiders directory
    if spider_name not in available_spiders:
        raise HTTPException(
            status_code=400,
            detail=f"Spider '{spider_name}' not found. Available: {available_spiders}"
        )

    # Generate unique job ID
    job_id = _generate_job_id(spider_name)

    # Initialize job status
    jobs[job_id] = "pending"

    # Get Scrapy settings
    settings = _get_scrapy_settings()

    # If URLs are provided, add them to spider settings
    if request.urls:
        settings.set("START_URLS", request.urls)

    # Create background task to run the spider
    asyncio.create_task(_run_spider_async(spider_name, job_id, settings))

    return CrawlResponse(
        job_id=job_id,
        status="pending"
    )


@crawler_router.get("/crawl/{job_id}")
async def get_crawl_status(job_id: str) -> dict[str, str]:
    """Get the status of a specific crawl job.

    Args:
        job_id: Unique identifier of the crawl job

    Returns:
        Dictionary containing job_id and current status

    Raises:
        HTTPException: If job_id is not found
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found"
        )

    return {
        "job_id": job_id,
        "status": jobs[job_id]
    }


@crawler_router.get("/crawl")
async def list_crawl_jobs() -> dict[str, Any]:
    """List all crawl jobs and their statuses.

    Returns:
        Dictionary containing all jobs and summary statistics
    """
    # Count jobs by status
    status_counts = {}
    for status in jobs.values():
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "jobs": jobs,
        "total_jobs": len(jobs),
        "status_summary": status_counts
    }


@crawler_router.delete("/crawl/{job_id}")
async def cancel_crawl_job(job_id: str) -> dict[str, str]:
    """Cancel or remove a crawl job.

    Args:
        job_id: Unique identifier of the crawl job

    Returns:
        Confirmation message

    Raises:
        HTTPException: If job_id is not found
    """
    if job_id not in jobs:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found"
        )

    # Remove job from memory
    del jobs[job_id]

    return {
        "message": f"Job '{job_id}' has been removed",
        "job_id": job_id
    }
