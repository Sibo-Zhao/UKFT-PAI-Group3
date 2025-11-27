from flask import jsonify
from app.models import Course, Module, Assignment
from app.views.schemas import courses_schema, modules_schema, assignments_schema

def get_all_courses():
    """
    Get all courses.
    """
    try:
        courses = Course.query.all()
        result = courses_schema.dump(courses)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_course_modules(course_id):
    """
    Get all modules for a specific course.
    """
    try:
        modules = Module.query.filter_by(course_id=course_id).all()
        result = modules_schema.dump(modules)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_module_assignments(module_id):
    """
    Get all assignments for a specific module.
    """
    try:
        assignments = Assignment.query.filter_by(module_id=module_id).all()
        result = assignments_schema.dump(assignments)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
