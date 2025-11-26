"""
Test fixtures for Flask application tests.
Following TDD principles with Flask test client.
"""
import pytest
from app import create_app
from app.config import TestConfig
from app.models import db, WeeklySurvey, ModuleRegistration, Student, Module, Course


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Provide a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Provide a CLI runner for the Flask app."""
    return app.test_cli_runner()


@pytest.fixture
def sample_survey_data(app):
    """Create sample survey data for testing."""
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
