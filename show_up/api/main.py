"""CLI launcher for the Show Up API server.

This module provides a command-line interface to start the FastAPI server
using uvicorn. Can be run with: uv run python -m show_up.api.main
"""

import sys
from typing import Any

import uvicorn


def main() -> None:
    """Main entry point for starting the API server.
    
    Starts the FastAPI application using uvicorn with development settings.
    For production, consider using a proper ASGI server deployment.
    """
    # Development server configuration
    config: dict[str, Any] = {
        "app": "show_up.api:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,  # Auto-reload on code changes during development
        "log_level": "info",
        "access_log": True,
    }
    
    print("Starting Show Up API server...")
    print(f"Server will be available at: http://localhost:{config['port']}")
    print(f"API documentation at: http://localhost:{config['port']}/docs")
    print(f"Alternative docs at: http://localhost:{config['port']}/redoc")
    print("Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
