"""
Test CSV Upload for SWO Surveys.

This module tests the CSV upload functionality for Student Wellbeing Officer surveys,
including validation, student updates, and survey creation.
"""
import pytest
import io
from app.models import Student, WeeklySurvey, ModuleRegistration, Course, Module, db


class TestCSVUpload:
    """Test suite for CSV upload of SWO surveys."""
    
    @pytest.fixture
    def setup_test_data(self, app):
        """Create test students, courses, and modules for CSV upload tests."""
        with app.app_context():
            # Clean up any existing test data first
            db.session.query(WeeklySurvey).filter(
                WeeklySurvey.registration_id.in_(
                    db.session.query(ModuleRegistration.registration_id).filter(
                        ModuleRegistration.student_id.in_(['CSV001', 'CSV002'])
                    )
                )
            ).delete(synchronize_session=False)
            db.session.query(ModuleRegistration).filter(
                ModuleRegistration.student_id.in_(['CSV001', 'CSV002'])
            ).delete(synchronize_session=False)
            db.session.query(Student).filter(
                Student.student_id.in_(['CSV001', 'CSV002'])
            ).delete(synchronize_session=False)
            db.session.query(Module).filter_by(module_id='CSVMOD001').delete()
            db.session.query(Course).filter_by(course_id='CSVCS101').delete()
            db.session.commit()
            
            # Create test course
            course = Course(
                course_id='CSVCS101',
                course_name='Computer Science',
                total_credits=180
            )
            db.session.add(course)
            
            # Create test module
            module = Module(
                module_id='CSVMOD001',
                course_id='CSVCS101',
                module_name='Introduction to Programming',
                duration_weeks=12
            )
            db.session.add(module)
            
            # Create test students
            student1 = Student(
                student_id='CSV001',
                first_name='John',
                last_name='Doe',
                email='john.csv@test.ac.uk',
                contact_no='07123456789',
                current_course_id='CSVCS101',
                enrolled_year=2024
            )
            
            student2 = Student(
                student_id='CSV002',
                first_name='Jane',
                last_name='Smith',
                email='jane.csv@test.ac.uk',
                contact_no='07987654321',
                current_course_id='CSVCS101',
                enrolled_year=2024
            )
            
            db.session.add_all([student1, student2])
            db.session.commit()
            
            # Create module registrations
            reg1 = ModuleRegistration(
                student_id='CSV001',
                module_id='CSVMOD001',
                status='Active'
            )
            
            reg2 = ModuleRegistration(
                student_id='CSV002',
                module_id='CSVMOD001',
                status='Active'
            )
            
            db.session.add_all([reg1, reg2])
            db.session.commit()
            
            yield
            
            # Cleanup
            db.session.query(WeeklySurvey).filter(
                WeeklySurvey.registration_id.in_(
                    db.session.query(ModuleRegistration.registration_id).filter(
                        ModuleRegistration.student_id.in_(['CSV001', 'CSV002'])
                    )
                )
            ).delete(synchronize_session=False)
            db.session.query(ModuleRegistration).filter(
                ModuleRegistration.student_id.in_(['CSV001', 'CSV002'])
            ).delete(synchronize_session=False)
            db.session.query(Student).filter(
                Student.student_id.in_(['CSV001', 'CSV002'])
            ).delete(synchronize_session=False)
            db.session.query(Module).filter_by(module_id='CSVMOD001').delete()
            db.session.query(Course).filter_by(course_id='CSVCS101').delete()
            db.session.commit()
    
    def test_csv_upload_success(self, client, setup_test_data):
        """Test successful CSV upload with valid data."""
        csv_content = """student_id,module_id,week,stress,sleep
CSV001,CSVMOD001,1,3,7.5
CSV002,CSVMOD001,1,4,6.0"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'test.csv')
        
        response = client.post(
            '/api/wellbeing/surveys/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['message'] == 'CSV upload completed'
        assert data['processed'] == 2
        assert data['skipped'] == 0
        assert data['details']['surveys_created_or_updated'] == 2
        
        # Verify surveys were created
        surveys = WeeklySurvey.query.filter(
            WeeklySurvey.registration_id.in_(
                db.session.query(ModuleRegistration.registration_id).filter(
                    ModuleRegistration.student_id.in_(['CSV001', 'CSV002'])
                )
            )
        ).all()
        assert len(surveys) == 2
    
    def test_csv_upload_skip_nonexistent_student(self, client, setup_test_data):
        """Test that non-existent students are skipped."""
        csv_content = """student_id,module_id,week,stress,sleep
