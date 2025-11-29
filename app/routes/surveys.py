"""
Survey routes blueprint.
Flask blueprint for weekly survey endpoints.
"""
from flask import Blueprint, request
from app.controllers import survey_controller

# Create blueprint
surveys_bp = Blueprint('surveys', __name__, url_prefix='/api')


@surveys_bp.route('/wellbeing/surveys/<string:student_id>', methods=['DELETE'])
def delete_student_surveys(student_id):
    """Delete all survey data for a specific student."""
    return survey_controller.delete_student_surveys(student_id)


@surveys_bp.route('/surveys', methods=['GET'])
def get_all_surveys():
    """
    Get all weekly survey records.
    
    Returns:
        JSON response with list of all surveys.
    """
    return survey_controller.get_all_surveys()


@surveys_bp.route('/wellbeing/surveys/bulk', methods=['POST'])
def bulk_upload_surveys():
    """
    Bulk upload survey records.
    
    Request Body:
        {
            "surveys": [
                {
                    "registration_id": 1,
                    "week_number": 1,
                    "stress_level": 3,
                    "sleep_hours": 7.5,
                    "social_connection_score": 4,
                    "comments": "Feeling good"
                }
            ]
        }
        
    Returns:
        JSON response with created count (201) or error (400)
    """
    data = request.get_json()
    return survey_controller.bulk_upload_surveys(data)
