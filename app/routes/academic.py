"""
Attendance and Submissions routes blueprint.
Flask blueprint for academic attendance and submission endpoints.
"""
from flask import Blueprint, jsonify, request
from app.models import WeeklyAttendance, Submission, ModuleRegistration, db
from app.schemas import attendances_schema, submissions_schema
from datetime import datetime

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
    try:
        data = request.get_json()
        attendance_records = data.get('attendance_records', [])
        
        if not attendance_records:
            return jsonify({"error": "No attendance records provided"}), 400
        
        created_count = 0
        for record in attendance_records:
            # Validate registration exists
            registration = ModuleRegistration.query.get(record['registration_id'])
            if not registration:
                continue  # Skip invalid registrations
            
            attendance = WeeklyAttendance(
                registration_id=record['registration_id'],
                week_number=record['week_number'],
                class_date=datetime.fromisoformat(record['class_date']),
                is_present=record['is_present'],
                reason_absent=record.get('reason_absent')
            )
            db.session.add(attendance)
            created_count += 1
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully created {created_count} attendance records",
            "count": created_count
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


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
    try:
        query = WeeklyAttendance.query
        
        # Apply filters if provided
        student_id = request.args.get('student_id')
        module_id = request.args.get('module_id')
        week_number = request.args.get('week_number')
        
        if student_id or module_id:
            # Join with registrations to filter by student/module
            query = query.join(ModuleRegistration)
            if student_id:
                query = query.filter(ModuleRegistration.student_id == student_id)
            if module_id:
                query = query.filter(ModuleRegistration.module_id == module_id)
        
        if week_number:
            query = query.filter(WeeklyAttendance.week_number == int(week_number))
        
        attendance_records = query.all()
        result = attendances_schema.dump(attendance_records)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    try:
        query = Submission.query
        
        # Apply filters
        assignment_id = request.args.get('assignment_id')
        student_id = request.args.get('student_id')
        module_id = request.args.get('module_id')
        
        if student_id or module_id:
            query = query.join(ModuleRegistration)
            if student_id:
                query = query.filter(ModuleRegistration.student_id == student_id)
            if module_id:
                query = query.filter(ModuleRegistration.module_id == module_id)
        
        if assignment_id:
            query = query.filter(Submission.assignment_id == assignment_id)
        
        submissions = query.all()
        result = submissions_schema.dump(submissions)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