CSV001,CSVMOD001,1,3,7.5
CSV999,CSVMOD001,1,5,4.0"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'test.csv')
        
        response = client.post(
            '/api/wellbeing/surveys/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['processed'] == 2
        assert data['skipped'] == 1
        assert any('CSV999' in str(item) for item in data['details']['students_not_found'])
        
        # Verify only one survey was created (for CSV001)
        surveys = WeeklySurvey.query.filter(
            WeeklySurvey.registration_id.in_(
                db.session.query(ModuleRegistration.registration_id).filter(
                    ModuleRegistration.student_id.in_(['CSV001', 'CSV002'])
                )
            )
        ).all()
        assert len(surveys) == 1
    
    def test_csv_upload_invalid_stress_level(self, client, setup_test_data):
        """Test validation of stress level (must be 1-5)."""
        csv_content = """student_id,module_id,week,stress,sleep
CSV001,CSVMOD001,1,10,7.5"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'test.csv')
        
        response = client.post(
            '/api/wellbeing/surveys/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Survey should not be created due to invalid stress level
        assert data['skipped'] == 1
        assert data['details']['surveys_created_or_updated'] == 0
        assert len(data['details']['invalid_rows']) > 0
        
        # Verify no surveys were created
        surveys = WeeklySurvey.query.filter(
            WeeklySurvey.registration_id.in_(
                db.session.query(ModuleRegistration.registration_id).filter(
                    ModuleRegistration.student_id.in_(['CSV001', 'CSV002'])
                )
            )
        ).all()
        assert len(surveys) == 0
    
    def test_csv_upload_invalid_sleep_hours(self, client, setup_test_data):
        """Test validation of sleep hours (must be 0-24)."""
        csv_content = """student_id,module_id,week,stress,sleep
CSV001,CSVMOD001,1,3,30.0"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'test.csv')
        
        response = client.post(
            '/api/wellbeing/surveys/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Survey should not be created due to invalid sleep hours
        assert data['skipped'] == 1
        assert data['details']['surveys_created_or_updated'] == 0
        
        # Verify no surveys were created
        surveys = WeeklySurvey.query.filter(
            WeeklySurvey.registration_id.in_(
                db.session.query(ModuleRegistration.registration_id).filter(
                    ModuleRegistration.student_id.in_(['CSV001', 'CSV002'])
                )
            )
        ).all()
        assert len(surveys) == 0
    
    def test_csv_upload_no_file(self, client, setup_test_data):
        """Test error when no file is provided."""
        response = client.post(
            '/api/wellbeing/surveys/csv-upload',
            data={},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'No file provided' in data['error']
    
    def test_csv_upload_invalid_headers(self, client, setup_test_data):
        """Test error when CSV has invalid headers."""
        csv_content = """student_id,name,stress,sleep
CSV001,John Doe,3,7.5"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'test.csv')
        
        response = client.post(
            '/api/wellbeing/surveys/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid CSV format' in data['error']
    
    def test_csv_upload_not_csv_file(self, client, setup_test_data):
        """Test error when file is not a CSV."""
        response = client.post(
            '/api/wellbeing/surveys/csv-upload',
            data={
                'file': (io.BytesIO(b'not csv content'), 'test.txt')
            },
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'must be a CSV file' in data['error']
    
    def test_csv_upload_multiple_weeks(self, client, setup_test_data):
        """Test CSV upload with multiple weeks for same student."""
        csv_content = """student_id,module_id,week,stress,sleep
CSV001,CSVMOD001,1,3,7.5
CSV001,CSVMOD001,2,4,6.0
CSV001,CSVMOD001,3,2,8.0"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'test.csv')
        
        response = client.post(
            '/api/wellbeing/surveys/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['processed'] == 3
        assert data['details']['surveys_created_or_updated'] == 3
        
        # Verify surveys have correct week numbers
        surveys = WeeklySurvey.query.filter(
            WeeklySurvey.registration_id.in_(
                db.session.query(ModuleRegistration.registration_id).filter(
                    ModuleRegistration.student_id == 'CSV001'
                )
            )
        ).order_by(WeeklySurvey.week_number).all()
        
        assert len(surveys) == 3
        assert surveys[0].week_number == 1
        assert surveys[0].stress_level == 3
        assert surveys[1].week_number == 2
        assert surveys[1].stress_level == 4
        assert surveys[2].week_number == 3
        assert surveys[2].stress_level == 2

