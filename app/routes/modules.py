"""
Module Routes.

This module defines API endpoints for module management operations including
CRUD operations for modules and module registration management.
"""
from flask import Blueprint, request
from app.controllers.module_controller import (
    get_all_modules, get_module, create_module, update_module, delete_module,
    register_student_to_module, get_module_registrations, update_registration_status
)

modules_bp = Blueprint('modules', __name__)


@modules_bp.route('/modules', methods=['GET'])
def list_modules():
    """
    Get all modules.
    
    Returns:
        JSON response with list of all modules
    """
    return get_all_modules()


@modules_bp.route('/modules/<module_id>', methods=['GET'])
def get_module_by_id(module_id):
    """
    Get a specific module by ID.
    
    Args:
        module_id (str): The unique identifier of the module
        
    Returns:
        JSON response with module data
    """
    return get_module(module_id)


@modules_bp.route('/modules', methods=['POST'])
def create_new_module():
    """
    Create a new module.
    
    Expected JSON payload:
        {
            "module_id": "string",
            "course_id": "string", 
            "module_name": "string",
            "duration_weeks": int (optional, default: 12)
        }
        
    Returns:
        JSON response with created module data
    """
    return create_module(request.json)


@modules_bp.route('/modules/<module_id>', methods=['PUT'])
def update_module_by_id(module_id):
    """
    Update an existing module.
    
    Args:
        module_id (str): The unique identifier of the module
        
    Expected JSON payload:
        {
            "module_name": "string" (optional),
            "duration_weeks": int (optional),
            "course_id": "string" (optional)
        }
        
    Returns:
        JSON response with updated module data
    """
    return update_module(module_id, request.json)


@modules_bp.route('/modules/<module_id>', methods=['DELETE'])
def delete_module_by_id(module_id):
    """
    Delete a module.
    
    Args:
        module_id (str): The unique identifier of the module
        
    Returns:
        JSON response with success message
    """
    return delete_module(module_id)


@modules_bp.route('/modules/registrations', methods=['POST'])
def register_student():
    """
    Register a student to a module.
    
    Expected JSON payload:
        {
            "student_id": "string",
            "module_id": "string",
            "status": "string" (optional, default: "Active"),
            "start_date": "YYYY-MM-DD" (optional)
        }
        
    Returns:
        JSON response with registration details
    """
    return register_student_to_module(request.json)


@modules_bp.route('/modules/<module_id>/registrations', methods=['GET'])
def get_registrations_for_module(module_id):
    """
    Get all student registrations for a specific module.
    
    Args:
        module_id (str): The unique identifier of the module
        
    Returns:
        JSON response with list of registrations
    """
    return get_module_registrations(module_id)


@modules_bp.route('/modules/registrations/<int:registration_id>', methods=['PUT'])
def update_registration(registration_id):
    """
    Update the status of a module registration.
    
    Args:
        registration_id (int): The unique identifier of the registration
        
    Expected JSON payload:
        {
            "status": "string" (Active, Completed, or Withdrawn)
        }
        
    Returns:
        JSON response with updated registration
    """
    return update_registration_status(registration_id, request.json)