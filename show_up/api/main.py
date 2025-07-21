"""CLI launcher for the Show Up API server."""

from fastapi import FastAPI
from show_up.api.router import api_router

app = FastAPI()

app.include_router(api_router)
