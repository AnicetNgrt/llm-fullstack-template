import os
from loguru import logger
import sys


def setup_simple_logger(log_level: str, log_file: str = None):
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        level=log_level.upper(),
        format="<green>{time:HH:mm:ss Z}</green>|<blue>{level}</blue>| <level>{message}</level>",
        filter="yourapp",
    )

    if log_file is not None:
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        logger.add(
            log_file,
            level=log_level.upper(),
            format="{time:YYYY-MM-DD HH:mm:ss Z}|{level}| {message}",
            rotation="1 day",
            retention="30 days",
            filter="yourapp",
        )

        if log_level.upper() != "TRACE":
            log_filename = os.path.basename(log_file)
            log_dirpath = os.path.dirname(log_file)

            logger.add(
                os.path.join(log_dirpath, f"trace.{log_filename}"),
                level="TRACE",
                format="{time:HH:mm:ss Z}| {message}",
                rotation="1h",
                retention="3 days",
                filter="yourapp",
            )

    logger.info(f"Setting LogLevel to {log_level.upper()}")
