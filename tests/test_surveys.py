"""
TDD Tests for Weekly Surveys API (Flask)
Following TDD: Write tests FIRST, then implement to make them pass.

Test Cases:
1. GET /api/surveys - Returns all surveys
2. Validate JSON structure
3. Validate data types
4. Handle empty database
5. Handle database errors
"""
import pytest
import json


class TestWeeklySurveysEndpoint:
    """Test suite for the weekly surveys GET endpoint."""
    
    def test_get_all_surveys_success(self, client, sample_survey_data):
        """
        Test that GET /api/surveys returns 200 OK and a list of surveys.
        TDD: This test validates the Flask endpoint works correctly.
        """
        response = client.get("/surveys")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 2
    
    def test_get_surveys_json_structure(self, client, sample_survey_data):
        """
        Test that each survey object has the correct JSON structure.
        TDD: Defines the expected response schema.
        """
        response = client.get("/surveys")
        surveys = json.loads(response.data)
        
        # Check first survey has all required fields
        survey = surveys[0]
        required_fields = [
            "survey_id",
            "registration_id",
            "week_number",
            "submitted_at",
            "stress_level",
            "sleep_hours",
            "social_connection_score",
            "comments"
        ]
        
        for field in required_fields:
            assert field in survey, f"Missing field: {field}"
    
    def test_get_surveys_data_types(self, client, sample_survey_data):
        """
        Test that survey fields have correct data types.
        TDD: Ensures proper data validation.
        """
        response = client.get("/surveys")
        survey = json.loads(response.data)[0]
        
        assert isinstance(survey["survey_id"], int)
        assert isinstance(survey["registration_id"], int)
        assert isinstance(survey["week_number"], int)
        assert isinstance(survey["stress_level"], int)
        assert isinstance(survey["sleep_hours"], (int, float))
        assert isinstance(survey["social_connection_score"], int)
        assert isinstance(survey["comments"], (str, type(None)))
    
    def test_get_surveys_stress_level_validation(self, client, sample_survey_data):
        """
        Test that stress_level is between 1 and 5.
        TDD: Validates business rules.
        """
        response = client.get("/surveys")
        surveys = json.loads(response.data)
        
        for survey in surveys:
            assert 1 <= survey["stress_level"] <= 5
    
    def test_get_surveys_social_score_validation(self, client, sample_survey_data):
        """
        Test that social_connection_score is between 1 and 5.
        TDD: Validates business rules.
        """
        response = client.get("/surveys")
        surveys = json.loads(response.data)
        
        for survey in surveys:
            assert 1 <= survey["social_connection_score"] <= 5
    
    def test_get_surveys_empty_database(self, client):
        """
        Test that endpoint handles empty database gracefully.
        TDD: Edge case handling.
        """
        response = client.get("/surveys")
        
        assert response.status_code == 200
        assert json.loads(response.data) == []
    
    def test_get_surveys_returns_correct_count(self, client, sample_survey_data):
        """
        Test that the endpoint returns the correct number of surveys.
        TDD: Verify query returns all records.
        """
        response = client.get("/surveys")
        surveys = json.loads(response.data)
        
        assert len(surveys) == len(sample_survey_data)


class TestSurveyDataIntegrity:
    """Test suite for data integrity and relationships."""
    
    def test_survey_has_valid_registration_id(self, client, sample_survey_data):
        """
        Test that surveys have valid registration IDs.
        TDD: Ensures foreign key relationships are maintained.
        """
        response = client.get("/surveys")
        surveys = json.loads(response.data)
        
        for survey in surveys:
            assert survey["registration_id"] > 0
    
    def test_survey_week_number_positive(self, client, sample_survey_data):
        """
        Test that week numbers are positive integers.
        TDD: Validates week number constraints.
        """
        response = client.get("/surveys")
        surveys = json.loads(response.data)
        
        for survey in surveys:
            assert survey["week_number"] > 0
    
    def test_survey_sleep_hours_reasonable(self, client, sample_survey_data):
        """
        Test that sleep hours are in a reasonable range (0-24).
        TDD: Validates sleep hours constraints.
        """
        response = client.get("/surveys")
        surveys = json.loads(response.data)
        
        for survey in surveys:
            assert 0 <= survey["sleep_hours"] <= 24


class TestFlaskAppHealth:
    """Test suite for Flask application health checks."""
    
    def test_root_endpoint(self, client):
        """Test that root endpoint returns app info."""
        response = client.get("/")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["framework"] == "Flask"
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
