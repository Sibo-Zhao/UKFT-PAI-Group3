"""
Course Controller Module.

This module handles course, module, and assignment retrieval operations.
Provides endpoints for accessing course catalog information and related data.
"""
from flask import jsonify
from app.models import Course, Module, Assignment
from app.views.schemas import courses_schema, modules_schema, assignments_schema


def get_all_courses():
    """
    Retrieve all courses from the database.
    
    Fetches all course records and serializes them using the course schema.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with list of courses
            - int: HTTP status code
                - 200: Success
                - 500: Server error
    
    Example Response:
        [
            {
                "course_id": "CS101",
                "course_name": "Introduction to Computer Science",
                "total_credits": 180,
                "created_at": "2025-01-01T00:00:00"
            }
        ]
    """
    try:
        courses = Course.query.all()
        result = courses_schema.dump(courses)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_course_modules(course_id):
    """
    Retrieve all modules associated with a specific course.
    
    Fetches all module records for the given course ID and serializes them.
    
    Args:
        course_id (str): The unique identifier of the course.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with list of modules
            - int: HTTP status code
                - 200: Success
                - 500: Server error
    
    Example Response:
        [
            {
                "module_id": "MOD101",
                "course_id": "CS101",
                "module_name": "Programming Fundamentals",
                "duration_weeks": 12
            }
        ]
    """
    try:
        modules = Module.query.filter_by(course_id=course_id).all()
        result = modules_schema.dump(modules)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_module_assignments(module_id):
    """
    Retrieve all assignments associated with a specific module.
    
    Fetches all assignment records for the given module ID and serializes them.
    
    Args:
        module_id (str): The unique identifier of the module.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with list of assignments
            - int: HTTP status code
                - 200: Success
                - 500: Server error
    
    Example Response:
        [
            {
                "assignment_id": "A001",
                "module_id": "MOD101",
                "title": "Final Project",
                "description": "Complete the final project",
                "due_date": "2025-12-15T23:59:59",
                "max_score": 100,
                "weightage_percent": 30.0
            }
        ]
    """
    try:
        assignments = Assignment.query.filter_by(module_id=module_id).all()
        result = assignments_schema.dump(assignments)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
