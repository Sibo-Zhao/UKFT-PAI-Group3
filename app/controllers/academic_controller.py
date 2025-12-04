from flask import jsonify
from app.models import WeeklyAttendance, Submission, ModuleRegistration, Assignment, db
from app.views.schemas import attendances_schema, submissions_schema, assignment_schema, attendance_schema, submission_schema, students_schema
from datetime import datetime

def bulk_upload_attendance(data):
    """
    Bulk upload attendance records.
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
    Get attendance records with optional filtering.
    Return student_id and student_name so the frontend can display them.
    """
    try:
        query = WeeklyAttendance.query.join(ModuleRegistration)

        student_id = filters.get("student_id")
        module_id = filters.get("module_id")
        week_number = filters.get("week_number")

        if student_id:
            query = query.filter(ModuleRegistration.student_id == student_id)
        if module_id:
            query = query.filter(ModuleRegistration.module_id == module_id)
        if week_number:
            query = query.filter(WeeklyAttendance.week_number == int(week_number))

        attendance_records = query.all()

        results = []
        for att in attendance_records:
            registration = getattr(att, "registration", None)
            student = getattr(registration, "student", None) if registration else None

            student_id_val = getattr(student, "student_id", None) if student else None
            first_name = getattr(student, "first_name", "") if student else ""
            last_name = getattr(student, "last_name", "") if student else ""
            student_name_val = (f"{first_name} {last_name}").strip() or None

            results.append(
                {
                    "attendance_id": att.attendance_id,
                    "registration_id": att.registration_id,
                    "week_number": att.week_number,
                    "class_date": att.class_date.isoformat() if att.class_date else None,
                    "is_present": att.is_present,
                    "reason_absent": att.reason_absent,
                    "student_id": student_id_val,
                    "student_name": student_name_val,
                }
            )

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_submissions(filters):
    """
    Get submission records with optional filtering.
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
    """Update a specific attendance record."""
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
    """Bulk upload grades for submissions."""
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
    """Update a specific grade and feedback."""
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
    """Get details of a specific assignment."""
    try:
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404
        
        result = assignment_schema.dump(assignment)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_module_registrations(module_id):
    """Get list of students enrolled in a module."""
    try:
        registrations = ModuleRegistration.query.filter_by(module_id=module_id).all()
        students = [reg.student for reg in registrations]
        result = students_schema.dump(students)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
