from flask import jsonify
from sqlalchemy import func, and_
from app.models import Student, ModuleRegistration, WeeklySurvey, WeeklyAttendance, Submission, Course, Module, Assignment, db
from app.views.schemas import student_schema, students_schema
from app.utils.error_handlers import handle_error, log_request_error
from app.utils.validators import StudentUpdateSchema, validate_request_data, validate_email
from app.constants import (
    ATTENDANCE_THRESHOLD_LOW, RISK_SCORE_HIGH_STRESS, RISK_SCORE_LOW_SLEEP,
    RISK_SCORE_LOW_SOCIAL, GRADE_THRESHOLD_FAILING, RISK_WEIGHT_ATTENDANCE,
    RISK_WEIGHT_HIGH_STRESS, RISK_WEIGHT_LOW_SLEEP, RISK_WEIGHT_LOW_SOCIAL,
    RISK_WEIGHT_FAILING_GRADES, ERROR_STUDENT_NOT_FOUND, ERROR_DUPLICATE_STUDENT_ID,
    ERROR_DUPLICATE_EMAIL, ERROR_MISSING_REQUIRED_FIELDS, SUCCESS_STUDENT_CREATED,
    SUCCESS_STUDENT_UPDATED, SUCCESS_STUDENT_DELETED
)
import logging

logger = logging.getLogger(__name__)

def get_all_students():
    """Get all students in the system."""
    try:
        logger.info("Fetching all students")
        students = Student.query.all()
        result = students_schema.dump(students)
        logger.info(f"Successfully retrieved {len(students)} students")
        return jsonify(result), 200
    except Exception as e:
        log_request_error("get_all_students", e)
        return handle_error(e, "in get_all_students")

