"""
TDD Tests for Academic Assignments API.

This module tests assignment CRUD operations following Test-Driven Development
principles. Tests verify assignment creation, updates, deletion, and error
handling.

Test Coverage:
    - Assignment creation (POST /academic/assignments)
    - Assignment updates (PUT /academic/assignments/{id})
    - Assignment deletion (DELETE /academic/assignments/{id})
    - Input validation and error handling
    - Foreign key constraint validation

Following TDD Cycle:
    1. RED: Write test defining expected behavior
    2. GREEN: Implement endpoint to pass test
    3. REFACTOR: Optimize while maintaining test success
"""
import pytest
import json
from datetime import datetime, timedelta
from datetime import timezone


class TestCreateAssignment:
    """
    Test suite for assignment creation operations.
    
    Tests the POST /academic/assignments endpoint for creating new
    assignments with proper validation.
    """
    
    def test_create_assignment_success(self, client, sample_survey_data): 
        """
        Test successful creation of a new assignment.
        
        Verifies that a valid assignment can be created and returns
        a 201 Created status with the assignment data.
        
        TDD Phase: GREEN - Basic creation functionality.
        """
        assignment_data = {
            "assignment_id": "A999",
            "module_id": "M001",
            "title": "Test Assignment",
            "description": "Test description",
            # "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "due_date": "2025-12-01T00:00:00Z",
            "max_score": 100,
            "weightage_percent": 25.0
        }
        
        response = client.post(
            "/academic/assignments",
            data=json.dumps(assignment_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["assignment_id"] == "A999"
        assert data["title"] == "Test Assignment"
    
    def test_create_assignment_missing_fields(self, client, sample_survey_data):
        """
        Test validation of required fields.
        
        Verifies that attempting to create an assignment without required
        fields returns a 400 Bad Request status.
        
        TDD Phase: RED/GREEN - Tests input validation.
        """
        assignment_data = {
            "module_id": "M001"
            # Missing required fields
        }
        
        response = client.post(
            "/academic/assignments",
            data=json.dumps(assignment_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_create_assignment_invalid_module(self, client):
        """
        Test that invalid module_id returns 400 or 404.
        """
        assignment_data = {
            "assignment_id": "A999",
            "module_id": "INVALID",
            "title": "Test Assignment",
            # "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "due_date": "2025-12-01T00:00:00Z",
            "max_score": 100
        }
        
        response = client.post(
            "/academic/assignments",
            data=json.dumps(assignment_data),
            content_type='application/json'
        )
        
        # Should validate module exists
        assert response.status_code in [400, 404]


class TestUpdateAssignment:
    """
    Test suite for assignment update operations.
    
    Tests the PUT /academic/assignments/{id} endpoint for updating
    existing assignments.
    """
    
    def test_update_assignment_success(self, client, sample_survey_data):
        """
        Test successful update of assignment information.
        
        Verifies that assignment fields can be updated and the response
        contains the updated values.
        
        TDD Phase: GREEN - Basic update functionality.
        """
        assignment_data = {
        "assignment_id": "A001",
        "module_id": "M001", 
        "title": "Original Title",
        "description": "Test description",
        "due_date": "2025-12-01T00:00:00Z",
        "max_score": 100,
        "weightage_percent": 25.0
        }
        client.post("/academic/assignments", json=assignment_data)
        update_data = {
            "title": "Updated Assignment Title",
            "max_score": 150
        }
        
        response = client.put(
            "/academic/assignments/A001",
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["title"] == "Updated Assignment Title"
        assert data["max_score"] == 150
    
    def test_update_assignment_not_found(self, client):
        """
        Test that updating non-existent assignment returns 404.
        """
        update_data = {
            "title": "Updated Title"
        }
        
        response = client.put(
            "/academic/assignments/NONEXISTENT",
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404


class TestDeleteAssignment:
    """
    Test suite for assignment deletion operations.
    
    Tests the DELETE /academic/assignments/{id} endpoint for removing
    assignments from the system.
    """
    
    def test_delete_assignment_success(self, client, sample_survey_data):
        """
        Test successful deletion of an assignment.
        
        Verifies that an assignment can be deleted and a success message
        is returned.
        
        TDD Phase: GREEN - Basic deletion functionality.
        """
        assignment_data = {
        "assignment_id": "A001",
        "module_id": "M001",
        "title": "Test Assignment", 
        "description": "Test description",
        "due_date": "2025-12-01T00:00:00Z",
        "max_score": 100,
        "weightage_percent": 25.0
        }
        client.post("/academic/assignments", json=assignment_data)
        response = client.delete("/academic/assignments/A001")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "message" in data
    
    def test_delete_assignment_not_found(self, client):
        """
        Test that deleting non-existent assignment returns 404.
        """
        response = client.delete("/academic/assignments/NONEXISTENT")
        
        assert response.status_code == 404
    
    def test_delete_assignment_verify_deletion(self, client, sample_survey_data):
        """
        Test verification of assignment deletion.
        
        Verifies that after deletion, the assignment no longer appears
        in the module's assignment list.
        
        TDD Phase: GREEN - Tests deletion persistence.
        """
        # Delete the assignment
        client.delete("/academic/assignments/A001")
        
        # Try to get assignments for the module
        response = client.get("/modules/M001/assignments")
        assignments = json.loads(response.data)
        
        # A001 should not be in the list
        assignment_ids = [a["assignment_id"] for a in assignments]
        assert "A001" not in assignment_ids
