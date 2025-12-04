"""
Error Handler Utilities.

This module provides standardized error handling and response formatting
for the application.
"""
import logging
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from marshmallow import ValidationError

logger = logging.getLogger(__name__)


def handle_error(error, context=""):
    """
    Handle exceptions with proper logging and user-friendly responses.
    
    Args:
        error (Exception): The exception that occurred
        context (str): Additional context about where the error occurred
    
    Returns:
        tuple: JSON response and HTTP status code
    """
    # Validation errors (400)
    if isinstance(error, ValidationError):
        logger.warning(f"Validation error {context}: {error.messages}")
        return jsonify({
            "error": "Validation failed",
            "details": error.messages
        }), 400
    
    # Database integrity errors (409)
    if isinstance(error, IntegrityError):
        logger.error(f"Database integrity error {context}: {str(error)}")
        return jsonify({
            "error": "Database constraint violation",
            "message": "The operation violates database constraints"
        }), 409
    
    # General database errors (500)
    if isinstance(error, SQLAlchemyError):
        logger.error(f"Database error {context}: {str(error)}")
        return jsonify({
            "error": "Database operation failed",
            "message": "An error occurred while accessing the database"
        }), 500
    
    # Value errors (400)
    if isinstance(error, ValueError):
        logger.warning(f"Value error {context}: {str(error)}")
        return jsonify({
            "error": "Invalid value",
            "message": str(error)
        }), 400
    
    # Key errors (400)
    if isinstance(error, KeyError):
        logger.warning(f"Missing key {context}: {str(error)}")
        return jsonify({
            "error": "Missing required field",
            "message": f"Required field {str(error)} is missing"
        }), 400
    
    # Generic errors (500)
    logger.exception(f"Unexpected error {context}: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


def log_request_error(endpoint, error, **kwargs):
    """
    Log request-specific errors with context.
    
    Args:
        endpoint (str): The endpoint where error occurred
        error (Exception): The exception
        **kwargs: Additional context (student_id, module_id, etc.)
    """
    context_str = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.error(f"Error in {endpoint} ({context_str}): {str(error)}")
