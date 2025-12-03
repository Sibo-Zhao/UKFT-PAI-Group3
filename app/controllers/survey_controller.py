"""
Survey Controller Module.

This module handles operations related to weekly wellbeing surveys including
retrieval, bulk uploads, and deletion of survey data.
"""
from flask import jsonify
from app.models import WeeklySurvey, ModuleRegistration, db
from app.views.schemas import weekly_surveys_schema


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
    
    Example Response:
        {
            "message": "Deleted 12 survey records for student S001",
            "deleted_count": 12
        }
    """
    try:
        # Get all registrations for this student
        registrations = ModuleRegistration.query.filter_by(student_id=student_id).all()
        registration_ids = [r.registration_id for r in registrations]
        
        if not registration_ids:
            return jsonify({"error": "Student not found or has no registrations"}), 404
        
        # Delete all surveys for this student's registrations
        deleted_count = WeeklySurvey.query.filter(
            WeeklySurvey.registration_id.in_(registration_ids)
        ).delete()
        
        db.session.commit()
        
        return jsonify({
            "message": f"Deleted {deleted_count} survey records for student {student_id}",
            "deleted_count": deleted_count
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

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
    """
    try:
        surveys = WeeklySurvey.query.all()
        result = weekly_surveys_schema.dump(surveys)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    
    Example Response:
        {
            "message": "Successfully created 15 survey records",
            "count": 15
        }
    
    Note:
        Surveys with invalid registration IDs are silently skipped.
    """
    try:
        surveys = data.get('surveys', [])
        
        if not surveys:
            return jsonify({"error": "No surveys provided"}), 400
        
        created_count = 0
        for survey_data in surveys:
            # Validate registration exists
            registration = db.session.get(ModuleRegistration, survey_data['registration_id'])
            if not registration:
                continue  # Skip invalid registrations
            
            survey = WeeklySurvey(
                registration_id=survey_data['registration_id'],
                week_number=survey_data['week_number'],
                stress_level=survey_data['stress_level'],
                sleep_hours=survey_data['sleep_hours'],
                social_connection_score=survey_data['social_connection_score'],
                comments=survey_data.get('comments')
            )
            db.session.add(survey)
            created_count += 1
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully created {created_count} survey records",
            "count": created_count
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
