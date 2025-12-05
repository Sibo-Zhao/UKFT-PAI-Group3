"""
Courses and Modules Routes Blueprint.

This module defines Flask routes for course and module management operations
including course listing, module retrieval, and assignment queries with proper
hierarchical relationships.

Endpoints:
    GET /courses - List all courses
    GET /courses/<course_id> - Get specific course details
    GET /courses/<course_id>/modules - List modules for a course
    GET /courses/<course_id>/students - List students enrolled in a course
    GET /courses/<course_id>/details - Get complete course hierarchy
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


@courses_bp.route('/courses/<string:course_id>', methods=['GET'])
def get_course_by_id(course_id):
    """
    Get a specific course by ID.
    
    Args:
        course_id: Course identifier
        
    Returns:
        JSON response with course details.
    """
    return course_controller.get_course(course_id)


@courses_bp.route('/courses/<string:course_id>/modules', methods=['GET'])
def get_course_modules(course_id):
    """
    Get all modules for a specific course.
    
    Args:
        course_id: Course identifier
        
    Returns:
        JSON response with course info and list of modules.
    """
    return course_controller.get_course_modules(course_id)


@courses_bp.route('/courses/<string:course_id>/details', methods=['GET'])
def get_course_details(course_id):
    """
    Get complete course details including modules and assignments.
    
    Args:
        course_id: Course identifier
        
    Returns:
        JSON response with complete course hierarchy (course -> modules -> assignments).
    """
    return course_controller.get_course_details(course_id)


@courses_bp.route('/courses/<string:course_id>/students', methods=['GET'])
def get_course_students(course_id):
    """
    Get all students enrolled in a specific course.
    
    Args:
        course_id: Course identifier
        
    Returns:
        JSON response with course info and list of enrolled students.
    """
    return course_controller.get_course_students(course_id)


@courses_bp.route('/modules/<string:module_id>/assignments', methods=['GET'])
def get_module_assignments(module_id):
    """
    Get all assignments for a specific module.
    
    Args:
        module_id: Module identifier
        
    Returns:
        JSON response with module info and list of assignments.
    """
    return course_controller.get_module_assignments(module_id)
