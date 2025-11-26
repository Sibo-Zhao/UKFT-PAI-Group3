"""
Courses and Modules routes blueprint.
Flask blueprint for course, module, and assignment endpoints.
"""
from flask import Blueprint, jsonify
from app.models import Course, Module, Assignment, db
from app.schemas import course_schema, courses_schema, module_schema, modules_schema, assignment_schema, assignments_schema

# Create blueprint
courses_bp = Blueprint('courses', __name__)


@courses_bp.route('/courses', methods=['GET'])
def get_all_courses():
    """
    Get all courses.
    
    Returns:
        JSON response with list of all courses.
    """
    try:
        courses = Course.query.all()
        result = courses_schema.dump(courses)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@courses_bp.route('/courses/<string:course_id>/modules', methods=['GET'])
def get_course_modules(course_id):
    """
    Get all modules for a specific course.
    
    Args:
        course_id: Course identifier
        
    Returns:
        JSON response with list of modules for the course.
    """
    try:
        modules = Module.query.filter_by(course_id=course_id).all()
        result = modules_schema.dump(modules)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@courses_bp.route('/modules/<string:module_id>/assignments', methods=['GET'])
def get_module_assignments(module_id):
    """
    Get all assignments for a specific module.
    
    Args:
        module_id: Module identifier
        
    Returns:
        JSON response with list of assignments for the module.
    """
    try:
        assignments = Assignment.query.filter_by(module_id=module_id).all()
        result = assignments_schema.dump(assignments)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
