"""Centralized logging configuration for ModelCtx."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up a logger with consistent configuration.
    
    Args:
        name: Logger name (will be prefixed with 'modelctx.')
        level: Logging level
        log_file: Optional file to write logs to
        format_string: Optional custom format string
    
    Returns:
        Configured logger instance
    """
    logger_name = f"modelctx.{name}" if not name.startswith("modelctx.") else name
    logger = logging.getLogger(logger_name)
    
    # Avoid adding multiple handlers if logger already exists
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Default format
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # File gets more detailed logs
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for the specified module.
    
    Args:
        name: Module name (e.g., 'cli', 'generator', 'backends.database')
    
    Returns:
        Logger instance
    """
    return setup_logger(name)


def configure_root_logger(verbose: bool = False) -> None:
    """Configure the root modelctx logger.
    
    Args:
        verbose: If True, set DEBUG level, otherwise INFO
    """
    level = logging.DEBUG if verbose else logging.INFO
    setup_logger("modelctx", level=level)