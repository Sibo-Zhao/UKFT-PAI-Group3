from flask import Blueprint, jsonify
from sqlalchemy import func, and_
from app.models import Student, ModuleRegistration, WeeklyAttendance, Submission, Assignment, db

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/module/<string:module_id>/academic', methods=['GET'])
def get_module_academic_report(module_id):
    """Get academic report for a module (grades, attendance, submissions)."""
    try:
        # Get all registrations for this module
        registrations = ModuleRegistration.query.filter_by(module_id=module_id).all()
        registration_ids = [r.registration_id for r in registrations]
        
        if not registration_ids:
            return jsonify({"error": "No students registered for this module"}), 404
        
        # Calculate class average grades
        avg_grade = db.session.query(func.avg(Submission.grade_achieved)).filter(
            Submission.registration_id.in_(registration_ids)
        ).scalar() or 0
        
        # Calculate submission rates
        total_assignments = Assignment.query.filter_by(module_id=module_id).count()
        total_possible_submissions = len(registration_ids) * total_assignments
        actual_submissions = Submission.query.filter(
            Submission.registration_id.in_(registration_ids)
        ).count()
        
        submission_rate = (actual_submissions / total_possible_submissions * 100) if total_possible_submissions > 0 else 0
        
        # Calculate attendance percentage
        total_attendance_records = WeeklyAttendance.query.filter(
            WeeklyAttendance.registration_id.in_(registration_ids)
        ).count()
        
        present_count = WeeklyAttendance.query.filter(
            and_(
                WeeklyAttendance.registration_id.in_(registration_ids),
                WeeklyAttendance.is_present == True
            )
        ).count()
        
        attendance_rate = (present_count / total_attendance_records * 100) if total_attendance_records > 0 else 0
        
        return jsonify({
            "module_id": module_id,
            "class_average_grade": round(float(avg_grade), 2),
            "submission_rate": round(submission_rate, 2),
            "attendance_rate": round(attendance_rate, 2),
            "total_students": len(registrations),
            "total_assignments": total_assignments
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@reports_bp.route('/student/<string:student_id>/academic', methods=['GET'])
def get_student_academic_report(student_id):
    """Get academic report for a specific student."""
    try:
        # student = Student.query.get(student_id)
        student = db.session.get(Student, student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        registrations = ModuleRegistration.query.filter_by(student_id=student_id).all()
        registration_ids = [r.registration_id for r in registrations]
        
        # Get grades
        submissions = Submission.query.filter(
            Submission.registration_id.in_(registration_ids)
        ).all()
        
        grades = []
        for sub in submissions:
            grades.append({
                "assignment_id": sub.assignment_id,
                "grade_achieved": float(sub.grade_achieved) if sub.grade_achieved else None,
                "submitted_at": sub.submitted_at.isoformat() if sub.submitted_at else None,
                "feedback": sub.grader_feedback
            })
        
        # Get attendance
        attendance_records = WeeklyAttendance.query.filter(
            WeeklyAttendance.registration_id.in_(registration_ids)
        ).all()
        
        attendance_data = []
        for att in attendance_records:
            attendance_data.append({
                "week_number": att.week_number,
                "class_date": att.class_date.isoformat(),
                "is_present": att.is_present,
                "reason_absent": att.reason_absent
            })
        
        return jsonify({
            "student_id": student_id,
            "name": f"{student.first_name} {student.last_name}",
            "grades": grades,
            "attendance": attendance_data,
            "modules_enrolled": len(registrations)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500