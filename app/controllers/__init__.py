"""
Controllers package.
Exports all controller modules for easy import.
"""
from app.controllers import course_controller
from app.controllers import student_controller
from app.controllers import survey_controller
from app.controllers import assignment_controller
from app.controllers import academic_controller
from app.controllers import auth_controller
from app.controllers import reports_controller

__all__ = [
    'course_controller',
    'student_controller',
    'survey_controller',
    'assignment_controller',
    'academic_controller',
    'auth_controller',
    'reports_controller'
]
