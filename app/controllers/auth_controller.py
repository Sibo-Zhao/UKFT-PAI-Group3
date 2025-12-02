"""
Authentication Controller Module.

This module handles user authentication operations including login validation
and role-based access control.

Note:
    Currently uses mock user data. In production, this should be replaced with
    a proper user model and database storage.
"""
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.error_handlers import handle_error, log_request_error
from app.utils.validators import LoginSchema, validate_request_data
import logging

logger = logging.getLogger(__name__)

# Mock user database with hashed passwords
# In production, replace with proper User model and database
USERS = {
    "cd_user": {
        "password_hash": generate_password_hash("cd_pass"),
        "role": "CD"
    },
    "swo_user": {
        "password_hash": generate_password_hash("swo_pass"),
        "role": "SWO"
    }
}


def login(data):
    """
    Authenticate user and return their role.
    
    Validates user credentials against the mock user database and returns
    the user's role if authentication is successful.
    
    Args:
        data (dict): Request data containing authentication credentials.
            Expected keys:
                - username (str): User's username
                - password (str): User's password (plain text - NOT SECURE)
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with authentication result
            - int: HTTP status code
                - 200: Login successful
                - 400: Missing required fields
                - 401: Invalid credentials
                - 500: Server error
    
    Example:
        >>> login({"username": "cd_user", "password": "cd_pass"})
        ({"message": "Login successful", "role": "CD", "username": "cd_user"}, 200)
    
    Warning:
        This implementation uses plain text password comparison and should NOT
        be used in production. Implement proper password hashing and salting.
    """
    try:
        # Validate input data
        validated_data, errors = validate_request_data(LoginSchema, data)
        if errors:
            logger.warning(f"Login validation failed: {errors}")
            return jsonify({"error": "Validation failed", "details": errors}), 400
        
        username = validated_data['username']
        password = validated_data['password']
        
        logger.info(f"Login attempt for user: {username}")
        user = USERS.get(username)
        if not user or not check_password_hash(user['password_hash'], password):
            logger.warning(f"Failed login attempt for user: {username}")
            return jsonify({"error": "Invalid credentials"}), 401
        
        logger.info(f"Successful login for user: {username}, role: {user['role']}")
        return jsonify({
            "message": "Login successful",
            "role": user['role'],
            "username": username
        }), 200
    except Exception as e:
        log_request_error("login", e, username=username if 'username' in locals() else 'unknown')
        return handle_error(e, "in login")
