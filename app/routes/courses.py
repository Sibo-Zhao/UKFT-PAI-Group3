"""
Courses and Modules Routes Blueprint.

This module defines Flask routes for course and module management operations
including course listing, module retrieval, and assignment queries.

Endpoints:
    GET /courses - List all courses
    GET /courses/<course_id>/modules - List modules for a course
    GET /modules/<module_id>/assignments - List assignments for a module
"""
from flask import Blueprint
from app.controllers import course_controller

# Create blueprint
courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/courses', methods=['GET'])
def get_all_courses():
    """
    Get all courses.
    
    Returns:
        JSON response with list of all courses.
    """
    return course_controller.get_all_courses()


@courses_bp.route('/courses/<string:course_id>/modules', methods=['GET'])
def get_course_modules(course_id):
    """
    Get all modules for a specific course.
    
    Args:
        course_id: Course identifier
        
    Returns:
        JSON response with list of modules for the course.
    """
    return course_controller.get_course_modules(course_id)


@courses_bp.route('/modules/<string:module_id>/assignments', methods=['GET'])
def get_module_assignments(module_id):
    """
    Get all assignments for a specific module.
    
    Args:
        module_id: Module identifier
        
    Returns:
        JSON response with list of assignments for the module.
    """
    return course_controller.get_module_assignments(module_id)
