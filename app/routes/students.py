"""
Student Routes Blueprint.

This module defines Flask routes for student management operations including
profile retrieval, analytics, at-risk identification, and CRUD operations.

Endpoints:
    GET /students - List all students
    GET /students/<id> - Get student details
    GET /students/at_risk - Identify at-risk students
    GET /students/<id>/academic_performance - Get academic metrics
    GET /students/<id>/wellbeing_trends - Get wellbeing trends
    GET /students/<id>/full_profile - Get complete profile
    PUT /students/<id> - Update student information
    DELETE /students/<id> - Delete student (cascade)
"""
from flask import Blueprint, request
from app.controllers import student_controller

# Create blueprint
students_bp = Blueprint('students', __name__, url_prefix='/students')


@students_bp.route('', methods=['GET'])
def get_all_students():
    """Get all students in the system."""
    return student_controller.get_all_students()


@students_bp.route('/<string:student_id>', methods=['GET'])
def get_student(student_id):
    """Get detailed information for a specific student."""
    return student_controller.get_student(student_id)

@students_bp.route('', methods=['POST'])
def create_student_route():
    data = request.get_json() or {}
    return student_controller.create_student(data)


@students_bp.route('/at_risk', methods=['GET'])
def get_at_risk_students():
    """
    Identify at-risk students based on multiple criteria:
    - Low attendance (<70%)
    - High stress levels (avg >4)
    - Low sleep (<6 hours avg)
    - Low social connection (avg <2)
    - Failing grades (<40%)
    
    Returns:
        JSON response with list of at-risk students and their risk factors
    """
    return student_controller.get_at_risk_students()


@students_bp.route('/<string:student_id>/academic_performance', methods=['GET'])
def get_academic_performance(student_id):
    """
    Get academic performance metrics for a student.
    
    Returns:
        JSON with grades, attendance, and submission stats
    """
    return student_controller.get_academic_performance(student_id)


@students_bp.route('/<string:student_id>/wellbeing_trends', methods=['GET'])
def get_wellbeing_trends(student_id):
    """
    Get wellbeing trend analysis for a student.
    
    Returns:
        JSON with stress, sleep, and social connection trends
    """
    return student_controller.get_wellbeing_trends(student_id)


@students_bp.route('/<string:student_id>/full_profile', methods=['GET'])
def get_full_profile(student_id):
    """
    Get complete student profile with all data.
    
    Returns:
        JSON with student info, academic performance, and wellbeing data
    """
    return student_controller.get_full_profile(student_id)

@students_bp.route('/<string:student_id>', methods=['PUT'])
def update_student(student_id):
    """
    Update student information.
    
    Request Body:
        JSON with fields to update (first_name, last_name, email, enrolled_year, current_course_id)
        
    Returns:
        JSON response with updated student (200) or error (404/400)
    """
    data = request.get_json()
    return student_controller.update_student(student_id, data)

@students_bp.route('/<string:student_id>', methods=['DELETE'])
def delete_student(student_id):
    """
    Delete a student and all related records.
    
    This performs a cascade delete, removing:
    - All module registrations
    - All weekly surveys
    - All attendance records
    - All submissions
    
    Returns:
        JSON response with success message (200) or error (404)
    """
    return student_controller.delete_student(student_id)
