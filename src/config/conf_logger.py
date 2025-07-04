import logging
import re
from datetime import datetime
from pathlib import Path

from src.config.config import LOGGER_LEVEL
from src.core.models import ValidationIssue

LOG_LINE_REGEX = re.compile(r"^(?P<timestamp>[\d\-: ]+) - (?P<level>[A-Z]+) - (?P<message>.+)$")


def setup_logger(name: str, file: str, level: int = LOGGER_LEVEL) -> logging.Logger:
    log_dir = Path(__file__).resolve().parents[2] / "log"
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_dir / f"{file}.log", mode='a')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


def parse_validation_issues_from_log() -> list[ValidationIssue]:
    issues = []
    keywords = ["validation", "missing declaration", "mismatched total", "anomaly", "orphaned"]
    log_dir = Path(__file__).resolve().parents[2] / "log"

    with open(log_dir, encoding="utf-8") as f:
        for line in f:
            match = LOG_LINE_REGEX.match(line)
            if match:
                message = match.group("message").lower()
                if any(keyword in message for keyword in keywords):
                    issues.append(
                        ValidationIssue(
                            timestamp=datetime.strptime(match.group("timestamp"), "%Y-%m-%d %H:%M:%S,%f"),
                            level=match.group("level"),
                            message=match.group("message")
                        )
                    )
    return issues