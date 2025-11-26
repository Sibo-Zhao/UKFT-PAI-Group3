"""
Student analytics and at-risk identification routes.
Flask blueprint for student profile and analytics endpoints.
"""
from flask import Blueprint, jsonify, request
from sqlalchemy import func, and_
from app.models import Student, ModuleRegistration, WeeklySurvey, WeeklyAttendance, Submission, db
from datetime import datetime

# Create blueprint
students_bp = Blueprint('students', __name__, url_prefix='/students')


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
    try:
        at_risk_students = []
        
        # Get all active students
        students = Student.query.all()
        
        for student in students:
            risk_factors = []
            risk_score = 0
            
            # Get student's registrations
            registrations = ModuleRegistration.query.filter_by(
                student_id=student.student_id
            ).all()
            
            if not registrations:
                continue
            
            registration_ids = [r.registration_id for r in registrations]
            
            # Check attendance
            total_attendance = WeeklyAttendance.query.filter(
                WeeklyAttendance.registration_id.in_(registration_ids)
            ).count()
            
            if total_attendance > 0:
                present_count = WeeklyAttendance.query.filter(
                    and_(
                        WeeklyAttendance.registration_id.in_(registration_ids),
                        WeeklyAttendance.is_present == True
                    )
                ).count()
                
                attendance_rate = (present_count / total_attendance) * 100
                if attendance_rate < 70:
                    risk_factors.append("low_attendance")
                    risk_score += 2.5
            
            # Check stress levels
            avg_stress = db.session.query(func.avg(WeeklySurvey.stress_level)).filter(
                WeeklySurvey.registration_id.in_(registration_ids)
            ).scalar()
            
            if avg_stress and avg_stress > 4:
                risk_factors.append("high_stress")
                risk_score += 3.0
            
            # Check sleep hours
            avg_sleep = db.session.query(func.avg(WeeklySurvey.sleep_hours)).filter(
                WeeklySurvey.registration_id.in_(registration_ids)
            ).scalar()
            
            if avg_sleep and avg_sleep < 6:
                risk_factors.append("low_sleep")
                risk_score += 2.0
            
            # Check social connection
            avg_social = db.session.query(func.avg(WeeklySurvey.social_connection_score)).filter(
                WeeklySurvey.registration_id.in_(registration_ids)
            ).scalar()
            
            if avg_social and avg_social < 2:
                risk_factors.append("low_social_connection")
                risk_score += 2.0
            
            # Check grades
            avg_grade = db.session.query(func.avg(Submission.grade_achieved)).filter(
                Submission.registration_id.in_(registration_ids)
            ).scalar()
            
            if avg_grade and avg_grade < 40:
                risk_factors.append("failing_grades")
                risk_score += 3.5
            
            # If student has any risk factors, add to list
            if risk_factors:
                at_risk_students.append({
                    "student_id": student.student_id,
                    "name": f"{student.first_name} {student.last_name}",
                    "email": student.email,
                    "risk_factors": risk_factors,
                    "risk_score": round(risk_score, 2)
                })
        
        # Sort by risk score (highest first)
        at_risk_students.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return jsonify({
            "at_risk_students": at_risk_students,
            "total_count": len(at_risk_students)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@students_bp.route('/<string:student_id>/academic_performance', methods=['GET'])
def get_academic_performance(student_id):
    """
    Get academic performance metrics for a student.
    
    Returns:
        JSON with grades, attendance, and submission stats
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        registrations = ModuleRegistration.query.filter_by(student_id=student_id).all()
        registration_ids = [r.registration_id for r in registrations]
        
        # Calculate metrics
        avg_grade = db.session.query(func.avg(Submission.grade_achieved)).filter(
            Submission.registration_id.in_(registration_ids)
        ).scalar() or 0
        
        total_submissions = Submission.query.filter(
            Submission.registration_id.in_(registration_ids)
        ).count()
        
        total_attendance = WeeklyAttendance.query.filter(
            WeeklyAttendance.registration_id.in_(registration_ids)
        ).count()
        
        present_count = WeeklyAttendance.query.filter(
            and_(
                WeeklyAttendance.registration_id.in_(registration_ids),
                WeeklyAttendance.is_present == True
            )
        ).count()
        
        attendance_rate = (present_count / total_attendance * 100) if total_attendance > 0 else 0
        
        return jsonify({
            "student_id": student_id,
            "name": f"{student.first_name} {student.last_name}",
            "average_grade": round(float(avg_grade), 2),
            "total_submissions": total_submissions,
            "attendance_rate": round(attendance_rate, 2),
            "modules_enrolled": len(registrations)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@students_bp.route('/<string:student_id>/wellbeing_trends', methods=['GET'])
def get_wellbeing_trends(student_id):
    """
    Get wellbeing trend analysis for a student.
    
    Returns:
        JSON with stress, sleep, and social connection trends
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        registrations = ModuleRegistration.query.filter_by(student_id=student_id).all()
        registration_ids = [r.registration_id for r in registrations]
        
        # Get survey data
        surveys = WeeklySurvey.query.filter(
            WeeklySurvey.registration_id.in_(registration_ids)
        ).order_by(WeeklySurvey.week_number).all()
        
        # Calculate averages
        avg_stress = db.session.query(func.avg(WeeklySurvey.stress_level)).filter(
            WeeklySurvey.registration_id.in_(registration_ids)
        ).scalar() or 0
        
        avg_sleep = db.session.query(func.avg(WeeklySurvey.sleep_hours)).filter(
            WeeklySurvey.registration_id.in_(registration_ids)
        ).scalar() or 0
        
        avg_social = db.session.query(func.avg(WeeklySurvey.social_connection_score)).filter(
            WeeklySurvey.registration_id.in_(registration_ids)
        ).scalar() or 0
        
        # Weekly trends
        weekly_data = []
        for survey in surveys:
            weekly_data.append({
                "week": survey.week_number,
                "stress_level": survey.stress_level,
                "sleep_hours": float(survey.sleep_hours) if survey.sleep_hours else None,
                "social_connection_score": survey.social_connection_score
            })
        
        return jsonify({
            "student_id": student_id,
            "name": f"{student.first_name} {student.last_name}",
            "averages": {
                "stress_level": round(float(avg_stress), 2),
                "sleep_hours": round(float(avg_sleep), 2),
                "social_connection_score": round(float(avg_social), 2)
            },
            "weekly_trends": weekly_data,
            "total_surveys": len(surveys)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@students_bp.route('/<string:student_id>/full_profile', methods=['GET'])
def get_full_profile(student_id):
    """
    Get complete student profile with all data.
    
    Returns:
        JSON with student info, academic performance, and wellbeing data
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        # Get academic performance
        registrations = ModuleRegistration.query.filter_by(student_id=student_id).all()
        registration_ids = [r.registration_id for r in registrations]
        
        avg_grade = db.session.query(func.avg(Submission.grade_achieved)).filter(
            Submission.registration_id.in_(registration_ids)
        ).scalar() or 0
        
        # Get wellbeing averages
        avg_stress = db.session.query(func.avg(WeeklySurvey.stress_level)).filter(
            WeeklySurvey.registration_id.in_(registration_ids)
        ).scalar() or 0
        
        avg_sleep = db.session.query(func.avg(WeeklySurvey.sleep_hours)).filter(
            WeeklySurvey.registration_id.in_(registration_ids)
        ).scalar() or 0
        
        return jsonify({
            "student_info": {
                "student_id": student.student_id,
                "name": f"{student.first_name} {student.last_name}",
                "email": student.email,
                "enrolled_year": student.enrolled_year,
                "course_id": student.current_course_id
            },
            "academic_performance": {
                "average_grade": round(float(avg_grade), 2),
                "modules_enrolled": len(registrations)
            },
            "wellbeing_summary": {
                "average_stress": round(float(avg_stress), 2),
                "average_sleep": round(float(avg_sleep), 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
