from flask import Blueprint, request
from app.controllers import auth_controller

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return role."""
    data = request.get_json()
    return auth_controller.login(data)