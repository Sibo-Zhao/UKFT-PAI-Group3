"""
Academic Assignments Routes Blueprint.

This module defines Flask routes for assignment CRUD operations including
creation, updates, and deletion of assignments.

Endpoints:
    POST /academic/assignments - Create new assignment
    PUT /academic/assignments/<id> - Update assignment
    DELETE /academic/assignments/<id> - Delete assignment
"""
from flask import Blueprint, request
from app.controllers import assignment_controller

# Create blueprint
assignments_bp = Blueprint('assignments', __name__, url_prefix='/academic')


@assignments_bp.route('/assignments', methods=['POST'])
def create_assignment():
    """
    Create a new assignment.
    
    Request Body:
        JSON with assignment details
        
    Returns:
        JSON response with created assignment (201) or error (400/404)
    """
    data = request.get_json()
    return assignment_controller.create_assignment(data)


@assignments_bp.route('/assignments/<string:assignment_id>', methods=['PUT'])
def update_assignment(assignment_id):
    """
    Update an existing assignment.
    
    Args:
        assignment_id: Assignment identifier
        
    Request Body:
        JSON with fields to update
        
    Returns:
        JSON response with updated assignment (200) or error (404/400)
    """
    data = request.get_json()
    return assignment_controller.update_assignment(assignment_id, data)


@assignments_bp.route('/assignments/<string:assignment_id>', methods=['DELETE'])
def delete_assignment(assignment_id):
    """
    Delete an assignment.
    
    Args:
        assignment_id: Assignment identifier
        
    Returns:
        JSON response with success message (200) or error (404)
    """
    return assignment_controller.delete_assignment(assignment_id)
