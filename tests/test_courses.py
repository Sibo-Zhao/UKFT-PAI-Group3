"""
TDD Tests for Courses & Modules API
Following TDD: Write tests FIRST, then implement to make them pass.

Test Cases:
1. GET /courses - Returns all courses
2. GET /courses/{course_id}/modules - Returns modules for a course
3. GET /modules/{module_id}/assignments - Returns assignments for a module
"""
import pytest
import json


class TestCoursesEndpoint:
    """Test suite for the courses GET endpoint."""
    
    def test_get_all_courses_success(self, client, sample_survey_data):
        """
        Test that GET /courses returns 200 OK and a list of courses.
        TDD: This test will fail until we implement the endpoint.
        """
        response = client.get("/courses")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_courses_json_structure(self, client, sample_survey_data):
        """
        Test that each course object has the correct JSON structure.
        TDD: Defines the expected response schema.
        """
        response = client.get("/courses")
        courses = json.loads(response.data)
        
        # Check first course has all required fields
        course = courses[0]
        required_fields = [
            "course_id",
            "course_name",
            "total_credits",
            "created_at"
        ]
        
        for field in required_fields:
            assert field in course, f"Missing field: {field}"
    
    def test_get_courses_data_types(self, client, sample_survey_data):
        """
        Test that course fields have correct data types.
        TDD: Ensures proper data validation.
        """
        response = client.get("/courses")
        course = json.loads(response.data)[0]
        
        assert isinstance(course["course_id"], str)
        assert isinstance(course["course_name"], str)
        assert isinstance(course["total_credits"], int)
    
    def test_get_courses_empty_database(self, client):
        """
        Test that endpoint handles empty database gracefully.
        TDD: Edge case handling.
        """
        response = client.get("/courses")
        
        assert response.status_code == 200
        # Should return empty list, not error
        assert isinstance(json.loads(response.data), list)


class TestCourseModulesEndpoint:
    """Test suite for getting modules by course ID."""
    
    def test_get_course_modules_success(self, client, sample_survey_data):
        """
        Test that GET /courses/{course_id}/modules returns modules.
        TDD: This test will fail until we implement the endpoint.
        """
        response = client.get("/courses/C001/modules")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_get_course_modules_json_structure(self, client, sample_survey_data):
        """
        Test that each module object has the correct JSON structure.
        """
        response = client.get("/courses/C001/modules")
        modules = json.loads(response.data)
        
        if len(modules) > 0:
            module = modules[0]
            required_fields = [
                "module_id",
                "course_id",
                "module_name",
                "duration_weeks"
            ]
            
            for field in required_fields:
                assert field in module, f"Missing field: {field}"
    
    def test_get_course_modules_invalid_course(self, client):
        """
        Test that invalid course ID returns empty list or 404.
        TDD: Error handling.
        """
        response = client.get("/courses/INVALID/modules")
        
        # Should return 200 with empty list or 404
        assert response.status_code in [200, 404]
    
    def test_get_course_modules_filters_by_course(self, client, sample_survey_data):
        """
        Test that endpoint only returns modules for the specified course.
        """
        response = client.get("/courses/C001/modules")
        modules = json.loads(response.data)
        
        # All modules should belong to C001
        for module in modules:
            assert module["course_id"] == "C001"


class TestModuleAssignmentsEndpoint:
    """Test suite for getting assignments by module ID."""
    
    def test_get_module_assignments_success(self, client, sample_survey_data):
        """
        Test that GET /modules/{module_id}/assignments returns assignments.
        TDD: This test will fail until we implement the endpoint.
        """
        response = client.get("/modules/M001/assignments")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
    
    def test_get_module_assignments_json_structure(self, client, sample_survey_data):
        """
        Test that each assignment object has the correct JSON structure.
        """
        response = client.get("/modules/M001/assignments")
        assignments = json.loads(response.data)
        
        if len(assignments) > 0:
            assignment = assignments[0]
            required_fields = [
                "assignment_id",
                "module_id",
                "title",
                "description",
                "due_date",
                "max_score",
                "weightage_percent"
            ]
            
            for field in required_fields:
                assert field in assignment, f"Missing field: {field}"
    
    def test_get_module_assignments_data_types(self, client, sample_survey_data):
        """
        Test that assignment fields have correct data types.
        """
        response = client.get("/modules/M001/assignments")
        assignments = json.loads(response.data)
        
        if len(assignments) > 0:
            assignment = assignments[0]
            assert isinstance(assignment["assignment_id"], str)
            assert isinstance(assignment["module_id"], str)
            assert isinstance(assignment["title"], str)
            assert isinstance(assignment["max_score"], int)
            assert isinstance(assignment["weightage_percent"], (int, float))
    
    def test_get_module_assignments_invalid_module(self, client):
        """
        Test that invalid module ID returns empty list or 404.
        """
        response = client.get("/modules/INVALID/assignments")
        
        assert response.status_code in [200, 404]
    
    def test_get_module_assignments_filters_by_module(self, client, sample_survey_data):
        """
        Test that endpoint only returns assignments for the specified module.
        """
        response = client.get("/modules/M001/assignments")
        assignments = json.loads(response.data)
        
        # All assignments should belong to M001
        for assignment in assignments:
            assert assignment["module_id"] == "M001"
