from flask import jsonify
from app.models import WeeklySurvey, ModuleRegistration, db
from app.views.schemas import weekly_surveys_schema

def delete_student_surveys(student_id):
    """Delete all survey data for a specific student."""
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
    Get all weekly survey records.
    """
    try:
        surveys = WeeklySurvey.query.all()
        result = weekly_surveys_schema.dump(surveys)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def bulk_upload_surveys(data):
    """
    Bulk upload survey records.
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
