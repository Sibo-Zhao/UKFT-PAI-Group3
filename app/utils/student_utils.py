"""
Student Utility Functions.

This module contains reusable utility functions for student-related operations
to reduce code duplication and improve maintainability.
"""
from app.models import Student, ModuleRegistration, db
from app.constants import ERROR_STUDENT_NOT_FOUND
import logging

logger = logging.getLogger(__name__)


def validate_student_exists(student_id):
    """
    Validate that a student exists in the database.
    
    Args:
        student_id (str): The unique identifier of the student.
    
    Returns:
        tuple: A tuple containing:
            - Student or None: Student object if found, None otherwise
            - dict or None: Error response dict if not found, None if found
            - int or None: HTTP status code if error, None if found
    
    Example:
        >>> student, error, status = validate_student_exists("S001")
        >>> if error:
        ...     return jsonify(error), status
        >>> # Continue with student object
    """
    student = db.session.get(Student, student_id)
    if not student:
        logger.warning(f"Student not found: {student_id}")
        return None, {"error": ERROR_STUDENT_NOT_FOUND}, 404
    return student, None, None


def get_student_registrations(student_id):
    """
    Get all module registrations for a student.
    
    Args:
        student_id (str): The unique identifier of the student.
    
    Returns:
        tuple: A tuple containing:
            - list[ModuleRegistration]: List of registrations
            - list[int]: List of registration IDs for easy querying
    
    Example:
        >>> registrations, registration_ids = get_student_registrations("S001")
        >>> if not registration_ids:
        ...     return jsonify({"message": "No registrations found"}), 200
    """
    registrations = ModuleRegistration.query.filter_by(student_id=student_id).all()
    registration_ids = [r.registration_id for r in registrations]
    return registrations, registration_ids


def calculate_attendance_rate(registration_ids):
    """
    Calculate attendance rate for given registrations.
    
    Args:
        registration_ids (list[int]): List of registration IDs.
    
    Returns:
        tuple: A tuple containing:
            - float: Attendance rate as percentage (0-100)
            - int: Total classes
            - int: Classes attended
    
    Example:
        >>> rate, total, attended = calculate_attendance_rate([1, 2, 3])
        >>> print(f"Attendance: {rate}% ({attended}/{total})")
    """
    from app.models import WeeklyAttendance
    from sqlalchemy import and_
    
    total_attendance = WeeklyAttendance.query.filter(
        WeeklyAttendance.registration_id.in_(registration_ids)
    ).count()
    
    if total_attendance == 0:
        return 0.0, 0, 0
    
    present_count = WeeklyAttendance.query.filter(
        and_(
            WeeklyAttendance.registration_id.in_(registration_ids),
            WeeklyAttendance.is_present == True
        )
    ).count()
    
    attendance_rate = (present_count / total_attendance) * 100
    return attendance_rate, total_attendance, present_count


def calculate_average_grade(registration_ids):
    """
    Calculate average grade for given registrations.
    
    Args:
        registration_ids (list[int]): List of registration IDs.
    
    Returns:
        tuple: A tuple containing:
            - float: Average grade (0.0 if no grades)
            - int: Total submissions
            - int: Graded submissions
    
    Example:
        >>> avg_grade, total, graded = calculate_average_grade([1, 2, 3])
        >>> print(f"Average grade: {avg_grade} ({graded}/{total} graded)")
    """
    from app.models import Submission
    from sqlalchemy import func
    
    submissions = Submission.query.filter(
        Submission.registration_id.in_(registration_ids)
    ).all()
    
    total_submissions = len(submissions)
    graded_submissions = [s for s in submissions if s.grade_achieved is not None]
    graded_count = len(graded_submissions)
    
    if graded_count == 0:
        return 0.0, total_submissions, 0
    
    avg_grade = sum(float(s.grade_achieved) for s in graded_submissions) / graded_count
    return avg_grade, total_submissions, graded_count


def format_student_name(student):
    """
    Format student's full name consistently.
    
    Args:
        student (Student): Student model instance.
    
    Returns:
        str: Formatted full name.
    
    Example:
        >>> name = format_student_name(student)
        >>> print(name)  # "John Doe"
    """
    return f"{student.first_name} {student.last_name}"


def build_student_summary(student, registrations, registration_ids):
    """
    Build a comprehensive student summary with common metrics.
    
    Args:
        student (Student): Student model instance.
        registrations (list[ModuleRegistration]): Student's registrations.
        registration_ids (list[int]): Registration IDs.
    
    Returns:
        dict: Student summary with basic info and metrics.
    
    Example:
        >>> summary = build_student_summary(student, registrations, registration_ids)
        >>> print(summary["attendance_rate"])
    """
    attendance_rate, total_classes, classes_attended = calculate_attendance_rate(registration_ids)
    avg_grade, total_submissions, graded_count = calculate_average_grade(registration_ids)
    
    return {
        "student_id": student.student_id,
        "student_name": format_student_name(student),
        "email": student.email,
        "course_id": student.current_course_id,
        "modules_enrolled": len(registrations),
        "attendance_rate": round(attendance_rate, 2),
        "total_classes": total_classes,
        "classes_attended": classes_attended,
        "average_grade": round(avg_grade, 2),
        "total_submissions": total_submissions,
        "graded_submissions": graded_count
    }