"""
TDD Tests for Student CRUD API.

This module tests student management endpoints following Test-Driven Development
principles. Tests are written first to define expected behavior, then
implementation is created to make tests pass.

Test Coverage:
    - Student information updates (PUT /students/{id})
    - Student deletion with cascade (DELETE /students/{id})
    - Error handling for invalid operations
    - Data validation

Following TDD Cycle:
    1. RED: Write failing test
    2. GREEN: Implement minimal code to pass
    3. REFACTOR: Improve code while keeping tests green
"""
import pytest
import json


class TestUpdateStudent:
    """
    Test suite for student update operations.
    
    Tests the PUT /students/{id} endpoint for updating student information
    including full updates, partial updates, and error cases.
    """
    
    def test_update_student_success(self, client, sample_survey_data):
        """
        Test successful full update of student information.
        
        Verifies that all student fields can be updated simultaneously
        and the response contains the updated values.
        
        TDD Phase: GREEN - Implementation should make this pass.
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
        Test partial update of student information.
        
        Verifies that only specified fields are updated while other
        fields remain unchanged.
        
        TDD Phase: GREEN - Tests partial update functionality.
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
        Test error handling for non-existent student.
        
        Verifies that attempting to update a student that doesn't exist
        returns a 404 Not Found status with an appropriate error message.
        
        TDD Phase: RED/GREEN - Tests error handling.
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
        Test email validation during update.
        
        Verifies that providing an invalid email format returns a 400 Bad
        Request status, ensuring data integrity.
        
        TDD Phase: RED/GREEN - Tests input validation.
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
    """
    Test suite for student deletion operations.
    
    Tests the DELETE /students/{id} endpoint including cascade deletion
    of related records (registrations, surveys, attendance, submissions).
    """
    
    def test_delete_student_success(self, client, sample_survey_data):
        """
        Test successful deletion of a student.
        
        Verifies that a student can be deleted and a success message
        is returned.
        
        TDD Phase: GREEN - Basic deletion functionality.
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
        Test cascade deletion of module registrations.
        
        Verifies that when a student is deleted, all their module
        registrations are also removed from the database.
        
        TDD Phase: GREEN - Tests cascade delete behavior.
        
        Note:
            This is critical for maintaining referential integrity and
            preventing orphaned records.
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
        Test cascade deletion of survey data.
        
        Verifies that when a student is deleted, all their weekly survey
        responses are also removed from the database.
        
        TDD Phase: GREEN - Tests cascade delete for surveys.
        
        Note:
            Important for GDPR compliance and data cleanup.
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