def create_student(data):
    """
    Create a new student in the system.
    
    Validates required fields, checks for duplicate student ID and email,
    then creates a new student record in the database.
    
    Args:
        data (dict): Student information dictionary.
            Required keys:
                - student_id (str): Unique student identifier
                - first_name (str): Student's first name
                - last_name (str): Student's last name
                - email (str): Student's email address (must be unique)
                - enrolled_year (int): Year of enrollment
                - current_course_id (str): Course the student is enrolled in
            Optional keys:
                - contact_no (str): Student's contact number
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with created student data
            - int: HTTP status code
                - 201: Student created successfully
                - 400: Missing required fields or validation error
                - 409: Student ID or email already exists
    
    Raises:
        ValueError: If enrolled_year cannot be converted to integer.
        DatabaseError: If database operation fails.
    
    Example:
        >>> create_student({
        ...     "student_id": "S001",
        ...     "first_name": "John",
        ...     "last_name": "Doe",
        ...     "email": "john@example.com",
        ...     "enrolled_year": 2023,
        ...     "current_course_id": "C001"
        ... })
        (JSON_response, 201)
    """
    try:
        required = ["student_id", "first_name", "last_name",
                    "email", "enrolled_year", "current_course_id"]
        missing = [f for f in required if f not in data or data[f] in (None, "")]
        if missing:
            return jsonify({"error": ERROR_MISSING_REQUIRED_FIELDS.format(fields=', '.join(missing))}), 400

        if db.session.get(Student, data["student_id"]):
            return jsonify({"error": ERROR_DUPLICATE_STUDENT_ID}), 409

        if Student.query.filter_by(email=data["email"]).first():
            return jsonify({"error": ERROR_DUPLICATE_EMAIL}), 409

        student = Student(
            student_id=data["student_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            contact_no=data.get("contact_no"),
            enrolled_year=int(data["enrolled_year"])
            if data.get("enrolled_year") not in (None, "")
            else None,
            current_course_id=data["current_course_id"],
        )

        db.session.add(student)
        db.session.commit()

        result = student_schema.dump(student)
        return jsonify(result), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

def get_student(student_id):
    """Get detailed information for a specific student."""
    try:
        logger.info(f"Fetching student: {student_id}")
        student = db.session.get(Student, student_id)
        if not student:
            logger.warning(f"Student not found: {student_id}")
            return jsonify({"error": "Student not found"}), 404
        
        result = student_schema.dump(student)
        logger.info(f"Successfully retrieved student: {student_id}")
        return jsonify(result), 200
    except Exception as e:
        log_request_error("get_student", e, student_id=student_id)
        return handle_error(e, f"in get_student for student_id={student_id}")

def update_student(student_id, data):
    try:
        student = db.session.get(Student, student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404

        if 'email' in data:
            email = data['email']
            if email and '@' not in email:
                return jsonify({"error": "Invalid email format"}), 400

        allowed_fields = ['first_name', 'last_name', 'email', 'enrolled_year', 'current_course_id']
        for field in allowed_fields:
            if field in data:
                setattr(student, field, data[field])

        db.session.commit()

        result = student_schema.dump(student)
        return jsonify(result), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def get_at_risk_students():
    """
    Identify at-risk students based on multiple criteria.
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
                if attendance_rate < ATTENDANCE_THRESHOLD_LOW:
                    risk_factors.append("low_attendance")
                    risk_score += RISK_WEIGHT_ATTENDANCE
            
            # Check stress levels
            avg_stress = db.session.query(func.avg(WeeklySurvey.stress_level)).filter(
                WeeklySurvey.registration_id.in_(registration_ids)
            ).scalar()
            
            if avg_stress and avg_stress > RISK_SCORE_HIGH_STRESS:
                risk_factors.append("high_stress")
                risk_score += RISK_WEIGHT_HIGH_STRESS
            
            # Check sleep hours
            avg_sleep = db.session.query(func.avg(WeeklySurvey.sleep_hours)).filter(
                WeeklySurvey.registration_id.in_(registration_ids)
            ).scalar()
            
            if avg_sleep and avg_sleep < RISK_SCORE_LOW_SLEEP:
                risk_factors.append("low_sleep")
                risk_score += RISK_WEIGHT_LOW_SLEEP
            
            # Check social connection
            avg_social = db.session.query(func.avg(WeeklySurvey.social_connection_score)).filter(
                WeeklySurvey.registration_id.in_(registration_ids)
            ).scalar()
            
            if avg_social and avg_social < RISK_SCORE_LOW_SOCIAL:
                risk_factors.append("low_social_connection")
                risk_score += RISK_WEIGHT_LOW_SOCIAL
            
            # Check grades
            avg_grade = db.session.query(func.avg(Submission.grade_achieved)).filter(
                Submission.registration_id.in_(registration_ids)
            ).scalar()
            
            if avg_grade and avg_grade < GRADE_THRESHOLD_FAILING:
                risk_factors.append("failing_grades")
                risk_score += RISK_WEIGHT_FAILING_GRADES
            
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

def delete_student(student_id):
    try:
        student = db.session.get(Student, student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404

        registrations = ModuleRegistration.query.filter_by(student_id=student_id).all()
        registration_ids = [r.registration_id for r in registrations]

        WeeklySurvey.query.filter(
            WeeklySurvey.registration_id.in_(registration_ids)
        ).delete(synchronize_session=False)

        WeeklyAttendance.query.filter(
            WeeklyAttendance.registration_id.in_(registration_ids)
        ).delete(synchronize_session=False)

        Submission.query.filter(
            Submission.registration_id.in_(registration_ids)
        ).delete(synchronize_session=False)

        ModuleRegistration.query.filter_by(student_id=student_id).delete()

        db.session.delete(student)
        db.session.commit()

        return jsonify({
            "message": f"Student {student_id} and all related records deleted successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def get_academic_performance(student_id):
    """
    Get academic performance metrics for a student.
    """
    try:
        student = db.session.get(Student, student_id)
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

def get_wellbeing_trends(student_id):
    """
    Get wellbeing trend analysis for a student.
    """
    try:
        student = db.session.get(Student, student_id)
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

def get_full_profile(student_id):
    """
    Get complete student profile with all data.
    """
    try:
        student = db.session.get(Student, student_id)
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

def update_student(student_id, data):
    """
    Update student information.
    
    Args:
        student_id: Student identifier
        data: Dictionary with fields to update
        
    Returns:
        JSON response with updated student (200) or error (404/400)
    """
    try:
        logger.info(f"Updating student: {student_id}")
        student = db.session.get(Student, student_id)
        if not student:
            logger.warning(f"Student not found for update: {student_id}")
            return jsonify({"error": "Student not found"}), 404
        
        # Validate input data
        validated_data, errors = validate_request_data(StudentUpdateSchema, data)
        if errors:
            logger.warning(f"Student update validation failed for {student_id}: {errors}")
            return jsonify({"error": "Validation failed", "details": errors}), 400
        
        # Update allowed fields from validated data
        allowed_fields = ['first_name', 'last_name', 'email', 'enrolled_year', 'current_course_id']
        updated_fields = []
        for field in allowed_fields:
            if field in validated_data:
                setattr(student, field, validated_data[field])
                updated_fields.append(field)
        
        db.session.commit()
        logger.info(f"Successfully updated student {student_id}, fields: {', '.join(updated_fields)}")
        
        result = student_schema.dump(student)
        return jsonify(result), 200
        
    except Exception as e:
        db.session.rollback()
        log_request_error("update_student", e, student_id=student_id)
        return handle_error(e, f"in update_student for student_id={student_id}")

def delete_student(student_id):
    """
    Delete a student and all related records (cascade delete).
    
    Args:
        student_id: Student identifier
        
    Returns:
        JSON response with success message (200) or error (404)
    """
    try:
        logger.info(f"Attempting to delete student: {student_id}")
        student = db.session.get(Student, student_id)
        if not student:
            logger.warning(f"Student not found for deletion: {student_id}")
            return jsonify({"error": "Student not found"}), 404
        
        # Get all registrations for this student
        registrations = ModuleRegistration.query.filter_by(student_id=student_id).all()
        registration_ids = [r.registration_id for r in registrations]
        
        logger.info(f"Deleting {len(registrations)} registrations for student: {student_id}")
        
        # Delete related records (cascade delete)
        # 1. Delete weekly surveys
        surveys_deleted = WeeklySurvey.query.filter(
            WeeklySurvey.registration_id.in_(registration_ids)
        ).delete(synchronize_session=False)
        
        # 2. Delete weekly attendance
        attendance_deleted = WeeklyAttendance.query.filter(
            WeeklyAttendance.registration_id.in_(registration_ids)
        ).delete(synchronize_session=False)
        
        # 3. Delete submissions
        submissions_deleted = Submission.query.filter(
            Submission.registration_id.in_(registration_ids)
        ).delete(synchronize_session=False)
        
        # 4. Delete module registrations
        ModuleRegistration.query.filter_by(student_id=student_id).delete()
        
        # 5. Finally, delete the student
        db.session.delete(student)
        db.session.commit()
        
        logger.info(f"Successfully deleted student {student_id} and related records: "
                   f"{surveys_deleted} surveys, {attendance_deleted} attendance, "
                   f"{submissions_deleted} submissions")
        
        return jsonify({
            "message": f"Student {student_id} and all related records deleted successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_request_error("delete_student", e, student_id=student_id)
        return handle_error(e, f"in delete_student for student_id={student_id}")


def get_student_analytics(student_id, module_id=None, week_start=None, week_end=None, assignment_type=None):
    """
    Get comprehensive analytics for a student across their course modules.
    
    Provides aggregated data including:
    - Average weekly attendance rate
    - Average grades across assignments
    - Average submission time (days before/after due date)
    - Wellbeing trends (stress, sleep, social connection)
    - Performance trends over time
    
    Args:
        student_id (str): The unique identifier of the student
        module_id (str, optional): Filter by specific module
        week_start (int, optional): Start week for filtering
        week_end (int, optional): End week for filtering
        assignment_type (str, optional): Filter by assignment type (future enhancement)
        
    Returns:
        tuple: JSON response with comprehensive analytics and HTTP status code
    """
    try:
        logger.info(f"Generating analytics for student: {student_id}")
        
        # Validate student exists
        student = db.session.get(Student, student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        # Get student's course and modules
        course = db.session.get(Course, student.current_course_id) if student.current_course_id else None
        
        # Get all registrations for this student (optionally filtered by module)
        registrations_query = ModuleRegistration.query.filter_by(student_id=student_id)
        if module_id:
            registrations_query = registrations_query.filter_by(module_id=module_id)
        
        registrations = registrations_query.all()
        registration_ids = [r.registration_id for r in registrations]
        
        if not registration_ids:
            return jsonify({
                "student_id": student_id,
                "student_name": f"{student.first_name} {student.last_name}",
                "course_id": student.current_course_id,
                "course_name": course.course_name if course else None,
                "message": "No module registrations found",
                "analytics": {}
            }), 200
        
        # Build week filter for attendance and surveys
        attendance_query = WeeklyAttendance.query.filter(
            WeeklyAttendance.registration_id.in_(registration_ids)
        )
        survey_query = WeeklySurvey.query.filter(
            WeeklySurvey.registration_id.in_(registration_ids)
        )
        
        if week_start:
            attendance_query = attendance_query.filter(WeeklyAttendance.week_number >= week_start)
            survey_query = survey_query.filter(WeeklySurvey.week_number >= week_start)
        if week_end:
            attendance_query = attendance_query.filter(WeeklyAttendance.week_number <= week_end)
            survey_query = survey_query.filter(WeeklySurvey.week_number <= week_end)
        
        # 1. ATTENDANCE ANALYTICS
        attendance_records = attendance_query.all()
        total_classes = len(attendance_records)
        classes_attended = sum(1 for record in attendance_records if record.is_present)
        avg_attendance_rate = (classes_attended / total_classes * 100) if total_classes > 0 else 0.0
        
        # Weekly attendance breakdown
        weekly_attendance = {}
        for record in attendance_records:
            week = record.week_number
            if week not in weekly_attendance:
                weekly_attendance[week] = {"total": 0, "present": 0}
            weekly_attendance[week]["total"] += 1
            if record.is_present:
                weekly_attendance[week]["present"] += 1
        
        attendance_trends = []
        for week in sorted(weekly_attendance.keys()):
            stats = weekly_attendance[week]
            rate = (stats["present"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
            attendance_trends.append({
                "week": week,
                "attendance_rate": round(rate, 2),
                "classes_attended": stats["present"],
                "total_classes": stats["total"]
            })
        
        # 2. GRADES ANALYTICS
        submissions = Submission.query.filter(
            Submission.registration_id.in_(registration_ids)
        ).all()
        
        graded_submissions = [s for s in submissions if s.grade_achieved is not None]
        total_submissions = len(submissions)
        graded_count = len(graded_submissions)
        
        if graded_count > 0:
            grades = [float(s.grade_achieved) for s in graded_submissions]
            avg_grade = sum(grades) / len(grades)
            min_grade = min(grades)
            max_grade = max(grades)
        else:
            avg_grade = min_grade = max_grade = 0.0
        
        # 3. SUBMISSION TIMING ANALYTICS
        submission_timing_data = []
        total_days_early = 0
        total_days_late = 0
        on_time_count = 0
        late_count = 0
        early_count = 0
        
        for submission in submissions:
            if submission.submitted_at:
                assignment = db.session.get(Assignment, submission.assignment_id)
                if assignment and assignment.due_date:
                    days_diff = (submission.submitted_at.date() - assignment.due_date.date()).days
                    
                    if days_diff < 0:  # Early submission
                        early_count += 1
                        total_days_early += abs(days_diff)
                    elif days_diff > 0:  # Late submission
                        late_count += 1
                        total_days_late += days_diff
                    else:  # On time
                        on_time_count += 1
                    
                    submission_timing_data.append({
                        "assignment_id": assignment.assignment_id,
                        "assignment_title": assignment.title,
                        "days_difference": days_diff,
                        "status": "early" if days_diff < 0 else "late" if days_diff > 0 else "on_time"
                    })
        
        avg_days_early = (total_days_early / early_count) if early_count > 0 else 0.0
        avg_days_late = (total_days_late / late_count) if late_count > 0 else 0.0
        
        # 4. WELLBEING ANALYTICS
        survey_records = survey_query.all()
        
        if survey_records:
            stress_levels = [s.stress_level for s in survey_records if s.stress_level is not None]
            sleep_hours = [s.sleep_hours for s in survey_records if s.sleep_hours is not None]
            social_scores = [s.social_connection_score for s in survey_records if s.social_connection_score is not None]
            
            avg_stress = sum(stress_levels) / len(stress_levels) if stress_levels else 0.0
            avg_sleep = sum(sleep_hours) / len(sleep_hours) if sleep_hours else 0.0
            avg_social = sum(social_scores) / len(social_scores) if social_scores else 0.0
        else:
            avg_stress = avg_sleep = avg_social = 0.0
        
        # Weekly wellbeing trends
        weekly_wellbeing = {}
        for survey in survey_records:
            week = survey.week_number
            if week not in weekly_wellbeing:
                weekly_wellbeing[week] = {
                    "stress_levels": [], "sleep_hours": [], "social_scores": []
                }
            
            if survey.stress_level is not None:
                weekly_wellbeing[week]["stress_levels"].append(survey.stress_level)
            if survey.sleep_hours is not None:
                weekly_wellbeing[week]["sleep_hours"].append(survey.sleep_hours)
            if survey.social_connection_score is not None:
                weekly_wellbeing[week]["social_scores"].append(survey.social_connection_score)
        
        wellbeing_trends = []
        for week in sorted(weekly_wellbeing.keys()):
            data = weekly_wellbeing[week]
            wellbeing_trends.append({
                "week": week,
                "avg_stress": round(sum(data["stress_levels"]) / len(data["stress_levels"]), 2) if data["stress_levels"] else None,
                "avg_sleep": round(sum(data["sleep_hours"]) / len(data["sleep_hours"]), 2) if data["sleep_hours"] else None,
                "avg_social": round(sum(data["social_scores"]) / len(data["social_scores"]), 2) if data["social_scores"] else None
            })
        
        # 5. MODULE BREAKDOWN
        module_breakdown = []
        for registration in registrations:
            module = db.session.get(Module, registration.module_id)
            
            # Module-specific attendance
            module_attendance = WeeklyAttendance.query.filter_by(
                registration_id=registration.registration_id
            )
            if week_start:
                module_attendance = module_attendance.filter(WeeklyAttendance.week_number >= week_start)
            if week_end:
                module_attendance = module_attendance.filter(WeeklyAttendance.week_number <= week_end)
            
            module_attendance_records = module_attendance.all()
            module_total_classes = len(module_attendance_records)
            module_attended = sum(1 for r in module_attendance_records if r.is_present)
            module_attendance_rate = (module_attended / module_total_classes * 100) if module_total_classes > 0 else 0.0
            
            # Module-specific grades
            module_submissions = Submission.query.filter_by(
                registration_id=registration.registration_id
            ).all()
            module_graded = [s for s in module_submissions if s.grade_achieved is not None]
            module_avg_grade = sum(float(s.grade_achieved) for s in module_graded) / len(module_graded) if module_graded else 0.0
            
            module_breakdown.append({
                "module_id": module.module_id if module else registration.module_id,
                "module_name": module.module_name if module else "Unknown",
                "registration_status": registration.status,
                "attendance_rate": round(module_attendance_rate, 2),
                "total_classes": module_total_classes,
                "classes_attended": module_attended,
                "average_grade": round(module_avg_grade, 2),
                "total_submissions": len(module_submissions),
                "graded_submissions": len(module_graded)
            })
        
        # Compile final response
        analytics = {
            "attendance": {
                "overall_rate": round(avg_attendance_rate, 2),
                "total_classes": total_classes,
                "classes_attended": classes_attended,
                "weekly_trends": attendance_trends
            },
            "academic_performance": {
                "average_grade": round(avg_grade, 2),
                "minimum_grade": round(min_grade, 2),
                "maximum_grade": round(max_grade, 2),
                "total_submissions": total_submissions,
                "graded_submissions": graded_count,
                "grading_completion_rate": round((graded_count / total_submissions * 100) if total_submissions > 0 else 0.0, 2)
            },
            "submission_timing": {
                "average_days_early": round(avg_days_early, 2),
                "average_days_late": round(avg_days_late, 2),
                "on_time_submissions": on_time_count,
                "early_submissions": early_count,
                "late_submissions": late_count,
                "punctuality_rate": round((on_time_count + early_count) / total_submissions * 100 if total_submissions > 0 else 0.0, 2)
            },
            "wellbeing": {
                "average_stress_level": round(avg_stress, 2),
                "average_sleep_hours": round(avg_sleep, 2),
                "average_social_connection": round(avg_social, 2),
                "total_surveys": len(survey_records),
                "weekly_trends": wellbeing_trends
            },
            "module_breakdown": module_breakdown
        }
        
        logger.info(f"Successfully generated analytics for student: {student_id}")
        return jsonify({
            "student_id": student_id,
            "student_name": f"{student.first_name} {student.last_name}",
            "course_id": student.current_course_id,
            "course_name": course.course_name if course else None,
            "filters_applied": {
                "module_id": module_id,
                "week_start": week_start,
                "week_end": week_end
            },
            "analytics": analytics
        }), 200
        
    except Exception as e:
        log_request_error("get_student_analytics", e, student_id=student_id)
        return handle_error(e, f"in get_student_analytics for student_id={student_id}")


def get_course_student_comparison(course_id, metric="attendance", week_start=None, week_end=None):
    """
    Compare all students in a course across specified metrics.
    
    Args:
        course_id (str): The unique identifier of the course
        metric (str): Metric to compare (attendance, grades, wellbeing, submissions)
        week_start (int, optional): Start week for filtering
        week_end (int, optional): End week for filtering
        
    Returns:
        tuple: JSON response with student comparison data and HTTP status code
    """
    try:
        logger.info(f"Generating course comparison for course: {course_id}, metric: {metric}")
        
        # Validate course exists
        course = db.session.get(Course, course_id)
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        # Get all students in this course
        students = Student.query.filter_by(current_course_id=course_id).all()
        
        if not students:
            return jsonify({
                "course_id": course_id,
                "course_name": course.course_name,
                "message": "No students found in this course",
                "comparison": []
            }), 200
        
        comparison_data = []
        
        for student in students:
            # Get student's registrations
            registrations = ModuleRegistration.query.filter_by(student_id=student.student_id).all()
            registration_ids = [r.registration_id for r in registrations]
            
            if not registration_ids:
                continue
            
            student_data = {
                "student_id": student.student_id,
                "student_name": f"{student.first_name} {student.last_name}",
                "email": student.email
            }
            
            if metric in ["attendance", "all"]:
                # Attendance metrics
                attendance_query = WeeklyAttendance.query.filter(
                    WeeklyAttendance.registration_id.in_(registration_ids)
                )
                if week_start:
                    attendance_query = attendance_query.filter(WeeklyAttendance.week_number >= week_start)
                if week_end:
                    attendance_query = attendance_query.filter(WeeklyAttendance.week_number <= week_end)
                
                attendance_records = attendance_query.all()
                total_classes = len(attendance_records)
                classes_attended = sum(1 for r in attendance_records if r.is_present)
                attendance_rate = (classes_attended / total_classes * 100) if total_classes > 0 else 0.0
                
                student_data["attendance_rate"] = round(attendance_rate, 2)
                student_data["total_classes"] = total_classes
                student_data["classes_attended"] = classes_attended
            
            if metric in ["grades", "all"]:
                # Grade metrics
                submissions = Submission.query.filter(
                    Submission.registration_id.in_(registration_ids)
                ).all()
                graded_submissions = [s for s in submissions if s.grade_achieved is not None]
                
                if graded_submissions:
                    avg_grade = sum(float(s.grade_achieved) for s in graded_submissions) / len(graded_submissions)
                    student_data["average_grade"] = round(avg_grade, 2)
                else:
                    student_data["average_grade"] = 0.0
                
                student_data["total_submissions"] = len(submissions)
                student_data["graded_submissions"] = len(graded_submissions)
            
            if metric in ["wellbeing", "all"]:
                # Wellbeing metrics
                survey_query = WeeklySurvey.query.filter(
                    WeeklySurvey.registration_id.in_(registration_ids)
                )
                if week_start:
                    survey_query = survey_query.filter(WeeklySurvey.week_number >= week_start)
                if week_end:
                    survey_query = survey_query.filter(WeeklySurvey.week_number <= week_end)
                
                surveys = survey_query.all()
                
                if surveys:
                    stress_levels = [s.stress_level for s in surveys if s.stress_level is not None]
                    sleep_hours = [s.sleep_hours for s in surveys if s.sleep_hours is not None]
                    social_scores = [s.social_connection_score for s in surveys if s.social_connection_score is not None]
                    
                    student_data["avg_stress_level"] = round(sum(stress_levels) / len(stress_levels), 2) if stress_levels else 0.0
                    student_data["avg_sleep_hours"] = round(sum(sleep_hours) / len(sleep_hours), 2) if sleep_hours else 0.0
                    student_data["avg_social_connection"] = round(sum(social_scores) / len(social_scores), 2) if social_scores else 0.0
                else:
                    student_data["avg_stress_level"] = 0.0
                    student_data["avg_sleep_hours"] = 0.0
                    student_data["avg_social_connection"] = 0.0
                
                student_data["total_surveys"] = len(surveys)
            
            comparison_data.append(student_data)
        
        # Sort by the primary metric
        if metric == "attendance":
            comparison_data.sort(key=lambda x: x.get("attendance_rate", 0), reverse=True)
        elif metric == "grades":
            comparison_data.sort(key=lambda x: x.get("average_grade", 0), reverse=True)
        elif metric == "wellbeing":
            comparison_data.sort(key=lambda x: x.get("avg_stress_level", 0))  # Lower stress is better
        
        logger.info(f"Successfully generated comparison for {len(comparison_data)} students in course: {course_id}")
        return jsonify({
            "course_id": course_id,
            "course_name": course.course_name,
            "comparison_metric": metric,
            "filters_applied": {
                "week_start": week_start,
                "week_end": week_end
            },
            "total_students": len(comparison_data),
            "students": comparison_data
        }), 200
        
    except Exception as e:
        log_request_error("get_course_student_comparison", e, course_id=course_id)
        return handle_error(e, f"in get_course_student_comparison for course_id={course_id}")
