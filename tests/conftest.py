"""
Test Configuration and Fixtures.

This module provides pytest fixtures for testing the Flask application.
Follows Test-Driven Development (TDD) principles with proper test isolation
and database setup/teardown.

Fixtures:
    app: Configured Flask application instance with test database.
    client: Flask test client for making HTTP requests.
    runner: Flask CLI runner for testing CLI commands.
    sample_survey_data: Pre-populated test data including courses, modules,
        students, registrations, and survey responses.
"""
import pytest
from app import create_app
from app.config import TestConfig
from app.models import db, WeeklySurvey, ModuleRegistration, Student, Module, Course


@pytest.fixture
def app():
    """
    Create and configure a test Flask application.
    
    Sets up a Flask application with test configuration and initializes
    an in-memory database. The database is created before each test and
    torn down after.
    
    Yields:
        Flask: Configured Flask application instance.
    
    Note:
        Uses TestConfig which should configure an in-memory or test database
        to avoid affecting production data.
    """
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Provide a test client for the Flask application.
    
    The test client allows making HTTP requests to the application
    without running a live server.
    
    Args:
        app (Flask): The Flask application fixture.
    
    Returns:
        FlaskClient: Test client for making requests.
    
    Example:
        >>> response = client.get('/api/surveys')
        >>> assert response.status_code == 200
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Provide a CLI runner for testing Flask CLI commands.
    
    Args:
        app (Flask): The Flask application fixture.
    
    Returns:
        FlaskCliRunner: CLI runner for testing commands.
    """
    return app.test_cli_runner()


@pytest.fixture
def sample_survey_data(app):
    """
    Create sample survey data for testing.
    
    Populates the test database with a complete data hierarchy:
    - One course (C001)
    - One module (M001) in that course
    - One student (S001) enrolled in the course
    - One module registration linking student to module
    - Two weekly survey responses
    
    This fixture provides realistic test data for testing survey-related
    endpoints and functionality.
    
    Args:
        app (Flask): The Flask application fixture.
    
    Yields:
        list[WeeklySurvey]: List of created survey objects for assertions.
    
    Note:
        All data is automatically cleaned up after the test due to the
        app fixture's teardown process.
    """
    with app.app_context():
        # Create course
        course = Course(
            course_id="C001",
            course_name="Test Course",
            total_credits=120
        )
        db.session.add(course)
        
        # Create module
        module = Module(
            module_id="M001",
            course_id="C001",
            module_name="Test Module",
            duration_weeks=12
        )
        db.session.add(module)
        
        # Create student
        student = Student(
            student_id="S001",
            first_name="Test",
            last_name="Student",
            email="test@example.com",
            enrolled_year=2024,
            current_course_id="C001"
        )
        db.session.add(student)
        
        from datetime import date
        # Create module registration
        registration = ModuleRegistration(
            student_id="S001",
            module_id="M001",
            status="Active",
            start_date=date(2025, 1, 10)
        )
        db.session.add(registration)
        db.session.commit()
        db.session.refresh(registration)
        
        # Create survey data
        survey1 = WeeklySurvey(
            registration_id=registration.registration_id,
            week_number=1,
            stress_level=2,
            sleep_hours=7.5,
            social_connection_score=4,
            comments="Feeling good"
        )
        survey2 = WeeklySurvey(
            registration_id=registration.registration_id,
            week_number=2,
            stress_level=3,
            sleep_hours=6.8,
            social_connection_score=4,
            comments="More work this week"
        )
        db.session.add(survey1)
        db.session.add(survey2)
        db.session.commit()
        
        yield [survey1, survey2]
