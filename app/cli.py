from __future__ import annotations

import argparse

import uvicorn

from app.config import settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="simplemem-api",
        description="Run the SimpleMem FastAPI server (uvicorn).",
    )
    parser.add_argument(
        "--host",
        default=settings.host,
        help=f"Host interface to bind (default: {settings.host})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.port,
        help=f"Port to listen on (default: {settings.port})",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        default=settings.debug,
        help="Enable auto-reload (default: on when DEBUG=true)",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        help="Uvicorn log level (default: info)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
    )
