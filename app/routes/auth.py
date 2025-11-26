from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Mock user database - replace with real user model
USERS = {
    "cd_user": {"password": "cd_pass", "role": "CD"},
    "swo_user": {"password": "swo_pass", "role": "SWO"}
}

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return role."""
    try:
        data = request.get_json()
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