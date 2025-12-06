"""
Test CSV Upload for SWO Surveys.

This module tests the CSV upload functionality for Student Wellbeing Officer surveys,
including validation, student updates, and survey creation.
"""
import pytest
import io
from datetime import datetime
from app.models import Student, WeeklySurvey, ModuleRegistration, Course, Module, Assignment, Submission, WeeklyAttendance, db


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


class TestAttendanceCSVUpload:
    """Test suite for CSV upload of attendance records."""
    
    @pytest.fixture
    def setup_attendance_data(self, app):
        """Create test data for attendance CSV upload tests."""
        with app.app_context():
            # Clean up any existing test data
            db.session.query(WeeklyAttendance).filter(
                WeeklyAttendance.registration_id.in_(
                    db.session.query(ModuleRegistration.registration_id).filter(
                        ModuleRegistration.student_id.in_(['ATT001', 'ATT002'])
                    )
                )
            ).delete(synchronize_session=False)
            db.session.query(ModuleRegistration).filter(
                ModuleRegistration.student_id.in_(['ATT001', 'ATT002'])
            ).delete(synchronize_session=False)
            db.session.query(Student).filter(
                Student.student_id.in_(['ATT001', 'ATT002'])
            ).delete(synchronize_session=False)
            db.session.query(Module).filter_by(module_id='ATTMOD001').delete()
            db.session.query(Course).filter_by(course_id='ATTCS101').delete()
            db.session.commit()
            
            # Create test course and module
            course = Course(
                course_id='ATTCS101',
                course_name='Attendance Test Course',
                total_credits=180
            )
            db.session.add(course)
            
            module = Module(
                module_id='ATTMOD001',
                course_id='ATTCS101',
                module_name='Test Module',
                duration_weeks=12
            )
            db.session.add(module)
            
            # Create test students
            student1 = Student(
                student_id='ATT001',
                first_name='Alice',
                last_name='Test',
                email='alice.att@test.ac.uk',
                current_course_id='ATTCS101',
                enrolled_year=2024
            )
            
            student2 = Student(
                student_id='ATT002',
                first_name='Bob',
                last_name='Test',
                email='bob.att@test.ac.uk',
                current_course_id='ATTCS101',
                enrolled_year=2024
            )
            
            db.session.add_all([student1, student2])
            db.session.commit()
            
            # Create module registrations
            reg1 = ModuleRegistration(
                student_id='ATT001',
                module_id='ATTMOD001',
                status='Active'
            )
            
            reg2 = ModuleRegistration(
                student_id='ATT002',
                module_id='ATTMOD001',
                status='Active'
            )
            
            db.session.add_all([reg1, reg2])
            db.session.commit()
            
            # Store registration IDs for tests
            self.reg1_id = reg1.registration_id
            self.reg2_id = reg2.registration_id
            
            yield
            
            # Cleanup
            db.session.query(WeeklyAttendance).filter(
                WeeklyAttendance.registration_id.in_([self.reg1_id, self.reg2_id])
            ).delete(synchronize_session=False)
            db.session.query(ModuleRegistration).filter(
                ModuleRegistration.student_id.in_(['ATT001', 'ATT002'])
            ).delete(synchronize_session=False)
            db.session.query(Student).filter(
                Student.student_id.in_(['ATT001', 'ATT002'])
            ).delete(synchronize_session=False)
            db.session.query(Module).filter_by(module_id='ATTMOD001').delete()
            db.session.query(Course).filter_by(course_id='ATTCS101').delete()
            db.session.commit()
    
    def test_attendance_csv_upload_success(self, client, setup_attendance_data):
        """Test successful attendance CSV upload with valid data."""
        csv_content = f"""registration_id,week,is_present,reason_absent
{self.reg1_id},1,true,
{self.reg1_id},2,false,Sick
{self.reg2_id},1,true,"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'attendance.csv')
        
        response = client.post(
            '/academic/attendance/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['message'] == 'CSV upload completed'
        assert data['processed'] == 3
        assert data['created'] == 3
        assert data['skipped'] == 0
        
        # Verify attendance records were created
        attendance = WeeklyAttendance.query.filter(
            WeeklyAttendance.registration_id.in_([self.reg1_id, self.reg2_id])
        ).all()
        assert len(attendance) == 3
    
    def test_attendance_csv_update_existing(self, client, setup_attendance_data):
        """Test updating existing attendance records."""
        # First create an attendance record
        attendance = WeeklyAttendance(
            registration_id=self.reg1_id,
            week_number=1,
            class_date=datetime.now().date(),
            is_present=True
        )
        db.session.add(attendance)
        db.session.commit()
        
        # Now update it via CSV
        csv_content = f"""registration_id,week,is_present,reason_absent
{self.reg1_id},1,false,Changed to absent"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'attendance.csv')
        
        response = client.post(
            '/academic/attendance/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['created'] == 1
        
        # Verify it was updated
        updated = WeeklyAttendance.query.filter_by(
            registration_id=self.reg1_id,
            week_number=1
        ).first()
        assert updated.is_present == False
        assert updated.reason_absent == 'Changed to absent'
    
    def test_attendance_csv_invalid_registration(self, client, setup_attendance_data):
        """Test handling of invalid registration IDs."""
        csv_content = """registration_id,week,is_present,reason_absent
99999,1,true,"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'attendance.csv')
        
        response = client.post(
            '/academic/attendance/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['skipped'] == 1
        assert data['created'] == 0
        assert 'Registration ID 99999' in str(data['details']['registrations_not_found'])
    
    def test_attendance_csv_invalid_is_present(self, client, setup_attendance_data):
        """Test validation of is_present field."""
        csv_content = f"""registration_id,week,is_present,reason_absent
{self.reg1_id},1,maybe,"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'attendance.csv')
        
        response = client.post(
            '/academic/attendance/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['skipped'] == 1
        assert len(data['details']['invalid_rows']) > 0
    
    def test_attendance_csv_missing_headers(self, client, setup_attendance_data):
        """Test error when required headers are missing."""
        csv_content = """registration_id,week
1,1"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'attendance.csv')
        
        response = client.post(
            '/academic/attendance/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid CSV format' in data['error']
    
    def test_attendance_csv_no_file(self, client, setup_attendance_data):
        """Test error when no file is provided."""
        response = client.post(
            '/academic/attendance/csv-upload',
            data={},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'No file provided' in data['error']
    
    def test_attendance_csv_not_csv_file(self, client, setup_attendance_data):
        """Test error when file is not a CSV."""
        response = client.post(
            '/academic/attendance/csv-upload',
            data={
                'file': (io.BytesIO(b'not csv'), 'test.txt')
            },
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'must be a CSV file' in data['error']


class TestGradesCSVUpload:
    """Test suite for CSV upload of grades."""
    
    @pytest.fixture
    def setup_grades_data(self, app):
        """Create test data for grades CSV upload tests."""
        with app.app_context():
            # Clean up any existing test data
            db.session.query(Submission).filter(
                Submission.registration_id.in_(
                    db.session.query(ModuleRegistration.registration_id).filter(
                        ModuleRegistration.student_id.in_(['GRD001', 'GRD002'])
                    )
                )
            ).delete(synchronize_session=False)
            db.session.query(Assignment).filter(
                Assignment.assignment_id.in_(['GRDA001', 'GRDA002'])
            ).delete(synchronize_session=False)
            db.session.query(ModuleRegistration).filter(
                ModuleRegistration.student_id.in_(['GRD001', 'GRD002'])
            ).delete(synchronize_session=False)
            db.session.query(Student).filter(
                Student.student_id.in_(['GRD001', 'GRD002'])
            ).delete(synchronize_session=False)
            db.session.query(Module).filter_by(module_id='GRDMOD001').delete()
            db.session.query(Course).filter_by(course_id='GRDCS101').delete()
            db.session.commit()
            
            # Create test course and module
            course = Course(
                course_id='GRDCS101',
                course_name='Grades Test Course',
                total_credits=180
            )
            db.session.add(course)
            
            module = Module(
                module_id='GRDMOD001',
                course_id='GRDCS101',
                module_name='Test Module',
                duration_weeks=12
            )
            db.session.add(module)
            
            # Create test students
            student1 = Student(
                student_id='GRD001',
                first_name='Charlie',
                last_name='Test',
                email='charlie.grd@test.ac.uk',
                current_course_id='GRDCS101',
                enrolled_year=2024
            )
            
            student2 = Student(
                student_id='GRD002',
                first_name='Diana',
                last_name='Test',
                email='diana.grd@test.ac.uk',
                current_course_id='GRDCS101',
                enrolled_year=2024
            )
            
            db.session.add_all([student1, student2])
            db.session.commit()
            
            # Create module registrations
            reg1 = ModuleRegistration(
                student_id='GRD001',
                module_id='GRDMOD001',
                status='Active'
            )
            
            reg2 = ModuleRegistration(
                student_id='GRD002',
                module_id='GRDMOD001',
                status='Active'
            )
            
            db.session.add_all([reg1, reg2])
            db.session.commit()
            
            # Create test assignments
            assignment1 = Assignment(
                assignment_id='GRDA001',
                module_id='GRDMOD001',
                title='Test Assignment 1',
                due_date=datetime.now(),
                max_score=100
            )
            
            assignment2 = Assignment(
                assignment_id='GRDA002',
                module_id='GRDMOD001',
                title='Test Assignment 2',
                due_date=datetime.now(),
                max_score=50
            )
            
            db.session.add_all([assignment1, assignment2])
            db.session.commit()
            
            # Store IDs for tests
            self.reg1_id = reg1.registration_id
            self.reg2_id = reg2.registration_id
            
            yield
            
            # Cleanup
            db.session.query(Submission).filter(
                Submission.registration_id.in_([self.reg1_id, self.reg2_id])
            ).delete(synchronize_session=False)
            db.session.query(Assignment).filter(
                Assignment.assignment_id.in_(['GRDA001', 'GRDA002'])
            ).delete(synchronize_session=False)
            db.session.query(ModuleRegistration).filter(
                ModuleRegistration.student_id.in_(['GRD001', 'GRD002'])
            ).delete(synchronize_session=False)
            db.session.query(Student).filter(
                Student.student_id.in_(['GRD001', 'GRD002'])
            ).delete(synchronize_session=False)
            db.session.query(Module).filter_by(module_id='GRDMOD001').delete()
            db.session.query(Course).filter_by(course_id='GRDCS101').delete()
            db.session.commit()
    
    def test_grades_csv_upload_success(self, client, setup_grades_data):
        """Test successful grades CSV upload with valid data."""
        csv_content = f"""registration_id,assignment_id,grade
{self.reg1_id},GRDA001,85.5
{self.reg1_id},GRDA002,42.0
{self.reg2_id},GRDA001,92.0"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'grades.csv')
        
        response = client.post(
            '/academic/grades/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['message'] == 'CSV upload completed'
        assert data['processed'] == 3
        assert data['updated'] == 3
        assert data['skipped'] == 0
        
        # Verify submissions were created
        submissions = Submission.query.filter(
            Submission.registration_id.in_([self.reg1_id, self.reg2_id])
        ).all()
        assert len(submissions) == 3
    
    def test_grades_csv_update_existing(self, client, setup_grades_data):
        """Test updating existing grade."""
        # First create a submission
        submission = Submission(
            registration_id=self.reg1_id,
            assignment_id='GRDA001',
            submitted_at=datetime.now(),
            grade_achieved=70.0
        )
        db.session.add(submission)
        db.session.commit()
        
        # Now update it via CSV
        csv_content = f"""registration_id,assignment_id,grade
{self.reg1_id},GRDA001,95.0"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'grades.csv')
        
        response = client.post(
            '/academic/grades/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['updated'] == 1
        
        # Verify it was updated
        updated = Submission.query.filter_by(
            registration_id=self.reg1_id,
            assignment_id='GRDA001'
        ).first()
        assert updated.grade_achieved == 95.0
    
    def test_grades_csv_invalid_assignment(self, client, setup_grades_data):
        """Test handling of invalid assignment IDs."""
        csv_content = f"""registration_id,assignment_id,grade
{self.reg1_id},INVALID999,85.0"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'grades.csv')
        
        response = client.post(
            '/academic/grades/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['skipped'] == 1
        assert data['updated'] == 0
        assert 'INVALID999 not found' in str(data['details']['invalid_rows'])
    
    def test_grades_csv_exceeds_max_score(self, client, setup_grades_data):
        """Test validation of grade exceeding max score."""
        csv_content = f"""registration_id,assignment_id,grade
{self.reg1_id},GRDA002,60.0"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'grades.csv')
        
        response = client.post(
            '/academic/grades/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['skipped'] == 1
        assert 'exceeds max score' in str(data['details']['invalid_rows'])
    
    def test_grades_csv_negative_grade(self, client, setup_grades_data):
        """Test validation of negative grades."""
        csv_content = f"""registration_id,assignment_id,grade
{self.reg1_id},GRDA001,-10.0"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'grades.csv')
        
        response = client.post(
            '/academic/grades/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['skipped'] == 1
        assert 'cannot be negative' in str(data['details']['invalid_rows'])
    
    def test_grades_csv_invalid_registration(self, client, setup_grades_data):
        """Test handling of invalid registration IDs."""
        csv_content = """registration_id,assignment_id,grade
99999,GRDA001,85.0"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'grades.csv')
        
        response = client.post(
            '/academic/grades/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['skipped'] == 1
        assert 'Registration ID 99999' in str(data['details']['registrations_not_found'])
    
    def test_grades_csv_missing_headers(self, client, setup_grades_data):
        """Test error when required headers are missing."""
        csv_content = """registration_id,grade
1,85.0"""
        
        csv_file = (io.BytesIO(csv_content.encode('utf-8')), 'grades.csv')
        
        response = client.post(
            '/academic/grades/csv-upload',
            data={'file': csv_file},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid CSV format' in data['error']
    
    def test_grades_csv_no_file(self, client, setup_grades_data):
        """Test error when no file is provided."""
        response = client.post(
            '/academic/grades/csv-upload',
            data={},
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'No file provided' in data['error']

