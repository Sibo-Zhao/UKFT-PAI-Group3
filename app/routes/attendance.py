"""
Attendance Routes.

This module defines API endpoints for attendance management operations including
recording attendance, retrieving attendance data, and generating reports.
"""
from flask import Blueprint, request
from app.controllers.attendance_controller import (
    record_attendance, get_student_attendance, get_module_attendance,
    update_attendance, delete_attendance, get_attendance_report
)

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/attendance', methods=['POST'])
def record_student_attendance():
    """
    Record attendance for a student.
    
    Expected JSON payload:
        {
            "registration_id": int,
            "week_number": int,
            "class_date": "YYYY-MM-DD",
            "is_present": boolean,
            "reason_absent": "string" (optional, required if is_present is false)
        }
        
    Returns:
        JSON response with attendance record
    """
    return record_attendance(request.json)


@attendance_bp.route('/attendance/student/<student_id>', methods=['GET'])
def get_attendance_for_student(student_id):
    """
    Get attendance records for a specific student.
    
    Args:
        student_id (str): The unique identifier of the student
        
    Returns:
        JSON response with student attendance data and summary
    """
    return get_student_attendance(student_id)


@attendance_bp.route('/attendance/module/<module_id>', methods=['GET'])
def get_attendance_for_module(module_id):
    """
    Get attendance summary for all students in a specific module.
    
    Args:
        module_id (str): The unique identifier of the module
        
    Returns:
        JSON response with module attendance data
    """
    return get_module_attendance(module_id)


@attendance_bp.route('/attendance/<int:attendance_id>', methods=['PUT'])
def update_attendance_record(attendance_id):
    """
    Update an existing attendance record.
    
    Args:
        attendance_id (int): The unique identifier of the attendance record
        
    Expected JSON payload:
        {
            "is_present": boolean (optional),
            "reason_absent": "string" (optional),
            "class_date": "YYYY-MM-DD" (optional)
        }
        
    Returns:
        JSON response with updated attendance record
    """
    return update_attendance(attendance_id, request.json)


@attendance_bp.route('/attendance/<int:attendance_id>', methods=['DELETE'])
def delete_attendance_record(attendance_id):
    """
    Delete an attendance record.
    
    Args:
        attendance_id (int): The unique identifier of the attendance record
        
    Returns:
        JSON response with success message
    """
    return delete_attendance(attendance_id)


@attendance_bp.route('/attendance/report', methods=['GET'])
def generate_attendance_report():
    """
    Generate attendance report for a date range.
    
    Query parameters:
        start_date (optional): Start date in YYYY-MM-DD format
        end_date (optional): End date in YYYY-MM-DD format
        
    Returns:
        JSON response with attendance report and statistics
    """
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    return get_attendance_report(start_date, end_date)