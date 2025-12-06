"""
Academic Routes Blueprint.

This module defines Flask routes for academic operations including attendance
tracking, grade management, and submission records.

Endpoints:
    POST /academic/attendance/csv-upload - Upload attendance via CSV
    GET /academic/attendance - Get attendance records (with filters)
    PUT /academic/attendance/<id> - Update attendance record
    GET /academic/submissions - Get submission records (with filters)
    POST /academic/grades/csv-upload - Upload grades via CSV
    PUT /academic/grades/<id> - Update grade
    GET /academic/assignments/<id> - Get assignment details
    GET /academic/registrations/module/<id> - Get module enrollments
"""
from flask import Blueprint, request, jsonify
from app.controllers import academic_controller

# Create blueprint
academic_bp = Blueprint('academic', __name__, url_prefix='/academic')


@academic_bp.route('/attendance/csv-upload', methods=['POST'])
def upload_csv_attendance():
    """
    Upload attendance records from CSV file.
    
    Accepts a CSV file with attendance data. Creates attendance entries for
    existing student/module registrations.
    
    Form Data:
        file: CSV file with headers: registration_id, week, is_present, reason_absent
    
    CSV Format Example:
        registration_id,week,is_present,reason_absent
        1,1,true,
        1,2,false,Sick
        2,1,true,
    
    Returns:
        JSON response with upload summary (201) or error (400, 500)
        
    Example Response:
        {
            "message": "CSV upload completed",
            "processed": 25,
            "created": 20,
            "skipped": 5,
            "details": {
                "students_not_found": ["S999 (Module: M001)"],
                "invalid_rows": []
            }
        }
    """
    # Check if file is present in request
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    csv_file = request.files['file']
    
    # Check if file has a filename
    if csv_file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Check file extension
    if not csv_file.filename.endswith('.csv'):
        return jsonify({"error": "File must be a CSV file"}), 400
    
    return academic_controller.upload_csv_attendance(csv_file)


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


@academic_bp.route('/grades/csv-upload', methods=['POST'])
def upload_csv_grades():
    """
    Upload grades from CSV file.
    
    Accepts a CSV file with grade data. Updates or creates submission grades
    for existing student/assignment combinations.
    
    Form Data:
        file: CSV file with headers: registration_id, assignment_id, grade
    
    CSV Format Example:
        registration_id,assignment_id,grade
        1,A001,85
        1,A002,92
        2,A001,78
    
    Returns:
        JSON response with upload summary (201) or error (400, 500)
        
    Example Response:
        {
            "message": "CSV upload completed",
            "processed": 25,
            "updated": 20,
            "skipped": 5,
            "details": {
                "students_not_found": ["S999 (Assignment: A001)"],
                "invalid_rows": []
            }
        }
    """
    # Check if file is present in request
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    csv_file = request.files['file']
    
    # Check if file has a filename
    if csv_file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Check file extension
    if not csv_file.filename.endswith('.csv'):
        return jsonify({"error": "File must be a CSV file"}), 400
    
    return academic_controller.upload_csv_grades(csv_file)


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