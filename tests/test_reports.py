import pytest
from app import create_app, db
from app.models import Student, Module, ModuleRegistration, WeeklyAttendance, Submission, Assignment, WeeklySurvey
from datetime import datetime, date, timedelta

@pytest.fixture
def app():
    class TestConfig:
        TESTING = True
        DEBUG = True
        SECRET_KEY = 'test-key'
        @property
        def database_url(self):
            return 'sqlite:///:memory:'

    app = create_app(config_class=TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def sample_data(app):
    with app.app_context():
        # Create Module
        module = Module(module_id="CS101", module_name="Intro to CS")
        db.session.add(module)
        
        # Create Student
        student = Student(student_id="S001", first_name="John", last_name="Doe", email="john@example.com")
        db.session.add(student)
        
        # Create Registration
        reg = ModuleRegistration(student_id="S001", module_id="CS101")
        db.session.add(reg)
        db.session.commit()
        
        # Create Assignment
        assign1 = Assignment(assignment_id="A1", module_id="CS101", title="A1", due_date=datetime.now())
        assign2 = Assignment(assignment_id="A2", module_id="CS101", title="A2", due_date=datetime.now())
        db.session.add_all([assign1, assign2])
        db.session.commit()
        
        # Create Submissions (Declining grades: 80 -> 60)
        sub1 = Submission(registration_id=reg.registration_id, assignment_id="A1", grade_achieved=80, submitted_at=datetime.now() - timedelta(days=7))
        sub2 = Submission(registration_id=reg.registration_id, assignment_id="A2", grade_achieved=60, submitted_at=datetime.now())
        db.session.add_all([sub1, sub2])
        
        # Create Attendance (Absent)
        att = WeeklyAttendance(registration_id=reg.registration_id, week_number=1, class_date=date.today(), is_present=False)
        db.session.add(att)
        
        # Create Survey
        survey = WeeklySurvey(registration_id=reg.registration_id, week_number=1, stress_level=3, sleep_hours=7)
        db.session.add(survey)
        
        db.session.commit()

def test_api_5_module_info(client, sample_data):
    """Test API 5: Module Info"""
    response = client.get('/reports/module/CS101/academic')
    assert response.status_code == 200
    data = response.get_json()
    assert data['module_name'] == "Intro to CS"
    assert 'pass_rate' in data
    assert data['pass_rate'] == 100.0  # Average is 70, so passed

def test_api_6_weekly_report(client, sample_data):
    """Test API 6: Weekly Attendance Report"""
    response = client.get('/reports/weekly/attendance')
    assert response.status_code == 200
    data = response.get_json()
    assert 'attendance_rate' in data
    assert data['attendance_rate']['current_week_average'] == 0.0  # 1 absent record

def test_api_7_absent_students(client, sample_data):
    """Test API 7: Absent Students Report"""
    response = client.get('/reports/weekly/absences')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['student_id'] == "S001"
    assert data[0]['total_absences'] == 1

def test_api_8_grade_decline(client, sample_data):
    """Test API 8: Grade Decline Report"""
    response = client.get('/reports/weekly/grade-decline')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['student_id'] == "S001"
    assert data[0]['decline'] == 20.0  # 80 - 60 = 20
