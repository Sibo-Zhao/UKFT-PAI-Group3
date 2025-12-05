"""
Student Routes Blueprint.

This module defines Flask routes for student management operations including
profile retrieval, analytics, at-risk identification, and CRUD operations.

Endpoints:
    GET /students - List all students
    GET /students/<id> - Get student details
    POST /students - Create new student
    PUT /students/<id> - Update student information
    DELETE /students/<id> - Delete student (cascade)
    GET /students/at_risk - Identify at-risk students
    GET /students/<id>/academic-performance - Comprehensive academic analytics with filtering
    GET /students/<id>/wellbeing_trends - Get wellbeing trends
    GET /students/<id>/full_profile - Get complete profile
    GET /students/course/<course_id>/comparison - Compare students in a course
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


@students_bp.route('/<string:student_id>/academic-performance', methods=['GET'])
def get_student_academic_performance(student_id):
    """
    Get comprehensive student academic performance across their course modules.
    
    Query Parameters:
        module_id (optional): Filter by specific module
        week_start (optional): Start week for filtering (integer)
        week_end (optional): End week for filtering (integer)
        
    Returns:
        JSON response with comprehensive academic performance including:
        - Average weekly attendance rate
        - Average grades across assignments
        - Average submission timing (early/late patterns)
        - Wellbeing trends (stress, sleep, social connection)
        - Module-by-module breakdown
    """
    module_id = request.args.get('module_id')
    week_start = request.args.get('week_start', type=int)
    week_end = request.args.get('week_end', type=int)
    assignment_type = request.args.get('assignment_type')
    
    return student_controller.get_student_analytics(
        student_id, module_id, week_start, week_end, assignment_type
    )


@students_bp.route('/course/<string:course_id>/comparison', methods=['GET'])
def get_course_student_comparison(course_id):
    """
    Compare all students in a course across specified metrics.
    
    Query Parameters:
        metric (optional): Metric to compare - 'attendance', 'grades', 'wellbeing', or 'all' (default: 'attendance')
        week_start (optional): Start week for filtering (integer)
        week_end (optional): End week for filtering (integer)
        
    Returns:
        JSON response with student comparison data including:
        - Ranked list of students by selected metric
        - Course-wide statistics
        - Individual student performance data
    """
    metric = request.args.get('metric', 'attendance')
    week_start = request.args.get('week_start', type=int)
    week_end = request.args.get('week_end', type=int)
    
    return student_controller.get_course_student_comparison(
        course_id, metric, week_start, week_end
    )
