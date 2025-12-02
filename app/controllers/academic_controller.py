"""
Academic Controller Module.

This module handles academic-related operations including attendance tracking,
grade management, and submission records.
"""
from flask import jsonify
from app.models import WeeklyAttendance, Submission, ModuleRegistration, Assignment, db
from app.views.schemas import attendances_schema, submissions_schema, assignment_schema, attendance_schema, submission_schema, students_schema
from datetime import datetime


def bulk_upload_attendance(data):
    """
    Bulk upload multiple attendance records at once.
    
    Validates each attendance record and creates entries in the database.
    Invalid registrations are skipped without failing the entire operation.
    
    Args:
        data (dict): Request data containing attendance records.
            Expected structure:
                {
                    "attendance_records": [
                        {
                            "registration_id": int,
                            "week_number": int,
                            "class_date": str (ISO date format),
                            "is_present": bool,
                            "reason_absent": str (optional)
                        }
                    ]
                }
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with upload summary
            - int: HTTP status code
                - 201: Upload successful
                - 400: No attendance records provided
                - 500: Server error
    
    Example Response:
        {
            "message": "Successfully created 45 attendance records",
            "count": 45
        }
    """
    try:
        attendance_records = data.get('attendance_records', [])
        
        if not attendance_records:
            return jsonify({"error": "No attendance records provided"}), 400
        
        created_count = 0
        for record in attendance_records:
            # Validate registration exists
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

def get_attendance(filters):
    """
    Retrieve attendance records with optional filtering.
    
    Supports filtering by student, module, and week number to narrow down results.
    
    Args:
        filters (dict): Dictionary containing optional filter parameters.
            Supported keys:
                - student_id (str): Filter by specific student
                - module_id (str): Filter by specific module
                - week_number (str): Filter by specific week
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with filtered attendance records
            - int: HTTP status code
                - 200: Success
                - 500: Server error
    """
    try:
        query = WeeklyAttendance.query
        
        # Apply filters if provided
        student_id = filters.get('student_id')
        module_id = filters.get('module_id')
        week_number = filters.get('week_number')
        
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

def get_submissions(filters):
    """
    Retrieve submission records with optional filtering.
    
    Supports filtering by student, assignment, and module to narrow down results.
    
    Args:
        filters (dict): Dictionary containing optional filter parameters.
            Supported keys:
                - student_id (str): Filter by specific student
                - assignment_id (str): Filter by specific assignment
                - module_id (str): Filter by specific module
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with filtered submission records
            - int: HTTP status code
                - 200: Success
                - 500: Server error
    """
    try:
        query = Submission.query
        
        # Apply filters
        assignment_id = filters.get('assignment_id')
        student_id = filters.get('student_id')
        module_id = filters.get('module_id')
        
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

def update_attendance(attendance_id, update_data):
    """
    Update a specific attendance record.
    
    Allows modification of attendance status and absence reason.
    
    Args:
        attendance_id (int): The unique identifier of the attendance record.
        update_data (dict): Dictionary containing fields to update.
            Allowed keys:
                - is_present (bool): New attendance status
                - reason_absent (str): New absence reason
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with updated attendance record
            - int: HTTP status code
                - 200: Update successful
                - 404: Attendance record not found
                - 500: Server error
    """
    try:
        attendance = db.session.get(WeeklyAttendance, attendance_id)
        if not attendance:
            return jsonify({"error": "Attendance record not found"}), 404
        
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

def bulk_upload_grades(data):
    """
    Bulk upload grades for multiple submissions.
    
    Updates grade and feedback information for existing submission records.
    
    Args:
        data (dict): Request data containing grade information.
            Expected structure:
                {
                    "grades": [
                        {
                            "submission_id": int,
                            "grade_achieved": float,
                            "grader_feedback": str (optional)
                        }
                    ]
                }
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with update summary
            - int: HTTP status code
                - 200: Update successful
                - 400: No grades provided
                - 500: Server error
    """
    try:
        grades_data = data.get('grades', [])
        
        if not grades_data:
            return jsonify({"error": "No grades provided"}), 400
        
        updated_count = 0
        for grade_data in grades_data:
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

def update_grade(submission_id, update_data):
    """
    Update grade and feedback for a specific submission.
    
    Args:
        submission_id (int): The unique identifier of the submission.
        update_data (dict): Dictionary containing fields to update.
            Allowed keys:
                - grade_achieved (float): New grade value
                - grader_feedback (str): New feedback text
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with updated submission
            - int: HTTP status code
                - 200: Update successful
                - 404: Submission not found
                - 500: Server error
    """
    try:
        submission = db.session.get(Submission, submission_id)
        if not submission:
            return jsonify({"error": "Submission not found"}), 404
        
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

def get_assignment(assignment_id):
    """
    Retrieve details of a specific assignment.
    
    Args:
        assignment_id (str): The unique identifier of the assignment.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with assignment details
            - int: HTTP status code
                - 200: Success
                - 404: Assignment not found
                - 500: Server error
    """
    try:
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404
        
        result = assignment_schema.dump(assignment)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_module_registrations(module_id):
    """
    Retrieve list of students enrolled in a specific module.
    
    Args:
        module_id (str): The unique identifier of the module.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with list of enrolled students
            - int: HTTP status code
                - 200: Success
                - 500: Server error
    """
    try:
        registrations = ModuleRegistration.query.filter_by(module_id=module_id).all()
        students = [reg.student for reg in registrations]
        result = students_schema.dump(students)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
