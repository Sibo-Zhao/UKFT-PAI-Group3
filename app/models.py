"""
Flask-SQLAlchemy ORM models matching the uni_wellbeing.sql schema.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class Course(db.Model):
    """Course model mapping to courses table."""
    __tablename__ = "courses"
    
    course_id = db.Column(db.String(20), primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    total_credits = db.Column(db.Integer, default=180)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationships
    modules = db.relationship("Module", back_populates="course")
    students = db.relationship("Student", back_populates="course")


class Module(db.Model):
    """Module model mapping to modules table."""
    __tablename__ = "modules"
    
    module_id = db.Column(db.String(20), primary_key=True)
    course_id = db.Column(db.String(20), db.ForeignKey("courses.course_id", ondelete="SET NULL"))
    module_name = db.Column(db.String(100), nullable=False)
    duration_weeks = db.Column(db.Integer, default=12)
    
    # Relationships
    course = db.relationship("Course", back_populates="modules")
    registrations = db.relationship("ModuleRegistration", back_populates="module")
    assignments = db.relationship("Assignment", back_populates="module")


class Student(db.Model):
    """Student model mapping to students table."""
    __tablename__ = "students"
    
    student_id = db.Column(db.String(20), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contact_no = db.Column(db.String(20))
    enrolled_year = db.Column(db.Integer)
    current_course_id = db.Column(db.String(20), db.ForeignKey("courses.course_id", ondelete="SET NULL"))
    
    # Relationships
    course = db.relationship("Course", back_populates="students")
    registrations = db.relationship("ModuleRegistration", back_populates="student")


class ModuleRegistration(db.Model):
    """Module registration model mapping to module_registrations table."""
    __tablename__ = "module_registrations"
    
    registration_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(20), db.ForeignKey("students.student_id", ondelete="CASCADE"), nullable=False)
    module_id = db.Column(db.String(20), db.ForeignKey("modules.module_id", ondelete="CASCADE"), nullable=False)
    status = db.Column(db.String(20), default='Active')  # Simplified for SQLite compatibility
    start_date = db.Column(db.Date)
    
    # Relationships
    student = db.relationship("Student", back_populates="registrations")
    module = db.relationship("Module", back_populates="registrations")
    weekly_surveys = db.relationship("WeeklySurvey", back_populates="registration")


class WeeklySurvey(db.Model):
    """Weekly survey model mapping to weekly_surveys table."""
    __tablename__ = "weekly_surveys"
    
    survey_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registration_id = db.Column(db.Integer, db.ForeignKey("module_registrations.registration_id", ondelete="CASCADE"), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, server_default=func.current_timestamp())
    stress_level = db.Column(db.Integer, nullable=True)  # CHECK constraint: 1-5
    sleep_hours = db.Column(db.Float)
    social_connection_score = db.Column(db.Integer, nullable=True)  # CHECK constraint: 1-5
    comments = db.Column(db.Text)
    
    # Relationships
    registration = db.relationship("ModuleRegistration", back_populates="weekly_surveys")


class Assignment(db.Model):
    """Assignment model mapping to assignments table."""
    __tablename__ = "assignments"
    
    assignment_id = db.Column(db.String(20), primary_key=True)
    module_id = db.Column(db.String(20), db.ForeignKey("modules.module_id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    max_score = db.Column(db.Integer, default=100)
    weightage_percent = db.Column(db.Float)
    
    # Relationships
    module = db.relationship("Module", back_populates="assignments")
    submissions = db.relationship("Submission", back_populates="assignment")


class Submission(db.Model):
    """Submission model mapping to submissions table."""
    __tablename__ = "submissions"
    
    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registration_id = db.Column(db.Integer, db.ForeignKey("module_registrations.registration_id", ondelete="CASCADE"), nullable=False)
    assignment_id = db.Column(db.String(20), db.ForeignKey("assignments.assignment_id", ondelete="CASCADE"), nullable=False)
    submitted_at = db.Column(db.DateTime)
    grade_achieved = db.Column(db.Float)
    grader_feedback = db.Column(db.Text)
    
    # Relationships
    registration = db.relationship("ModuleRegistration")
    assignment = db.relationship("Assignment", back_populates="submissions")


class WeeklyAttendance(db.Model):
    """Weekly attendance model mapping to weekly_attendance table."""
    __tablename__ = "weekly_attendance"
    
    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registration_id = db.Column(db.Integer, db.ForeignKey("module_registrations.registration_id", ondelete="CASCADE"), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    class_date = db.Column(db.Date, nullable=False)
    is_present = db.Column(db.Boolean, nullable=False, default=False)
    reason_absent = db.Column(db.String(255))
    
    # Relationships
    registration = db.relationship("ModuleRegistration")
