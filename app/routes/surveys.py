"""
Survey Routes Blueprint.

This module defines Flask routes for weekly survey operations including
survey retrieval, bulk uploads, deletion, and wellbeing reports.

Endpoints:
    GET /api/surveys - List all surveys
    POST /api/wellbeing/surveys/bulk - Bulk upload surveys
    DELETE /api/wellbeing/surveys/<student_id> - Delete student surveys
    GET /wellbeing/early-warning - Get early warning report
    GET /wellbeing/weekly - Get weekly wellbeing report
"""
from flask import Blueprint, request
from app.controllers import survey_controller, reports_controller

# Create blueprint
surveys_bp = Blueprint('surveys', __name__)


@surveys_bp.route('/api/wellbeing/surveys/<string:student_id>', methods=['DELETE'])
def delete_student_surveys(student_id):
    """Delete all survey data for a specific student."""
    return survey_controller.delete_student_surveys(student_id)


@surveys_bp.route('/api/surveys', methods=['GET'])
def get_all_surveys():
    """
    Get all weekly survey records.
    
    Returns:
        JSON response with list of all surveys.
    """
    return survey_controller.get_all_surveys()


@surveys_bp.route('/api/wellbeing/surveys/bulk', methods=['POST'])
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


@surveys_bp.route('/wellbeing/early-warning', methods=['GET'])
def get_early_warning():
    """
    Get early warning report for students with high stress levels (4-5) or low sleep hours (< 5).
    
    Returns:
        JSON response with:
        - high_stress_students: count and list of students with stress level 4-5
        - low_sleep_students: count and list of students with sleep hours < 5
    """
    return reports_controller.get_early_warning()


@surveys_bp.route('/wellbeing/weekly', methods=['GET'])
def get_weekly_report():
    """
    Get weekly report with average stress level and sleep hours, comparing current week with previous week.
    
    Returns:
        JSON response with:
        - current_week: latest week number
        - previous_week: previous week number (if available)
        - stress_level: current and previous week averages, change, and description
        - sleep_hours: current and previous week averages, change, and description
    """
    return reports_controller.get_weekly_report()