"""Logging utilities for the QuantumMeta License system."""

import logging
import sys
from pathlib import Path
from typing import Optional
import platformdirs


def setup_logger(
    name: str = "quantummeta_license",
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger for the QuantumMeta License system.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_default_log_file() -> str:
    """Get the default log file path."""
    config_dir = Path(platformdirs.user_config_dir("quantummeta"))
    config_dir.mkdir(parents=True, exist_ok=True)
    return str(config_dir / "license.log")


# Default logger instance
logger = setup_logger()
