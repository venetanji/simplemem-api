#!/usr/bin/env python3
"""
Entrypoint script to run SimpleMem API server
"""

import uvicorn
from app.config import settings


def main():
    """Run the FastAPI application with uvicorn"""
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )


if __name__ == "__main__":
    main()
