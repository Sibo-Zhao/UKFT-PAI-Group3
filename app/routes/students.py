"""
Student analytics and at-risk identification routes.
Flask blueprint for student profile and analytics endpoints.
"""
from flask import Blueprint
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
