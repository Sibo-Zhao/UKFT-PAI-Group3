"""
Reports Controller Module.

This module generates various analytical reports including academic performance,
early warning indicators, and weekly wellbeing trends.
"""
from flask import jsonify
from sqlalchemy import func, and_, desc
from app.models import Student, ModuleRegistration, WeeklyAttendance, Submission, Assignment, WeeklySurvey, db


def get_module_academic_report(module_id):
    """
    Generate comprehensive academic report for a specific module.
    
    Calculates aggregate statistics including average grades, submission rates,
    and attendance rates for all students enrolled in the module.
    
    Args:
        module_id (str): The unique identifier of the module.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with module statistics
            - int: HTTP status code
                - 200: Success
                - 404: No students registered for module
                - 500: Server error
    
    Example Response:
        {
            "module_id": "MOD101",
            "class_average_grade": 78.5,
            "submission_rate": 92.3,
            "attendance_rate": 87.5,
            "total_students": 45,
            "total_assignments": 8
        }
    """
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

def get_student_academic_report(student_id):
    """
    Generate comprehensive academic report for a specific student.
    
    Retrieves all grades, attendance records, and enrollment information
    for the specified student.
    
    Args:
        student_id (str): The unique identifier of the student.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with student academic data
            - int: HTTP status code
                - 200: Success
                - 404: Student not found
                - 500: Server error
    
    Example Response:
        {
            "student_id": "S001",
            "name": "John Doe",
            "grades": [...],
            "attendance": [...],
            "modules_enrolled": 4
        }
    """
    try:
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

def get_early_warning():
    """
    Generate early warning report for at-risk students.
    
    Identifies students with concerning wellbeing indicators based on their
    most recent survey responses. Flags students with high stress (≥4) or
    insufficient sleep (<5 hours).
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with at-risk student lists
            - int: HTTP status code
                - 200: Success
                - 500: Server error
    
    Example Response:
        {
            "high_stress_students": {
                "count": 12,
                "students": [
                    {
                        "student_id": "S001",
                        "name": "John Doe",
                        "email": "john@example.com",
                        "stress_level": 5,
                        "sleep_hours": 6.5,
                        "week_number": 8
                    }
                ]
            },
            "low_sleep_students": {
                "count": 8,
                "students": [...]
            }
        }
    
    Note:
        Uses the most recent survey submission for each student across all
        their module registrations.
    """
    try:
        # Get all students with their registrations
        all_students = Student.query.all()
        
        # Get the latest survey for each student
        students_high_stress = []
        students_low_sleep = []
        
        for student in all_students:
            registrations = ModuleRegistration.query.filter_by(student_id=student.student_id).all()
            registration_ids = [r.registration_id for r in registrations]
            
            if not registration_ids:
                continue
            
            # Get the most recent survey for this student (across all their registrations)
            latest_survey = WeeklySurvey.query.filter(
                WeeklySurvey.registration_id.in_(registration_ids)
            ).order_by(desc(WeeklySurvey.submitted_at)).first()
            
            if not latest_survey:
                continue
            
            student_info = {
                "student_id": student.student_id,
                "name": f"{student.first_name} {student.last_name}",
                "email": student.email,
                "enrolled_year": student.enrolled_year,
                "stress_level": latest_survey.stress_level,
                "sleep_hours": float(latest_survey.sleep_hours) if latest_survey.sleep_hours else None,
                "week_number": latest_survey.week_number,
                "submitted_at": latest_survey.submitted_at.isoformat() if latest_survey.submitted_at else None
            }
            
            # Check for high stress (4-5)
            if latest_survey.stress_level and latest_survey.stress_level >= 4:
                students_high_stress.append(student_info)
            
            # Check for low sleep (< 5 hours)
            if latest_survey.sleep_hours and latest_survey.sleep_hours < 5:
                students_low_sleep.append(student_info)
        
        return jsonify({
            "high_stress_students": {
                "count": len(students_high_stress),
                "students": students_high_stress
            },
            "low_sleep_students": {
                "count": len(students_low_sleep),
                "students": students_low_sleep
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_weekly_report():
    """
    Generate weekly wellbeing trend report.
    
    Calculates average stress levels and sleep hours for the current week
    and compares them with the previous week to identify trends.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with weekly statistics
            - int: HTTP status code
                - 200: Success
                - 404: No survey data available
                - 500: Server error
    
    Example Response:
        {
            "current_week": 8,
            "previous_week": 7,
            "stress_level": {
                "current_week_average": 3.2,
                "previous_week_average": 2.8,
                "change": 0.4,
                "change_description": "Increased"
            },
            "sleep_hours": {
                "current_week_average": 7.1,
                "previous_week_average": 7.5,
                "change": -0.4,
                "change_description": "Decreased"
            }
        }
    """
    try:
        # Get the latest week number from all surveys
        latest_week = db.session.query(func.max(WeeklySurvey.week_number)).scalar()
        
        if not latest_week:
            return jsonify({
                "error": "No survey data available"
            }), 404
        
        # Calculate averages for current week (latest week)
        current_week_stress = db.session.query(func.avg(WeeklySurvey.stress_level)).filter(
            WeeklySurvey.week_number == latest_week
        ).scalar() or 0
        
        current_week_sleep = db.session.query(func.avg(WeeklySurvey.sleep_hours)).filter(
            WeeklySurvey.week_number == latest_week
        ).scalar() or 0
        
        # Calculate averages for previous week
        previous_week = latest_week - 1
        previous_week_stress = None
        previous_week_sleep = None
        stress_change = None
        sleep_change = None
        
        if previous_week > 0:
            previous_week_stress = db.session.query(func.avg(WeeklySurvey.stress_level)).filter(
                WeeklySurvey.week_number == previous_week
            ).scalar()
            
            previous_week_sleep = db.session.query(func.avg(WeeklySurvey.sleep_hours)).filter(
                WeeklySurvey.week_number == previous_week
            ).scalar()
            
            # Calculate changes
            if previous_week_stress is not None:
                stress_change = round(float(current_week_stress) - float(previous_week_stress), 2)
            
            if previous_week_sleep is not None:
                sleep_change = round(float(current_week_sleep) - float(previous_week_sleep), 2)
        
        return jsonify({
            "current_week": latest_week,
            "previous_week": previous_week if previous_week > 0 else None,
            "stress_level": {
                "current_week_average": round(float(current_week_stress), 2),
                "previous_week_average": round(float(previous_week_stress), 2) if previous_week_stress is not None else None,
                "change": stress_change,
                "change_description": _get_change_description(stress_change) if stress_change is not None else None
            },
            "sleep_hours": {
                "current_week_average": round(float(current_week_sleep), 2),
                "previous_week_average": round(float(previous_week_sleep), 2) if previous_week_sleep is not None else None,
                "change": sleep_change,
                "change_description": _get_change_description(sleep_change, is_sleep=True) if sleep_change is not None else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _get_change_description(change, is_sleep=False):
    """
    Generate human-readable description of metric changes.
    
    Helper function to convert numeric changes into descriptive text.
    
    Args:
        change (float): The numeric change value (can be positive, negative, or zero).
        is_sleep (bool): Whether the metric is sleep-related (currently unused,
            reserved for future sleep-specific descriptions).
    
    Returns:
        str: Description of the change ("Increased", "Decreased", or "No change").
        None: If change is None.
    """
    if change is None:
        return None
    
    if is_sleep:
        if change > 0:
            return "Increased"
        elif change < 0:
            return "Decreased"
        else:
            return "No change"
    else:
        if change > 0:
            return "Increased"
        elif change < 0:
            return "Decreased"
        else:
            return "No change"
