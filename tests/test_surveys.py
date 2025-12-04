"""
TDD Tests for Weekly Surveys API.

This module tests weekly survey endpoints following Test-Driven Development
principles. Tests verify survey retrieval, data validation, and business
rule enforcement.

Test Coverage:
    - Survey listing (GET /api/surveys)
    - JSON response structure validation
    - Data type validation
    - Business rule validation (stress levels, sleep hours, etc.)
    - Edge case handling (empty database)
    - Application health checks

Following TDD Cycle:
    1. RED: Write test defining expected behavior
    2. GREEN: Implement endpoint to pass test
    3. REFACTOR: Optimize while maintaining test success
"""
import pytest
import json


class TestWeeklySurveysEndpoint:
    """
    Test suite for weekly survey retrieval.
    
    Tests the GET /api/surveys endpoint for retrieving all survey responses
    from the database.
    """
    
    def test_get_all_surveys_success(self, client, sample_survey_data):
        """
        Test successful retrieval of all surveys.
        
        Verifies that the endpoint returns a 200 status and a list of
        survey objects matching the expected count.
        
        TDD Phase: GREEN - Basic endpoint functionality.
        """
        response = client.get("/api/surveys")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 2
    
    def test_get_surveys_json_structure(self, client, sample_survey_data):
        """
        Test survey response JSON structure.
        
        Verifies that each survey object contains all required fields
        with correct naming, defining the API contract.
        
        TDD Phase: RED - Defines expected API schema.
        """
        response = client.get("/api/surveys")
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
        Test survey field data types.
        
        Verifies that each field in the survey response has the correct
        data type (int, float, string, etc.).
        
        TDD Phase: GREEN - Tests serialization correctness.
        """
        response = client.get("/api/surveys")
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
        Test stress level business rule validation.
        
        Verifies that all stress level values fall within the valid
        range of 1-5 as defined by business requirements.
        
        TDD Phase: GREEN - Tests business rule enforcement.
        """
        response = client.get("/api/surveys")
        surveys = json.loads(response.data)
        
        for survey in surveys:
            assert 1 <= survey["stress_level"] <= 5
    
    def test_get_surveys_social_score_validation(self, client, sample_survey_data):
        """
        Test that social_connection_score is between 1 and 5.
        TDD: Validates business rules.
        """
        response = client.get("/api/surveys")
        surveys = json.loads(response.data)
        
        for survey in surveys:
            assert 1 <= survey["social_connection_score"] <= 5
    
    def test_get_surveys_empty_database(self, client):
        """
        Test that endpoint handles empty database gracefully.
        TDD: Edge case handling.
        """
        response = client.get("/api/surveys")
        
        assert response.status_code == 200
        assert json.loads(response.data) == []
    
    def test_get_surveys_returns_correct_count(self, client, sample_survey_data):
        """
        Test that the endpoint returns the correct number of surveys.
        TDD: Verify query returns all records.
        """
        response = client.get("/api/surveys")
        surveys = json.loads(response.data)
        
        assert len(surveys) == len(sample_survey_data)


class TestSurveyDataIntegrity:
    """
    Test suite for survey data integrity and relationships.
    
    Tests that survey data maintains proper relationships and constraints
    as defined by the database schema.
    """
    
    def test_survey_has_valid_registration_id(self, client, sample_survey_data):
        """
        Test foreign key relationship integrity.
        
        Verifies that all surveys have valid registration IDs, ensuring
        referential integrity is maintained.
        
        TDD Phase: GREEN - Tests database constraints.
        """
        response = client.get("/api/surveys")
        surveys = json.loads(response.data)
        
        for survey in surveys:
            assert survey["registration_id"] > 0
    
    def test_survey_week_number_positive(self, client, sample_survey_data):
        """
        Test that week numbers are positive integers.
        TDD: Validates week number constraints.
        """
        response = client.get("/api/surveys")
        surveys = json.loads(response.data)
        
        for survey in surveys:
            assert survey["week_number"] > 0
    
    def test_survey_sleep_hours_reasonable(self, client, sample_survey_data):
        """
        Test that sleep hours are in a reasonable range (0-24).
        TDD: Validates sleep hours constraints.
        """
        response = client.get("/api/surveys")
        surveys = json.loads(response.data)
        
        for survey in surveys:
            assert 0 <= survey["sleep_hours"] <= 24


class TestFlaskAppHealth:
    """
    Test suite for Flask application health checks.
    
    Tests basic application endpoints to verify the Flask app is
    running correctly.
    """
    
    def test_root_endpoint(self, client):
        """
        Test root endpoint returns application information.
        
        Verifies that the root endpoint is accessible and returns
        basic application metadata.
        
        TDD Phase: GREEN - Basic health check.
        """
        response = client.get("/")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["framework"] == "Flask"
    
    def test_health_endpoint(self, client):
        """
        Test health check endpoint.
        
        Verifies that the /health endpoint returns a healthy status,
        useful for monitoring and deployment checks.
        
        TDD Phase: GREEN - Health monitoring.
        """
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
