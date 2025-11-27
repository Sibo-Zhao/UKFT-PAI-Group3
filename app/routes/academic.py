"""
Attendance and Submissions routes blueprint.
Flask blueprint for academic attendance and submission endpoints.
"""
from flask import Blueprint, jsonify, request
from app.models import WeeklyAttendance, Submission, ModuleRegistration, db, Assignment
from app.schemas import attendances_schema, submissions_schema, assignment_schema
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
            # registration = ModuleRegistration.query.get(record['registration_id'])
            registration = db.session.get(ModuleRegistration, record['registration_id'])
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

@academic_bp.route('/attendance/<int:attendance_id>', methods=['PUT'])
def update_attendance(attendance_id):
    """Update a specific attendance record."""
    try:
        # attendance = WeeklyAttendance.query.get(attendance_id)
        attendance = db.session.get(WeeklyAttendance, attendance_id)
        if not attendance:
            return jsonify({"error": "Attendance record not found"}), 404
        
        update_data = request.get_json()
        if 'is_present' in update_data:
            attendance.is_present = update_data['is_present']
        if 'reason_absent' in update_data:
            attendance.reason_absent = update_data['reason_absent']
        
        db.session.commit()
        result = attendance_schema.dump(attendance)
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@academic_bp.route('/grades/bulk', methods=['POST'])
def bulk_upload_grades():
    """Bulk upload grades for submissions."""
    try:
        data = request.get_json()
        grades_data = data.get('grades', [])
        
        if not grades_data:
            return jsonify({"error": "No grades provided"}), 400
        
        updated_count = 0
        for grade_data in grades_data:
            # submission = Submission.query.get(grade_data['submission_id'])
            submission = db.session.get(Submission, grade_data['submission_id'])
            if submission:
                submission.grade_achieved = grade_data.get('grade_achieved')
                submission.grader_feedback = grade_data.get('grader_feedback')
                updated_count += 1
        
        db.session.commit()
        return jsonify({"message": f"Updated {updated_count} grades"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@academic_bp.route('/grades/<int:submission_id>', methods=['PUT'])
def update_grade(submission_id):
    """Update a specific grade and feedback."""
    try:
        # submission = Submission.query.get(submission_id)
        submission = db.session.get(Submission, submission_id)
        if not submission:
            return jsonify({"error": "Submission not found"}), 404
        
        update_data = request.get_json()
        if 'grade_achieved' in update_data:
            submission.grade_achieved = update_data['grade_achieved']
        if 'grader_feedback' in update_data:
            submission.grader_feedback = update_data['grader_feedback']
        
        db.session.commit()
        result = submission_schema.dump(submission)
        return jsonify(result), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@academic_bp.route('/assignments/<string:assignment_id>', methods=['GET'])
def get_assignment(assignment_id):
    """Get details of a specific assignment."""
    try:
        # assignment = Assignment.query.get(assignment_id)
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404
        
        result = assignment_schema.dump(assignment)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@academic_bp.route('/registrations/module/<string:module_id>', methods=['GET'])
def get_module_registrations(module_id):
    """Get list of students enrolled in a module."""
    try:
        from app.schemas import student_schema
        
        registrations = ModuleRegistration.query.filter_by(module_id=module_id).all()
        students = [reg.student for reg in registrations]
        result = students_schema.dump(students)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500