"""
Authentication Controller Module.

This module handles user authentication operations including login validation
and role-based access control.

Note:
    Currently uses mock user data. In production, this should be replaced with
    a proper user model and secure password hashing (e.g., bcrypt).
"""
from flask import jsonify

# Mock user database - replace with real user model and secure password hashing
USERS = {
    "cd_user": {"password": "cd_pass", "role": "CD"},
    "swo_user": {"password": "swo_pass", "role": "SWO"}
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
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "Username and password required"}), 400
        
        user = USERS.get(username)
        if not user or user['password'] != password:  # Simple check, use hash in production
            return jsonify({"error": "Invalid credentials"}), 401
        
        return jsonify({
            "message": "Login successful",
            "role": user['role'],
            "username": username
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
