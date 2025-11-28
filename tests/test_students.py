"""
TDD Tests for Student CRUD API
Following TDD: Write tests FIRST, then implement to make them pass.

Test Cases:
1. PUT /students/{id} - Update student information
2. DELETE /students/{id} - Delete student
"""
import pytest
import json


class TestUpdateStudent:
    """Test suite for updating student information."""
    
    def test_update_student_success(self, client, sample_survey_data):
        """
        Test that PUT /students/{id} updates student information.
        TDD: This test will fail until we implement the endpoint.
        """
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com"
        }
        
        response = client.put(
            "/students/S001",
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["email"] == "updated@example.com"
        assert data["student_id"] == "S001"
    
    def test_update_student_partial(self, client, sample_survey_data):
        """
        Test that partial updates work (only updating some fields).
        """
        update_data = {
            "email": "newemail@example.com"
        }
        
        response = client.put(
            "/students/S001",
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["email"] == "newemail@example.com"
        # Original name should remain
        assert data["first_name"] == "Test"
        assert data["last_name"] == "Student"
    
    def test_update_student_not_found(self, client):
        """
        Test that updating non-existent student returns 404.
        """
        update_data = {
            "first_name": "Updated"
        }
        
        response = client.put(
            "/students/NONEXISTENT",
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data
    
    def test_update_student_invalid_email(self, client, sample_survey_data):
        """
        Test that invalid email format returns 400.
        """
        update_data = {
            "email": "invalid-email-format"
        }
        
        response = client.put(
            "/students/S001",
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
    
    def test_update_student_enrolled_year(self, client, sample_survey_data):
        """
        Test updating enrolled year.
        """
        update_data = {
            "enrolled_year": 2025
        }
        
        response = client.put(
            "/students/S001",
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["enrolled_year"] == 2025


class TestDeleteStudent:
    """Test suite for deleting students."""
    
    def test_delete_student_success(self, client, sample_survey_data):
        """
        Test that DELETE /students/{id} deletes a student.
        TDD: This test will fail until we implement the endpoint.
        """
        response = client.delete("/students/S001")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
        assert "deleted" in data["message"].lower()
    
    def test_delete_student_not_found(self, client):
        """
        Test that deleting non-existent student returns 404.
        """
        response = client.delete("/students/NONEXISTENT")
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data
    
    def test_delete_student_verify_deletion(self, client, sample_survey_data):
        """
        Test that deleted student is actually removed from database.
        """
        # Delete the student
        delete_response = client.delete("/students/S001")
        assert delete_response.status_code == 200
        
        # Try to get the student - should return 404
        get_response = client.get("/students/S001")
        assert get_response.status_code == 404
    
    def test_delete_student_cascade_registrations(self, client, sample_survey_data):
        """
        Test that deleting student also removes related registrations.
        Cascade delete should remove all related data.
        """
        # Verify student has registrations before deletion
        from app.models import ModuleRegistration, db
        from flask import current_app
        
        with current_app.app_context():
            registrations_before = ModuleRegistration.query.filter_by(student_id="S001").count()
            assert registrations_before > 0
        
        # Delete the student
        response = client.delete("/students/S001")
        assert response.status_code == 200
        
        # Verify registrations are also deleted
        with current_app.app_context():
            registrations_after = ModuleRegistration.query.filter_by(student_id="S001").count()
            assert registrations_after == 0
    
    def test_delete_student_cascade_surveys(self, client, sample_survey_data):
        """
        Test that deleting student also removes related survey data.
        """
        from app.models import WeeklySurvey, ModuleRegistration, db
        from flask import current_app
        
        with current_app.app_context():
            # Get registration IDs for this student
            registrations = ModuleRegistration.query.filter_by(student_id="S001").all()
            reg_ids = [r.registration_id for r in registrations]
            
            # Verify surveys exist
            surveys_before = WeeklySurvey.query.filter(
                WeeklySurvey.registration_id.in_(reg_ids)
            ).count()
            assert surveys_before > 0
        
        # Delete the student
        response = client.delete("/students/S001")
        assert response.status_code == 200
        
        # Verify surveys are also deleted
        with current_app.app_context():
            surveys_after = WeeklySurvey.query.filter(
                WeeklySurvey.registration_id.in_(reg_ids)
            ).count()
            assert surveys_after == 0
