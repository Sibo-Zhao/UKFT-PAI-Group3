"""
Attendance Controller Module.

This module handles operations related to weekly attendance tracking including
recording attendance, retrieving attendance data, and generating attendance reports.
"""
from flask import jsonify
from sqlalchemy import func, and_
from app.models import WeeklyAttendance, ModuleRegistration, Student, Module, db
from app.utils.error_handlers import handle_error, log_request_error
from app.constants import (
    ERROR_STUDENT_NOT_FOUND, ERROR_MODULE_NOT_FOUND, ERROR_REGISTRATION_NOT_FOUND,
    ERROR_INVALID_DATE_FORMAT, SUCCESS_ATTENDANCE_RECORDED, DATE_FORMAT
)
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)


def record_attendance(data):
    """
    Record attendance for a student in a specific week.
    
    Args:
        data (dict): Attendance data including registration_id, week_number, 
                    class_date, is_present, reason_absent
        
    Returns:
        tuple: JSON response with attendance record and HTTP status code
    """
    try:
        logger.info(f"Recording attendance for registration: {data.get('registration_id')}")
        
        # Validate required fields
        required_fields = ['registration_id', 'week_number', 'class_date', 'is_present']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Validate registration exists
        registration = db.session.get(ModuleRegistration, data['registration_id'])
        if not registration:
            return jsonify({"error": ERROR_REGISTRATION_NOT_FOUND}), 404
        
        # Check if attendance already recorded for this week
        existing_attendance = WeeklyAttendance.query.filter_by(
            registration_id=data['registration_id'],
            week_number=data['week_number']
        ).first()
        
        if existing_attendance:
            return jsonify({"error": "Attendance already recorded for this week"}), 409
        
        # Parse class_date
        try:
            class_date = datetime.strptime(data['class_date'], DATE_FORMAT).date()
        except ValueError:
            return jsonify({"error": ERROR_INVALID_DATE_FORMAT}), 400
        
        # Create attendance record
        attendance = WeeklyAttendance(
            registration_id=data['registration_id'],
            week_number=data['week_number'],
            class_date=class_date,
            is_present=bool(data['is_present']),
            reason_absent=data.get('reason_absent') if not data['is_present'] else None
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        logger.info(f"Successfully recorded attendance for registration: {data['registration_id']}")
        return jsonify({
            "message": SUCCESS_ATTENDANCE_RECORDED,
            "attendance_id": attendance.attendance_id,
            "registration_id": attendance.registration_id,
            "week_number": attendance.week_number,
            "is_present": attendance.is_present
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_request_error("record_attendance", e)
        return handle_error(e, "in record_attendance")


def get_student_attendance(student_id):
    """
    Get attendance records for a specific student across all modules.
    
    Args:
        student_id (str): The unique identifier of the student
        
    Returns:
        tuple: JSON response with attendance data and HTTP status code
    """
    try:
        logger.info(f"Fetching attendance for student: {student_id}")
        
        # Validate student exists
        student = db.session.get(Student, student_id)
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        # Get all registrations for this student
        registrations = ModuleRegistration.query.filter_by(student_id=student_id).all()
        registration_ids = [r.registration_id for r in registrations]
        
        if not registration_ids:
            return jsonify({
                "student_id": student_id,
                "student_name": f"{student.first_name} {student.last_name}",
                "attendance_records": [],
                "summary": {
                    "total_classes": 0,
                    "classes_attended": 0,
                    "attendance_rate": 0.0
                }
            }), 200
        
        # Get attendance records
        attendance_records = WeeklyAttendance.query.filter(
            WeeklyAttendance.registration_id.in_(registration_ids)
        ).order_by(WeeklyAttendance.class_date).all()
        
        # Build response with module information
        result = []
        for record in attendance_records:
            registration = db.session.get(ModuleRegistration, record.registration_id)
            module = db.session.get(Module, registration.module_id) if registration else None
            
            result.append({
                "attendance_id": record.attendance_id,
                "week_number": record.week_number,
                "class_date": record.class_date.isoformat(),
                "is_present": record.is_present,
                "reason_absent": record.reason_absent,
                "module_id": module.module_id if module else None,
                "module_name": module.module_name if module else None
            })
        
        # Calculate summary statistics
        total_classes = len(attendance_records)
        classes_attended = sum(1 for record in attendance_records if record.is_present)
        attendance_rate = (classes_attended / total_classes * 100) if total_classes > 0 else 0.0
        
        logger.info(f"Successfully retrieved {total_classes} attendance records for student: {student_id}")
        return jsonify({
            "student_id": student_id,
            "student_name": f"{student.first_name} {student.last_name}",
            "attendance_records": result,
            "summary": {
                "total_classes": total_classes,
                "classes_attended": classes_attended,
                "attendance_rate": round(attendance_rate, 2)
            }
        }), 200
        
    except Exception as e:
        log_request_error("get_student_attendance", e, student_id=student_id)
        return handle_error(e, f"in get_student_attendance for student_id={student_id}")


def get_module_attendance(module_id):
    """
    Get attendance summary for all students in a specific module.
    
    Args:
        module_id (str): The unique identifier of the module
        
    Returns:
        tuple: JSON response with module attendance data and HTTP status code
    """
    try:
        logger.info(f"Fetching attendance for module: {module_id}")
        
        # Validate module exists
        module = db.session.get(Module, module_id)
        if not module:
            return jsonify({"error": "Module not found"}), 404
        
        # Get all registrations for this module
        registrations = ModuleRegistration.query.filter_by(module_id=module_id).all()
        
        result = []
        for registration in registrations:
            student = db.session.get(Student, registration.student_id)
            
            # Get attendance for this registration
            attendance_records = WeeklyAttendance.query.filter_by(
                registration_id=registration.registration_id
            ).all()
            
            total_classes = len(attendance_records)
            classes_attended = sum(1 for record in attendance_records if record.is_present)
            attendance_rate = (classes_attended / total_classes * 100) if total_classes > 0 else 0.0
            
            result.append({
                "student_id": registration.student_id,
                "student_name": f"{student.first_name} {student.last_name}" if student else "Unknown",
                "registration_status": registration.status,
                "total_classes": total_classes,
                "classes_attended": classes_attended,
                "attendance_rate": round(attendance_rate, 2)
            })
        
        # Calculate module-wide statistics
        total_students = len(result)
        avg_attendance_rate = sum(s['attendance_rate'] for s in result) / total_students if total_students > 0 else 0.0
        
        logger.info(f"Successfully retrieved attendance data for {total_students} students in module: {module_id}")
        return jsonify({
            "module_id": module_id,
            "module_name": module.module_name,
            "student_attendance": result,
            "summary": {
                "total_students": total_students,
                "average_attendance_rate": round(avg_attendance_rate, 2)
            }
        }), 200
        
    except Exception as e:
        log_request_error("get_module_attendance", e, module_id=module_id)
        return handle_error(e, f"in get_module_attendance for module_id={module_id}")


def update_attendance(attendance_id, data):
    """
    Update an existing attendance record.
    
    Args:
        attendance_id (int): The unique identifier of the attendance record
        data (dict): Updated attendance data
        
    Returns:
        tuple: JSON response with updated attendance and HTTP status code
    """
    try:
        logger.info(f"Updating attendance record: {attendance_id}")
        
        attendance = db.session.get(WeeklyAttendance, attendance_id)
        if not attendance:
            return jsonify({"error": "Attendance record not found"}), 404
        
        # Update allowed fields
        if 'is_present' in data:
            attendance.is_present = bool(data['is_present'])
            # Clear reason_absent if marking as present
            if attendance.is_present:
                attendance.reason_absent = None
        
        if 'reason_absent' in data and not attendance.is_present:
            attendance.reason_absent = data['reason_absent']
        
        if 'class_date' in data:
            try:
                attendance.class_date = datetime.strptime(data['class_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        db.session.commit()
        
        logger.info(f"Successfully updated attendance record: {attendance_id}")
        return jsonify({
            "message": "Attendance updated successfully",
            "attendance_id": attendance.attendance_id,
            "is_present": attendance.is_present,
            "reason_absent": attendance.reason_absent
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_request_error("update_attendance", e, attendance_id=attendance_id)
        return handle_error(e, f"in update_attendance for attendance_id={attendance_id}")


def delete_attendance(attendance_id):
    """
    Delete an attendance record.
    
    Args:
        attendance_id (int): The unique identifier of the attendance record
        
    Returns:
        tuple: JSON response with success message and HTTP status code
    """
    try:
        logger.info(f"Deleting attendance record: {attendance_id}")
        
        attendance = db.session.get(WeeklyAttendance, attendance_id)
        if not attendance:
            return jsonify({"error": "Attendance record not found"}), 404
        
        db.session.delete(attendance)
        db.session.commit()
        
        logger.info(f"Successfully deleted attendance record: {attendance_id}")
        return jsonify({"message": f"Attendance record {attendance_id} deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        log_request_error("delete_attendance", e, attendance_id=attendance_id)
        return handle_error(e, f"in delete_attendance for attendance_id={attendance_id}")


def get_attendance_report(start_date=None, end_date=None):
    """
    Generate attendance report for a date range.
    
    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
        
    Returns:
        tuple: JSON response with attendance report and HTTP status code
    """
    try:
        logger.info(f"Generating attendance report from {start_date} to {end_date}")
        
        query = WeeklyAttendance.query
        
        # Apply date filters if provided
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(WeeklyAttendance.class_date >= start_date_obj)
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400
        
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(WeeklyAttendance.class_date <= end_date_obj)
            except ValueError:
                return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400
        
        attendance_records = query.all()
        
        # Calculate statistics
        total_records = len(attendance_records)
        present_count = sum(1 for record in attendance_records if record.is_present)
        absent_count = total_records - present_count
        overall_attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0.0
        
        # Group by week for trends
        weekly_stats = {}
        for record in attendance_records:
            week = record.week_number
            if week not in weekly_stats:
                weekly_stats[week] = {"total": 0, "present": 0}
            weekly_stats[week]["total"] += 1
            if record.is_present:
                weekly_stats[week]["present"] += 1
        
        weekly_trends = []
        for week, stats in sorted(weekly_stats.items()):
            rate = (stats["present"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
            weekly_trends.append({
                "week_number": week,
                "attendance_rate": round(rate, 2),
                "total_classes": stats["total"]
            })
        
        logger.info(f"Successfully generated attendance report with {total_records} records")
        return jsonify({
            "report_period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "summary": {
                "total_records": total_records,
                "present_count": present_count,
                "absent_count": absent_count,
                "overall_attendance_rate": round(overall_attendance_rate, 2)
            },
            "weekly_trends": weekly_trends
        }), 200
        
    except Exception as e:
        log_request_error("get_attendance_report", e)
        return handle_error(e, "in get_attendance_report")