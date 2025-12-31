"""
Shared logging configuration for all services
Provides consistent logging format and levels
"""
import logging
import sys


def setup_logger(service_name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup structured logger for service

    Args:
        service_name: Name of the service
        level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(service_name)

    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # Add handler
    logger.addHandler(handler)

    return logger
