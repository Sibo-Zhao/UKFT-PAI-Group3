"""
Survey routes blueprint.
Flask blueprint for weekly survey endpoints.
"""
from flask import Blueprint, jsonify, request
from app.models import WeeklySurvey, db
from app.schemas import weekly_surveys_schema

# Create blueprint
surveys_bp = Blueprint('surveys', __name__, url_prefix='/api')

@surveys_bp.route('/wellbeing/surveys/<string:student_id>', methods=['DELETE'])
def delete_student_surveys(student_id):
    """Delete all survey data for a specific student."""
    try:
        from app.models import ModuleRegistration
        
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

@surveys_bp.route('/surveys', methods=['GET'])
def get_all_surveys():
    """
    Get all weekly survey records.
    
    Returns:
        JSON response with list of all surveys.
    """
    try:
        surveys = WeeklySurvey.query.all()
        result = weekly_surveys_schema.dump(surveys)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
    try:
        from app.models import ModuleRegistration
        data = request.get_json()
        surveys = data.get('surveys', [])
        
        if not surveys:
            return jsonify({"error": "No surveys provided"}), 400
        
        created_count = 0
        for survey_data in surveys:
            # Validate registration exists
            # registration = ModuleRegistration.query.get(survey_data['registration_id'])
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
