"""
Flask-SQLAlchemy ORM Models.

This module defines all database models for the University Wellbeing API,
matching the uni_wellbeing.sql schema. Models include courses, modules,
students, registrations, surveys, assignments, submissions, and attendance.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()


class Course(db.Model):
    """
    Course model representing academic courses.
    
    Maps to the 'courses' table in the database. A course contains multiple
    modules and can have multiple students enrolled.
    
    Attributes:
        course_id (str): Primary key, unique course identifier (max 20 chars).
        course_name (str): Name of the course (max 100 chars).
        total_credits (int): Total credit hours for the course (default: 180).
        created_at (datetime): Timestamp when the course was created.
    
    Relationships:
        modules (list[Module]): All modules belonging to this course.
        students (list[Student]): All students enrolled in this course.
    """
    __tablename__ = "courses"
    
    course_id = db.Column(db.String(20), primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    total_credits = db.Column(db.Integer, default=180)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationships
    modules = db.relationship("Module", back_populates="course")
    students = db.relationship("Student", back_populates="course")


class Module(db.Model):
    """
    Module model representing course modules.
    
    Maps to the 'modules' table. A module is a component of a course and
    contains assignments. Students register for modules.
    
    Attributes:
        module_id (str): Primary key, unique module identifier (max 20 chars).
        course_id (str): Foreign key to courses table (SET NULL on delete).
        module_name (str): Name of the module (max 100 chars).
        duration_weeks (int): Duration of the module in weeks (default: 12).
    
    Relationships:
        course (Course): The course this module belongs to.
        registrations (list[ModuleRegistration]): Student registrations for this module.
        assignments (list[Assignment]): All assignments in this module.
    """
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
    """
    Student model representing enrolled students.
    
    Maps to the 'students' table. Students enroll in courses and register
    for modules.
    
    Attributes:
        student_id (str): Primary key, unique student identifier (max 20 chars).
        first_name (str): Student's first name (max 50 chars).
        last_name (str): Student's last name (max 50 chars).
        email (str): Student's email address, must be unique (max 100 chars).
        contact_no (str): Student's contact number (max 20 chars, optional).
        enrolled_year (int): Year the student enrolled (optional).
        current_course_id (str): Foreign key to current course (SET NULL on delete).
    
    Relationships:
        course (Course): The course the student is currently enrolled in.
        registrations (list[ModuleRegistration]): All module registrations for this student.
    """
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
    """
    Module registration model linking students to modules.
    
    Maps to the 'module_registrations' table. Represents a student's enrollment
    in a specific module. This is the central linking table for tracking student
    progress, surveys, and attendance.
    
    Attributes:
        registration_id (int): Primary key, auto-incrementing identifier.
        student_id (str): Foreign key to students table (CASCADE on delete).
        module_id (str): Foreign key to modules table (CASCADE on delete).
        status (str): Registration status (default: 'Active', max 20 chars).
        start_date (date): Date when the student started the module (optional).
    
    Relationships:
        student (Student): The student who registered.
        module (Module): The module the student registered for.
        weekly_surveys (list[WeeklySurvey]): All survey responses for this registration.
    """
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
    """
    Weekly survey model for student wellbeing data.
    
    Maps to the 'weekly_surveys' table. Stores weekly wellbeing survey responses
    including stress levels, sleep hours, and social connection scores.
    
    Attributes:
        survey_id (int): Primary key, auto-incrementing identifier.
        registration_id (int): Foreign key to module_registrations (CASCADE on delete).
        week_number (int): Week number of the survey (must be positive).
        submitted_at (datetime): Timestamp when survey was submitted.
        stress_level (int): Stress level rating (1-5 scale, optional).
        sleep_hours (float): Hours of sleep reported (optional).
        social_connection_score (int): Social connection rating (1-5 scale, optional).
        comments (text): Additional comments from student (optional).
    
    Relationships:
        registration (ModuleRegistration): The module registration this survey belongs to.
    
    Note:
        Database CHECK constraints enforce stress_level and social_connection_score
        to be between 1 and 5, though this is not enforced at the ORM level.
    """
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
    """
    Assignment model representing course assignments.
    
    Maps to the 'assignments' table. Assignments belong to modules and can
    have multiple student submissions.
    
    Attributes:
        assignment_id (str): Primary key, unique assignment identifier (max 20 chars).
        module_id (str): Foreign key to modules table (CASCADE on delete).
        title (str): Assignment title (max 100 chars).
        description (text): Detailed assignment description (optional).
        due_date (datetime): Deadline for assignment submission.
        max_score (int): Maximum achievable score (default: 100).
        weightage_percent (float): Percentage weight in final grade (optional).
    
    Relationships:
        module (Module): The module this assignment belongs to.
        submissions (list[Submission]): All student submissions for this assignment.
    """
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
    """
    Submission model representing student assignment submissions.
    
    Maps to the 'submissions' table. Tracks when students submit assignments
    and stores their grades and feedback.
    
    Attributes:
        submission_id (int): Primary key, auto-incrementing identifier.
        registration_id (int): Foreign key to module_registrations (CASCADE on delete).
        assignment_id (str): Foreign key to assignments table (CASCADE on delete).
        submitted_at (datetime): Timestamp when submission was made (optional).
        grade_achieved (float): Grade received for the submission (optional).
        grader_feedback (text): Feedback from grader (optional).
    
    Relationships:
        registration (ModuleRegistration): The module registration this submission belongs to.
        assignment (Assignment): The assignment this is a submission for.
    """
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
    """
    Weekly attendance model for tracking student attendance.
    
    Maps to the 'weekly_attendance' table. Records whether students attended
    classes each week and reasons for absences.
    
    Attributes:
        attendance_id (int): Primary key, auto-incrementing identifier.
        registration_id (int): Foreign key to module_registrations (CASCADE on delete).
        week_number (int): Week number of the attendance record.
        class_date (date): Date of the class.
        is_present (bool): Whether the student was present (default: False).
        reason_absent (str): Reason for absence if not present (max 255 chars, optional).
    
    Relationships:
        registration (ModuleRegistration): The module registration this attendance belongs to.
    """
    __tablename__ = "weekly_attendance"
    
    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    registration_id = db.Column(db.Integer, db.ForeignKey("module_registrations.registration_id", ondelete="CASCADE"), nullable=False)
    week_number = db.Column(db.Integer, nullable=False)
    class_date = db.Column(db.Date, nullable=False)
    is_present = db.Column(db.Boolean, nullable=False, default=False)
    reason_absent = db.Column(db.String(255))
    
    # Relationships
    registration = db.relationship("ModuleRegistration")
