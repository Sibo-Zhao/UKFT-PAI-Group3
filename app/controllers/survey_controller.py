"""
Survey Controller Module.

This module handles operations related to weekly wellbeing surveys including
retrieval, bulk uploads, and deletion of survey data.
"""
from flask import jsonify
from app.models import WeeklySurvey, ModuleRegistration, db
from app.views.schemas import weekly_surveys_schema
from app.constants import ERROR_STUDENT_NOT_FOUND
from app.utils.error_handlers import handle_error, log_request_error
import logging

logger = logging.getLogger(__name__)


def delete_student_surveys(student_id):
    """
    Delete all survey data for a specific student.
    
    Removes all weekly survey records associated with the student's module
    registrations. This is useful for data cleanup or GDPR compliance.
    
    Args:
        student_id (str): The unique identifier of the student.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with deletion summary
            - int: HTTP status code
                - 200: Deletion successful
                - 404: Student not found or has no registrations
                - 500: Server error
    
    Raises:
        DatabaseError: If database operation fails.
    
    Example Response:
        {
            "message": "Deleted 12 survey records for student S001",
            "deleted_count": 12
        }
    
    Note:
        This operation cannot be undone. All survey data for the student
        will be permanently removed from the database.
    """
    try:
        logger.info(f"Deleting survey data for student: {student_id}")
        
        # Get all registrations for this student
        registrations = ModuleRegistration.query.filter_by(student_id=student_id).all()
        registration_ids = [r.registration_id for r in registrations]
        
        if not registration_ids:
            logger.warning(f"No registrations found for student: {student_id}")
            return jsonify({"error": "Student not found or has no registrations"}), 404
        
        # Delete all surveys for this student's registrations
        deleted_count = WeeklySurvey.query.filter(
            WeeklySurvey.registration_id.in_(registration_ids)
        ).delete(synchronize_session=False)
        
        db.session.commit()
        
        logger.info(f"Successfully deleted {deleted_count} survey records for student: {student_id}")
        return jsonify({
            "message": f"Deleted {deleted_count} survey records for student {student_id}",
            "deleted_count": deleted_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_request_error("delete_student_surveys", e, student_id=student_id)
        return handle_error(e, f"in delete_student_surveys for student_id={student_id}")

def get_all_surveys():
    """
    Retrieve all weekly survey records from the database.
    
    Fetches all survey responses and serializes them using the survey schema.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with list of surveys
            - int: HTTP status code
                - 200: Success
                - 500: Server error
    
    Raises:
        DatabaseError: If database query fails.
    
    Example Response:
        [
            {
                "survey_id": 1,
                "registration_id": 1,
                "week_number": 1,
                "submitted_at": "2025-01-15T10:30:00",
                "stress_level": 3,
                "sleep_hours": 7.5,
                "social_connection_score": 4,
                "comments": "Feeling good this week"
            }
        ]
    
    Note:
        This endpoint returns all survey records. Consider implementing
        pagination for large datasets in production environments.
    """
    try:
        logger.info("Fetching all survey records")
        surveys = WeeklySurvey.query.all()
        result = weekly_surveys_schema.dump(surveys)
        logger.info(f"Successfully retrieved {len(surveys)} survey records")
        return jsonify(result), 200
        
    except Exception as e:
        log_request_error("get_all_surveys", e)
        return handle_error(e, "in get_all_surveys")

def bulk_upload_surveys(data):
    """
    Bulk upload multiple survey records at once.
    
    Validates each survey record and creates entries in the database.
    Invalid registrations are skipped without failing the entire operation.
    
    Args:
        data (dict): Request data containing survey records.
            Expected structure:
                {
                    "surveys": [
                        {
                            "registration_id": int,
                            "week_number": int,
                            "stress_level": int (1-5),
                            "sleep_hours": float,
                            "social_connection_score": int (1-5),
                            "comments": str (optional)
                        }
                    ]
                }
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with upload summary
            - int: HTTP status code
                - 201: Upload successful
                - 400: No surveys provided
                - 500: Server error
    
    Raises:
        ValueError: If survey data format is invalid.
        DatabaseError: If database operation fails.
    
    Example Response:
        {
            "message": "Successfully created 15 survey records",
            "count": 15,
            "skipped": 2
        }
    
    Note:
        Surveys with invalid registration IDs are silently skipped.
        The response includes both created and skipped counts for transparency.
    """
    try:
        logger.info("Starting bulk survey upload")
        surveys = data.get('surveys', [])
        
        if not surveys:
            logger.warning("No surveys provided in bulk upload request")
            return jsonify({"error": "No surveys provided"}), 400
        
        created_count = 0
        skipped_count = 0
        
        for survey_data in surveys:
            try:
                # Validate registration exists
                registration = db.session.get(ModuleRegistration, survey_data['registration_id'])
                if not registration:
                    skipped_count += 1
                    continue  # Skip invalid registrations
                
                survey = WeeklySurvey(
                    registration_id=survey_data['registration_id'],
                    week_number=survey_data['week_number'],
                    stress_level=survey_data.get('stress_level'),
                    sleep_hours=survey_data.get('sleep_hours'),
                    social_connection_score=survey_data.get('social_connection_score'),
                    comments=survey_data.get('comments')
                )
                db.session.add(survey)
                created_count += 1
                
            except (KeyError, ValueError) as e:
                logger.warning(f"Invalid survey data format: {e}")
                skipped_count += 1
                continue
        
        db.session.commit()
        
        logger.info(f"Bulk upload completed: {created_count} created, {skipped_count} skipped")
        return jsonify({
            "message": f"Successfully created {created_count} survey records",
            "count": created_count,
            "skipped": skipped_count
        }), 201
        
    except Exception as e:
        db.session.rollback()
        log_request_error("bulk_upload_surveys", e)
        return handle_error(e, "in bulk_upload_surveys")
