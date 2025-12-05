"""
Submission Routes.

This module defines API endpoints for assignment submission management including
creating submissions, grading, and retrieving submission data.
"""
from flask import Blueprint, request
from app.controllers.submission_controller import (
    create_submission, grade_submission, get_student_submissions,
    get_assignment_submissions, update_submission, delete_submission,
    get_grading_summary
)

submissions_bp = Blueprint('submissions', __name__)


@submissions_bp.route('/submissions', methods=['POST'])
def create_new_submission():
    """
    Create a new assignment submission.
    
    Expected JSON payload:
        {
            "registration_id": int,
            "assignment_id": "string",
            "submitted_at": "ISO datetime string" (optional, defaults to current time),
            "grade_achieved": float (optional),
            "grader_feedback": "string" (optional)
        }
        
    Returns:
        JSON response with submission record
    """
    return create_submission(request.json)


@submissions_bp.route('/submissions/<int:submission_id>/grade', methods=['PUT'])
def grade_student_submission(submission_id):
    """
    Grade an existing submission.
    
    Args:
        submission_id (int): The unique identifier of the submission
        
    Expected JSON payload:
        {
            "grade_achieved": float,
            "grader_feedback": "string" (optional)
        }
        
    Returns:
        JSON response with graded submission
    """
    return grade_submission(submission_id, request.json)


@submissions_bp.route('/submissions/student/<student_id>', methods=['GET'])
def get_submissions_for_student(student_id):
    """
    Get all submissions for a specific student.
    
    Args:
        student_id (str): The unique identifier of the student
        
    Returns:
        JSON response with student submissions and summary statistics
    """
    return get_student_submissions(student_id)


@submissions_bp.route('/submissions/assignment/<assignment_id>', methods=['GET'])
def get_submissions_for_assignment(assignment_id):
    """
    Get all submissions for a specific assignment.
    
    Args:
        assignment_id (str): The unique identifier of the assignment
        
    Returns:
        JSON response with assignment submissions and statistics
    """
    return get_assignment_submissions(assignment_id)


@submissions_bp.route('/submissions/<int:submission_id>', methods=['PUT'])
def update_submission_record(submission_id):
    """
    Update an existing submission.
    
    Args:
        submission_id (int): The unique identifier of the submission
        
    Expected JSON payload:
        {
            "submitted_at": "ISO datetime string" (optional),
            "grade_achieved": float (optional),
            "grader_feedback": "string" (optional)
        }
        
    Returns:
        JSON response with updated submission
    """
    return update_submission(submission_id, request.json)


@submissions_bp.route('/submissions/<int:submission_id>', methods=['DELETE'])
def delete_submission_record(submission_id):
    """
    Delete a submission record.
    
    Args:
        submission_id (int): The unique identifier of the submission
        
    Returns:
        JSON response with success message
    """
    return delete_submission(submission_id)


@submissions_bp.route('/submissions/summary', methods=['GET'])
def get_overall_grading_summary():
    """
    Get overall grading summary across all assignments.
    
    Returns:
        JSON response with grading statistics and grade distribution
    """
    return get_grading_summary()