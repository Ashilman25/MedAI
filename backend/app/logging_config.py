import json
import logging
import os
import sys


class _JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        if record.exc_info and record.exc_info[1] is not None:
            msg = msg + "\n" + self.formatException(record.exc_info)
        return json.dumps({
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "msg": msg,
        })


def _make_rich_handler() -> logging.Handler | None:
    """Return a Rich-based handler if the library is installed, else None."""
    try:
        from rich.console import Console
        from rich.logging import RichHandler

        return RichHandler(
            console=Console(stderr=False),
            show_path=False,
            markup=True,
        )
    except ImportError:
        return None


def setup_logging() -> logging.Logger:
    log_format = os.getenv("LOG_FORMAT", "json").strip().lower()

    logger = logging.getLogger("medai")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if setup_logging is called more than once
    if logger.handlers:
        return logger

    if log_format == "pretty":
        handler = _make_rich_handler()
        if handler is None:
            # Rich not installed — fall back to JSON and warn on stderr
            print(
                "LOG_FORMAT=pretty but rich is not installed; falling back to JSON.",
                file=sys.stderr,
            )
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(_JSONFormatter())
        # RichHandler already formats nicely; no extra formatter needed
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_JSONFormatter())

    logger.addHandler(handler)
    # Don't propagate to root logger (avoids duplicate output)
    logger.propagate = False
    return logger


logger = setup_logging()
