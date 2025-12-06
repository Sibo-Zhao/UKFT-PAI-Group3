"""
Academic Controller Module.

This module handles academic-related operations including attendance tracking,
grade management, and submission records.
"""
from flask import jsonify
from app.models import WeeklyAttendance, Submission, ModuleRegistration, Assignment, Student, db
from app.views.schemas import attendances_schema, submissions_schema, assignment_schema, attendance_schema, submission_schema, students_schema
from app.utils.error_handlers import handle_error, log_request_error
from datetime import datetime
import csv
import io
import logging

logger = logging.getLogger(__name__)


def upload_csv_attendance(csv_file):
    """
    Upload attendance records from CSV file.
    
    Accepts a CSV file with attendance data and creates attendance entries.
    Uses registration_id directly for efficiency.
    
    Args:
        csv_file: File object from Flask request.files
    
    Returns:
        tuple: JSON response with upload summary and HTTP status code
    
    CSV Format:
        registration_id,week,is_present,reason_absent
        1,1,true,
        2,1,false,Sick
    """
    try:
        logger.info("Starting CSV attendance upload")
        
        if not csv_file:
            logger.warning("No CSV file provided")
            return jsonify({"error": "No CSV file provided"}), 400
        
        # Read CSV file
        csv_data = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        # Validate CSV headers
        required_headers = {'registration_id', 'week', 'is_present'}
        
        if not required_headers.issubset(set(csv_reader.fieldnames or [])):
            logger.error(f"Invalid CSV headers. Expected: {required_headers}")
            return jsonify({
                "error": "Invalid CSV format",
                "required_headers": list(required_headers),
                "received_headers": csv_reader.fieldnames
            }), 400
        
        processed_count = 0
        created_count = 0
        skipped_count = 0
        registrations_not_found = []
        invalid_rows = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            try:
                processed_count += 1
                
                registration_id = int(row['registration_id'].strip())
                week = int(row['week'].strip())
                is_present_str = row['is_present'].strip().lower()
                reason_absent = row.get('reason_absent', '').strip() or None
                
                # Parse boolean
                if is_present_str in ['true', '1', 'yes', 'present']:
                    is_present = True
                elif is_present_str in ['false', '0', 'no', 'absent']:
                    is_present = False
                else:
                    invalid_rows.append(f"Row {row_num}: Invalid is_present value '{is_present_str}'")
                    skipped_count += 1
                    continue
                
                # Validate registration exists
                registration = db.session.get(ModuleRegistration, registration_id)
                
                if not registration:
                    registrations_not_found.append(f"Registration ID {registration_id}")
                    skipped_count += 1
                    continue
                
                # Check if attendance already exists for this week
                existing = WeeklyAttendance.query.filter_by(
                    registration_id=registration_id,
                    week_number=week
                ).first()
                
                if existing:
                    # Update existing record
                    existing.is_present = is_present
                    existing.reason_absent = reason_absent
                    existing.class_date = datetime.now().date()
                else:
                    # Create new attendance record
                    attendance = WeeklyAttendance(
                        registration_id=registration_id,
                        week_number=week,
                        class_date=datetime.now().date(),
                        is_present=is_present,
                        reason_absent=reason_absent
                    )
                    db.session.add(attendance)
                
                created_count += 1
                
            except ValueError as e:
                invalid_rows.append(f"Row {row_num}: {str(e)}")
                skipped_count += 1
                continue
            except Exception as e:
                logger.error(f"Error processing row {row_num}: {str(e)}")
                invalid_rows.append(f"Row {row_num}: {str(e)}")
                skipped_count += 1
                continue
        
        db.session.commit()
        
        logger.info(f"CSV upload completed: {created_count} created/updated, {skipped_count} skipped")
        
        return jsonify({
            "message": "CSV upload completed",
            "processed": processed_count,
            "created": created_count,
            "skipped": skipped_count,
            "details": {
                "registrations_not_found": registrations_not_found,
                "total_not_found": len(registrations_not_found),
                "invalid_rows": invalid_rows,
                "total_invalid": len(invalid_rows)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"CSV upload failed: {str(e)}")
        return handle_error(e, "in upload_csv_attendance")

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

def upload_csv_grades(csv_file):
    """
    Upload grades from CSV file.
    
    Accepts a CSV file with grade data and updates/creates submission grades.
    Uses registration_id directly for efficiency.
    
    Args:
        csv_file: File object from Flask request.files
    
    Returns:
        tuple: JSON response with upload summary and HTTP status code
    
    CSV Format:
        registration_id,assignment_id,grade
        1,A001,85
        2,A002,92
    """
    try:
        logger.info("Starting CSV grades upload")
        
        if not csv_file:
            logger.warning("No CSV file provided")
            return jsonify({"error": "No CSV file provided"}), 400
        
        # Read CSV file
        csv_data = csv_file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        
        # Validate CSV headers
        required_headers = {'registration_id', 'assignment_id', 'grade'}
        
        if not required_headers.issubset(set(csv_reader.fieldnames or [])):
            logger.error(f"Invalid CSV headers. Expected: {required_headers}")
            return jsonify({
                "error": "Invalid CSV format",
                "required_headers": list(required_headers),
                "received_headers": csv_reader.fieldnames
            }), 400
        
        processed_count = 0
        updated_count = 0
        skipped_count = 0
        registrations_not_found = []
        invalid_rows = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            try:
                processed_count += 1
                
                registration_id = int(row['registration_id'].strip())
                assignment_id = row['assignment_id'].strip()
                grade_str = row['grade'].strip()
                
                # Parse grade
                try:
                    grade = float(grade_str)
                    if grade < 0:
                        invalid_rows.append(f"Row {row_num}: Grade cannot be negative")
                        skipped_count += 1
                        continue
                except ValueError:
                    invalid_rows.append(f"Row {row_num}: Invalid grade value '{grade_str}'")
                    skipped_count += 1
                    continue
                
                # Validate assignment exists
                assignment = db.session.get(Assignment, assignment_id)
                if not assignment:
                    invalid_rows.append(f"Row {row_num}: Assignment {assignment_id} not found")
                    skipped_count += 1
                    continue
                
                # Check max score
                if grade > assignment.max_score:
                    invalid_rows.append(f"Row {row_num}: Grade {grade} exceeds max score {assignment.max_score}")
                    skipped_count += 1
                    continue
                
                # Validate registration exists
                registration = db.session.get(ModuleRegistration, registration_id)
                if not registration:
                    registrations_not_found.append(f"Registration ID {registration_id}")
                    skipped_count += 1
                    continue
                
                # Verify registration is for the correct module
                if registration.module_id != assignment.module_id:
                    invalid_rows.append(f"Row {row_num}: Registration {registration_id} is not enrolled in module {assignment.module_id}")
                    skipped_count += 1
                    continue
                
                # Find or create submission
                submission = Submission.query.filter_by(
                    registration_id=registration_id,
                    assignment_id=assignment_id
                ).first()
                
                if submission:
                    # Update existing submission
                    submission.grade_achieved = grade
                else:
                    # Create new submission with grade
                    submission = Submission(
                        registration_id=registration_id,
                        assignment_id=assignment_id,
                        submitted_at=datetime.now(),
                        grade_achieved=grade
                    )
                    db.session.add(submission)
                
                updated_count += 1
                
            except ValueError as e:
                invalid_rows.append(f"Row {row_num}: {str(e)}")
                skipped_count += 1
                continue
            except Exception as e:
                logger.error(f"Error processing row {row_num}: {str(e)}")
                invalid_rows.append(f"Row {row_num}: {str(e)}")
                skipped_count += 1
                continue
        
        db.session.commit()
        
        logger.info(f"CSV upload completed: {updated_count} updated/created, {skipped_count} skipped")
        
        return jsonify({
            "message": "CSV upload completed",
            "processed": processed_count,
            "updated": updated_count,
            "skipped": skipped_count,
            "details": {
                "registrations_not_found": registrations_not_found,
                "total_not_found": len(registrations_not_found),
                "invalid_rows": invalid_rows,
                "total_invalid": len(invalid_rows)
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"CSV upload failed: {str(e)}")
        return handle_error(e, "in upload_csv_grades")

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
