"""
Attendance and Submissions routes blueprint.
Flask blueprint for academic attendance and submission endpoints.
"""
from flask import Blueprint, request
from app.controllers import academic_controller

# Create blueprint
academic_bp = Blueprint('academic', __name__, url_prefix='/academic')


@academic_bp.route('/attendance/bulk', methods=['POST'])
def bulk_upload_attendance():
    """
    Bulk upload attendance records.
    
    Request Body:
        {
            "attendance_records": [
                {
                    "registration_id": 1,
                    "week_number": 1,
                    "class_date": "2025-01-15",
                    "is_present": true,
                    "reason_absent": null
                }
            ]
        }
        
    Returns:
        JSON response with created count (201) or error (400)
    """
    data = request.get_json()
    return academic_controller.bulk_upload_attendance(data)


@academic_bp.route('/attendance', methods=['GET'])
def get_attendance():
    """
    Get attendance records with optional filtering.
    
    Query Parameters:
        student_id (optional): Filter by student
        module_id (optional): Filter by module
        week_number (optional): Filter by week
        
    Returns:
        JSON response with attendance records
    """
    filters = {
        'student_id': request.args.get('student_id'),
        'module_id': request.args.get('module_id'),
        'week_number': request.args.get('week_number')
    }
    return academic_controller.get_attendance(filters)


@academic_bp.route('/submissions', methods=['GET'])
def get_submissions():
    """
    Get submission records with optional filtering.
    
    Query Parameters:
        student_id (optional): Filter by student
        assignment_id (optional): Filter by assignment
        module_id (optional): Filter by module
        
    Returns:
        JSON response with submission records
    """
    filters = {
        'student_id': request.args.get('student_id'),
        'assignment_id': request.args.get('assignment_id'),
        'module_id': request.args.get('module_id')
    }
    return academic_controller.get_submissions(filters)


@academic_bp.route('/attendance/<int:attendance_id>', methods=['PUT'])
def update_attendance(attendance_id):
    """Update a specific attendance record."""
    data = request.get_json()
    return academic_controller.update_attendance(attendance_id, data)


@academic_bp.route('/grades/bulk', methods=['POST'])
def bulk_upload_grades():
    """Bulk upload grades for submissions."""
    data = request.get_json()
    return academic_controller.bulk_upload_grades(data)


@academic_bp.route('/grades/<int:submission_id>', methods=['PUT'])
def update_grade(submission_id):
    """Update a specific grade and feedback."""
    data = request.get_json()
    return academic_controller.update_grade(submission_id, data)


@academic_bp.route('/assignments/<string:assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    """Get details of a specific assignment."""
    return academic_controller.get_assignment(assignment_id)


@academic_bp.route('/registrations/module/<string:module_id>', methods=['GET'])
def get_module_registrations(module_id):
    """Get list of students enrolled in a module."""
    return academic_controller.get_module_registrations(module_id)