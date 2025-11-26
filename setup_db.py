"""
Database setup script to initialize the database and seed it with sample data.
Run this script to set up your local MySQL database for testing the API.
"""
import os
from app import create_app, db
from app.models import Course, Module, Student, ModuleRegistration, WeeklySurvey, Assignment, Submission, WeeklyAttendance
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Initialize database and seed with sample data."""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Check if data already exists
        if Course.query.first():
            print("Data already exists. Skipping seed.")
            return

        print("Seeding sample data...")
        
        # 1. Create Courses
        course1 = Course(course_id="C001", course_name="Computer Science", total_credits=120)
        course2 = Course(course_id="C002", course_name="Data Science", total_credits=120)
        db.session.add_all([course1, course2])
        
        # 2. Create Modules
        mod1 = Module(module_id="CS101", course_id="C001", module_name="Intro to Programming", duration_weeks=12)
        mod2 = Module(module_id="CS102", course_id="C001", module_name="Algorithms", duration_weeks=12)
        mod3 = Module(module_id="DS101", course_id="C002", module_name="Data Analysis", duration_weeks=12)
        db.session.add_all([mod1, mod2, mod3])
        
        # 3. Create Students
        student1 = Student(
            student_id="S001", first_name="John", last_name="Doe", 
            email="john@example.com", enrolled_year=2024, current_course_id="C001"
        )
        student2 = Student(
            student_id="S002", first_name="Jane", last_name="Smith", 
            email="jane@example.com", enrolled_year=2024, current_course_id="C002"
        )
        db.session.add_all([student1, student2])
        db.session.commit()  # Commit to get IDs
        
        # 4. Create Registrations
        reg1 = ModuleRegistration(student_id="S001", module_id="CS101", status="Active", start_date=date(2025, 1, 10))
        reg2 = ModuleRegistration(student_id="S001", module_id="CS102", status="Active", start_date=date(2025, 1, 10))
        reg3 = ModuleRegistration(student_id="S002", module_id="DS101", status="Active", start_date=date(2025, 1, 10))
        db.session.add_all([reg1, reg2, reg3])
        db.session.commit()
        
        # 5. Create Assignments
        assign1 = Assignment(
            assignment_id="A001", module_id="CS101", title="Python Basics", 
            description="Complete exercises 1-10", due_date=datetime.now() + timedelta(days=7),
            max_score=100, weightage_percent=20.0
        )
        db.session.add(assign1)
        
        # 6. Create Submissions
        sub1 = Submission(
            registration_id=reg1.registration_id, assignment_id="A001",
            submitted_at=datetime.now(), grade_achieved=85.5, grader_feedback="Good job!"
        )
        db.session.add(sub1)
        
        # 7. Create Surveys
        survey1 = WeeklySurvey(
            registration_id=reg1.registration_id, week_number=1,
            stress_level=3, sleep_hours=7.5, social_connection_score=4, comments="Good week"
        )
        db.session.add(survey1)
        
        # 8. Create Attendance
        att1 = WeeklyAttendance(
            registration_id=reg1.registration_id, week_number=1,
            class_date=date(2025, 1, 15), is_present=True
        )
        db.session.add(att1)
        
        db.session.commit()
        print("Database setup complete! Sample data created.")

if __name__ == "__main__":
    setup_database()
