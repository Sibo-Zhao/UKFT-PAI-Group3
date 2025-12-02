"""
Logging Configuration Module.

This module sets up application-wide logging with proper formatting,
handlers, and log levels.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
import os


def setup_logging(app=None):
    """
    Configure application logging.
    
    Sets up console and file handlers with appropriate formatting
    and log levels based on environment.
    
    Args:
        app: Flask application instance (optional)
    
    Returns:
        logging.Logger: Configured root logger
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Determine log level from environment or app config
    log_level = logging.INFO
    if app:
        log_level = logging.DEBUG if app.config.get('DEBUG') else logging.INFO
    
    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Set SQLAlchemy logging to WARNING to reduce noise
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name (str): Logger name (typically __name__)
    
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
