"""
Submission Controller Module.

This module handles operations related to assignment submissions including
creating submissions, grading, and retrieving submission data.
"""
from flask import jsonify
from sqlalchemy import func, and_
from app.models import Submission, Assignment, ModuleRegistration, Student, Module, db
from app.utils.error_handlers import handle_error, log_request_error
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_submission(data):
    """
    Create a new assignment submission.
    
    Args:
        data (dict): Submission data including registration_id, assignment_id, submitted_at
        
    Returns:
        tuple: JSON response with submission record and HTTP status code
    """
    try:
        logger.info(f"Creating submission for assignment: {data.get('assignment_id')}")
        
        # Validate required fields
        required_fields = ['registration_id', 'assignment_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Validate registration exists
        registration = db.session.get(ModuleRegistration, data['registration_id'])
        if not registration:
            return jsonify({"error": "Registration not found"}), 404
        
        # Validate assignment exists
        assignment = db.session.get(Assignment, data['assignment_id'])
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404
        
        # Check if submission already exists
        existing_submission = Submission.query.filter_by(
            registration_id=data['registration_id'],
            assignment_id=data['assignment_id']
        ).first()
        
        if existing_submission:
            return jsonify({"error": "Submission already exists for this assignment"}), 409
        
        # Parse submitted_at if provided
        submitted_at = None
        if data.get('submitted_at'):
            try:
                submitted_at = datetime.fromisoformat(data['submitted_at'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid submitted_at format. Use ISO format"}), 400
        else:
            submitted_at = datetime.utcnow()
        
        # Create submission
        submission = Submission(
            registration_id=data['registration_id'],
            assignment_id=data['assignment_id'],
            submitted_at=submitted_at,
            grade_achieved=data.get('grade_achieved'),
            grader_feedback=data.get('grader_feedback')
        )
        
        db.session.add(submission)
        db.session.commit()
        
        logger.info(f"Successfully created submission: {submission.submission_id}")
        return jsonify({
            "message": "Submission created successfully",
            "submission_id": submission.submission_id,
            "registration_id": submission.registration_id,
            "assignment_id": submission.assignment_id,
            "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_request_error("create_submission", e)
        return handle_error(e, "in create_submission")


def grade_submission(submission_id, data):
    """
    Grade an existing submission.
    
    Args:
        submission_id (int): The unique identifier of the submission
        data (dict): Grading data including grade_achieved and grader_feedback
        
    Returns:
        tuple: JSON response with graded submission and HTTP status code
    """
    try:
        logger.info(f"Grading submission: {submission_id}")
        
        submission = db.session.get(Submission, submission_id)
        if not submission:
            return jsonify({"error": "Submission not found"}), 404
        
        # Validate grade if provided
        if 'grade_achieved' in data:
            grade = data['grade_achieved']
            if grade is not None:
                try:
                    grade = float(grade)
                    if grade < 0:
                        return jsonify({"error": "Grade cannot be negative"}), 400
                    
                    # Get assignment to check max_score
                    assignment = db.session.get(Assignment, submission.assignment_id)
                    if assignment and grade > assignment.max_score:
                        return jsonify({"error": f"Grade cannot exceed maximum score of {assignment.max_score}"}), 400
                    
                    submission.grade_achieved = grade
                except (ValueError, TypeError):
                    return jsonify({"error": "Invalid grade format"}), 400
        
        # Update feedback if provided
        if 'grader_feedback' in data:
            submission.grader_feedback = data['grader_feedback']
        
        db.session.commit()
        
        logger.info(f"Successfully graded submission: {submission_id}")
        return jsonify({
            "message": "Submission graded successfully",
            "submission_id": submission.submission_id,
            "grade_achieved": float(submission.grade_achieved) if submission.grade_achieved else None,
            "grader_feedback": submission.grader_feedback
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_request_error("grade_submission", e, submission_id=submission_id)
        return handle_error(e, f"in grade_submission for submission_id={submission_id}")


def get_student_submissions(student_id):
    """
    Get all submissions for a specific student.
    
    Args:
        student_id (str): The unique identifier of the student
        
    Returns:
        tuple: JSON response with student submissions and HTTP status code
    """
    try:
        logger.info(f"Fetching submissions for student: {student_id}")
        
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
                "submissions": [],
                "summary": {
                    "total_submissions": 0,
                    "graded_submissions": 0,
                    "average_grade": 0.0
                }
            }), 200
        
        # Get submissions
        submissions = Submission.query.filter(
            Submission.registration_id.in_(registration_ids)
        ).order_by(Submission.submitted_at.desc()).all()
        
        # Build response with assignment and module information
        result = []
        for submission in submissions:
            assignment = db.session.get(Assignment, submission.assignment_id)
            registration = db.session.get(ModuleRegistration, submission.registration_id)
            module = db.session.get(Module, registration.module_id) if registration else None
            
            result.append({
                "submission_id": submission.submission_id,
                "assignment_id": submission.assignment_id,
                "assignment_title": assignment.title if assignment else "Unknown",
                "module_id": module.module_id if module else None,
                "module_name": module.module_name if module else None,
                "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
                "grade_achieved": float(submission.grade_achieved) if submission.grade_achieved else None,
                "max_score": assignment.max_score if assignment else None,
                "grader_feedback": submission.grader_feedback,
                "due_date": assignment.due_date.isoformat() if assignment and assignment.due_date else None
            })
        
        # Calculate summary statistics
        total_submissions = len(submissions)
        graded_submissions = sum(1 for s in submissions if s.grade_achieved is not None)
        
        if graded_submissions > 0:
            avg_grade = sum(float(s.grade_achieved) for s in submissions if s.grade_achieved is not None) / graded_submissions
        else:
            avg_grade = 0.0
        
        logger.info(f"Successfully retrieved {total_submissions} submissions for student: {student_id}")
        return jsonify({
            "student_id": student_id,
            "student_name": f"{student.first_name} {student.last_name}",
            "submissions": result,
            "summary": {
                "total_submissions": total_submissions,
                "graded_submissions": graded_submissions,
                "average_grade": round(avg_grade, 2)
            }
        }), 200
        
    except Exception as e:
        log_request_error("get_student_submissions", e, student_id=student_id)
        return handle_error(e, f"in get_student_submissions for student_id={student_id}")


def get_assignment_submissions(assignment_id):
    """
    Get all submissions for a specific assignment.
    
    Args:
        assignment_id (str): The unique identifier of the assignment
        
    Returns:
        tuple: JSON response with assignment submissions and HTTP status code
    """
    try:
        logger.info(f"Fetching submissions for assignment: {assignment_id}")
        
        # Validate assignment exists
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404
        
        # Get submissions
        submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
        
        # Build response with student information
        result = []
        for submission in submissions:
            registration = db.session.get(ModuleRegistration, submission.registration_id)
            student = db.session.get(Student, registration.student_id) if registration else None
            
            result.append({
                "submission_id": submission.submission_id,
                "student_id": student.student_id if student else None,
                "student_name": f"{student.first_name} {student.last_name}" if student else "Unknown",
                "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
                "grade_achieved": float(submission.grade_achieved) if submission.grade_achieved else None,
                "grader_feedback": submission.grader_feedback,
                "is_late": submission.submitted_at > assignment.due_date if submission.submitted_at and assignment.due_date else False
            })
        
        # Calculate statistics
        total_submissions = len(submissions)
        graded_count = sum(1 for s in submissions if s.grade_achieved is not None)
        late_submissions = sum(1 for s in submissions if s.submitted_at and assignment.due_date and s.submitted_at > assignment.due_date)
        
        if graded_count > 0:
            avg_grade = sum(float(s.grade_achieved) for s in submissions if s.grade_achieved is not None) / graded_count
        else:
            avg_grade = 0.0
        
        logger.info(f"Successfully retrieved {total_submissions} submissions for assignment: {assignment_id}")
        return jsonify({
            "assignment_id": assignment_id,
            "assignment_title": assignment.title,
            "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
            "max_score": assignment.max_score,
            "submissions": result,
            "summary": {
                "total_submissions": total_submissions,
                "graded_submissions": graded_count,
                "late_submissions": late_submissions,
                "average_grade": round(avg_grade, 2)
            }
        }), 200
        
    except Exception as e:
        log_request_error("get_assignment_submissions", e, assignment_id=assignment_id)
        return handle_error(e, f"in get_assignment_submissions for assignment_id={assignment_id}")


def update_submission(submission_id, data):
    """
    Update an existing submission.
    
    Args:
        submission_id (int): The unique identifier of the submission
        data (dict): Updated submission data
        
    Returns:
        tuple: JSON response with updated submission and HTTP status code
    """
    try:
        logger.info(f"Updating submission: {submission_id}")
        
        submission = db.session.get(Submission, submission_id)
        if not submission:
            return jsonify({"error": "Submission not found"}), 404
        
        # Update allowed fields
        if 'submitted_at' in data:
            try:
                submission.submitted_at = datetime.fromisoformat(data['submitted_at'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid submitted_at format. Use ISO format"}), 400
        
        if 'grade_achieved' in data:
            grade = data['grade_achieved']
            if grade is not None:
                try:
                    grade = float(grade)
                    if grade < 0:
                        return jsonify({"error": "Grade cannot be negative"}), 400
                    
                    # Check against assignment max_score
                    assignment = db.session.get(Assignment, submission.assignment_id)
                    if assignment and grade > assignment.max_score:
                        return jsonify({"error": f"Grade cannot exceed maximum score of {assignment.max_score}"}), 400
                    
                    submission.grade_achieved = grade
                except (ValueError, TypeError):
                    return jsonify({"error": "Invalid grade format"}), 400
            else:
                submission.grade_achieved = None
        
        if 'grader_feedback' in data:
            submission.grader_feedback = data['grader_feedback']
        
        db.session.commit()
        
        logger.info(f"Successfully updated submission: {submission_id}")
        return jsonify({
            "message": "Submission updated successfully",
            "submission_id": submission.submission_id,
            "grade_achieved": float(submission.grade_achieved) if submission.grade_achieved else None,
            "grader_feedback": submission.grader_feedback
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_request_error("update_submission", e, submission_id=submission_id)
        return handle_error(e, f"in update_submission for submission_id={submission_id}")


def delete_submission(submission_id):
    """
    Delete a submission record.
    
    Args:
        submission_id (int): The unique identifier of the submission
        
    Returns:
        tuple: JSON response with success message and HTTP status code
    """
    try:
        logger.info(f"Deleting submission: {submission_id}")
        
        submission = db.session.get(Submission, submission_id)
        if not submission:
            return jsonify({"error": "Submission not found"}), 404
        
        db.session.delete(submission)
        db.session.commit()
        
        logger.info(f"Successfully deleted submission: {submission_id}")
        return jsonify({"message": f"Submission {submission_id} deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        log_request_error("delete_submission", e, submission_id=submission_id)
        return handle_error(e, f"in delete_submission for submission_id={submission_id}")


def get_grading_summary():
    """
    Get overall grading summary across all assignments.
    
    Returns:
        tuple: JSON response with grading statistics and HTTP status code
    """
    try:
        logger.info("Generating grading summary")
        
        # Get all submissions
        submissions = Submission.query.all()
        
        # Calculate overall statistics
        total_submissions = len(submissions)
        graded_submissions = sum(1 for s in submissions if s.grade_achieved is not None)
        ungraded_submissions = total_submissions - graded_submissions
        
        if graded_submissions > 0:
            grades = [float(s.grade_achieved) for s in submissions if s.grade_achieved is not None]
            avg_grade = sum(grades) / len(grades)
            min_grade = min(grades)
            max_grade = max(grades)
        else:
            avg_grade = min_grade = max_grade = 0.0
        
        # Grade distribution
        grade_ranges = {
            "90-100": 0,
            "80-89": 0,
            "70-79": 0,
            "60-69": 0,
            "50-59": 0,
            "0-49": 0
        }
        
        for submission in submissions:
            if submission.grade_achieved is not None:
                grade = float(submission.grade_achieved)
                if grade >= 90:
                    grade_ranges["90-100"] += 1
                elif grade >= 80:
                    grade_ranges["80-89"] += 1
                elif grade >= 70:
                    grade_ranges["70-79"] += 1
                elif grade >= 60:
                    grade_ranges["60-69"] += 1
                elif grade >= 50:
                    grade_ranges["50-59"] += 1
                else:
                    grade_ranges["0-49"] += 1
        
        logger.info(f"Successfully generated grading summary for {total_submissions} submissions")
        return jsonify({
            "summary": {
                "total_submissions": total_submissions,
                "graded_submissions": graded_submissions,
                "ungraded_submissions": ungraded_submissions,
                "grading_completion_rate": round((graded_submissions / total_submissions * 100) if total_submissions > 0 else 0.0, 2)
            },
            "grade_statistics": {
                "average_grade": round(avg_grade, 2),
                "minimum_grade": round(min_grade, 2),
                "maximum_grade": round(max_grade, 2)
            },
            "grade_distribution": grade_ranges
        }), 200
        
    except Exception as e:
        log_request_error("get_grading_summary", e)
        return handle_error(e, "in get_grading_summary")