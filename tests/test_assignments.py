"""
TDD Tests for Academic Assignments API
Following TDD: Write tests FIRST, then implement to make them pass.

Test Cases:
1. POST /academic/assignments - Create assignment
2. PUT /academic/assignments/{id} - Update assignment
3. DELETE /academic/assignments/{id} - Delete assignment
"""
import pytest
import json
from datetime import datetime, timedelta


class TestCreateAssignment:
    """Test suite for creating assignments."""
    
    def test_create_assignment_success(self, client):
        """
        Test that POST /academic/assignments creates a new assignment.
        TDD: This test will fail until we implement the endpoint.
        """
        assignment_data = {
            "assignment_id": "A999",
            "module_id": "M001",
            "title": "Test Assignment",
            "description": "Test description",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
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
    
    def test_create_assignment_missing_fields(self, client):
        """
        Test that missing required fields returns 400.
        TDD: Validation error handling.
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
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
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
    """Test suite for updating assignments."""
    
    def test_update_assignment_success(self, client, sample_survey_data):
        """
        Test that PUT /academic/assignments/{id} updates an assignment.
        """
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
    """Test suite for deleting assignments."""
    
    def test_delete_assignment_success(self, client, sample_survey_data):
        """
        Test that DELETE /academic/assignments/{id} deletes an assignment.
        """
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
        Test that deleted assignment is actually removed.
        """
        # Delete the assignment
        client.delete("/academic/assignments/A001")
        
        # Try to get assignments for the module
        response = client.get("/modules/M001/assignments")
        assignments = json.loads(response.data)
        
        # A001 should not be in the list
        assignment_ids = [a["assignment_id"] for a in assignments]
        assert "A001" not in assignment_ids
