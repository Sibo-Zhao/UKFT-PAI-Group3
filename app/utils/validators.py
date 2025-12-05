"""
Input Validation Utilities.

This module provides validation schemas and helper functions for
validating incoming request data.
"""
import re
from marshmallow import Schema, fields, validates, ValidationError

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


class LoginSchema(Schema):
    """Schema for login request validation."""
    username = fields.Str(required=True, error_messages={
        "required": "Username is required"
    })
    password = fields.Str(required=True, error_messages={
        "required": "Password is required"
    })


class StudentUpdateSchema(Schema):
    """Schema for student update request validation."""
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email(error_messages={
        "invalid": "Invalid email format"
    })
    enrolled_year = fields.Int()
    current_course_id = fields.Str()
    
    @validates('enrolled_year')
    def validate_enrolled_year(self, value):
        """Validate enrolled year is reasonable."""
        if value < 1900 or value > 2100:
            raise ValidationError("Enrolled year must be between 1900 and 2100")


class AssignmentCreateSchema(Schema):
    """Schema for assignment creation validation."""
    assignment_id = fields.Str(required=True)
    module_id = fields.Str(required=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    due_date = fields.DateTime(required=True)
    max_score = fields.Int(missing=100)
    weightage_percent = fields.Float(allow_none=True)
    
    @validates('max_score')
    def validate_max_score(self, value):
        """Validate max score is positive."""
        if value <= 0:
            raise ValidationError("Max score must be positive")
    
    @validates('weightage_percent')
    def validate_weightage(self, value):
        """Validate weightage is between 0 and 100."""
        if value is not None and (value < 0 or value > 100):
            raise ValidationError("Weightage must be between 0 and 100")


class AssignmentUpdateSchema(Schema):
    """Schema for assignment update validation."""
    title = fields.Str()
    description = fields.Str(allow_none=True)
    due_date = fields.DateTime()
    max_score = fields.Int()
    weightage_percent = fields.Float(allow_none=True)
    
    @validates('max_score')
    def validate_max_score(self, value):
        """Validate max score is positive."""
        if value <= 0:
            raise ValidationError("Max score must be positive")
    
    @validates('weightage_percent')
    def validate_weightage(self, value):
        """Validate weightage is between 0 and 100."""
        if value is not None and (value < 0 or value > 100):
            raise ValidationError("Weightage must be between 0 and 100")


class SurveyBulkUploadSchema(Schema):
    """Schema for bulk survey upload validation."""
    surveys = fields.List(fields.Dict(), required=True)


class AttendanceBulkUploadSchema(Schema):
    """Schema for bulk attendance upload validation."""
    attendance_records = fields.List(fields.Dict(), required=True)


class GradeBulkUploadSchema(Schema):
    """Schema for bulk grade upload validation."""
    grades = fields.List(fields.Dict(), required=True)


class ModuleCreateSchema(Schema):
    """Schema for module creation validation."""
    module_id = fields.Str(required=True)
    course_id = fields.Str(required=True)
    module_name = fields.Str(required=True)
    duration_weeks = fields.Int(missing=12)
    
    @validates('duration_weeks')
    def validate_duration(self, value):
        """Validate duration is positive."""
        if value <= 0:
            raise ValidationError("Duration must be positive")


class ModuleUpdateSchema(Schema):
    """Schema for module update validation."""
    module_name = fields.Str()
    duration_weeks = fields.Int()
    course_id = fields.Str()
    
    @validates('duration_weeks')
    def validate_duration(self, value):
        """Validate duration is positive."""
        if value <= 0:
            raise ValidationError("Duration must be positive")


class ModuleRegistrationSchema(Schema):
    """Schema for module registration validation."""
    student_id = fields.Str(required=True)
    module_id = fields.Str(required=True)
    status = fields.Str(missing='Active')
    start_date = fields.Date()
    
    @validates('status')
    def validate_status(self, value):
        """Validate registration status."""
        valid_statuses = ['Active', 'Completed', 'Withdrawn']
        if value not in valid_statuses:
            raise ValidationError(f"Status must be one of: {', '.join(valid_statuses)}")


class AttendanceRecordSchema(Schema):
    """Schema for attendance record validation."""
    registration_id = fields.Int(required=True)
    week_number = fields.Int(required=True)
    class_date = fields.Date(required=True)
    is_present = fields.Bool(required=True)
    reason_absent = fields.Str(allow_none=True)
    
    @validates('week_number')
    def validate_week_number(self, value):
        """Validate week number is positive."""
        if value <= 0:
            raise ValidationError("Week number must be positive")


class SubmissionCreateSchema(Schema):
    """Schema for submission creation validation."""
    registration_id = fields.Int(required=True)
    assignment_id = fields.Str(required=True)
    submitted_at = fields.DateTime()
    grade_achieved = fields.Float(allow_none=True)
    grader_feedback = fields.Str(allow_none=True)
    
    @validates('grade_achieved')
    def validate_grade(self, value):
        """Validate grade is non-negative."""
        if value is not None and value < 0:
            raise ValidationError("Grade cannot be negative")


class SubmissionGradeSchema(Schema):
    """Schema for submission grading validation."""
    grade_achieved = fields.Float(required=True)
    grader_feedback = fields.Str(allow_none=True)
    
    @validates('grade_achieved')
    def validate_grade(self, value):
        """Validate grade is non-negative."""
        if value < 0:
            raise ValidationError("Grade cannot be negative")


class WeeklySurveySchema(Schema):
    """Schema for weekly survey validation."""
    registration_id = fields.Int(required=True)
    week_number = fields.Int(required=True)
    stress_level = fields.Int(allow_none=True)
    sleep_hours = fields.Float(allow_none=True)
    social_connection_score = fields.Int(allow_none=True)
    comments = fields.Str(allow_none=True)
    
    @validates('stress_level')
    def validate_stress_level(self, value):
        """Validate stress level is between 1 and 5."""
        if value is not None and (value < 1 or value > 5):
            raise ValidationError("Stress level must be between 1 and 5")
    
    @validates('social_connection_score')
    def validate_social_score(self, value):
        """Validate social connection score is between 1 and 5."""
        if value is not None and (value < 1 or value > 5):
            raise ValidationError("Social connection score must be between 1 and 5")
    
    @validates('sleep_hours')
    def validate_sleep_hours(self, value):
        """Validate sleep hours is reasonable."""
        if value is not None and (value < 0 or value > 24):
            raise ValidationError("Sleep hours must be between 0 and 24")
    
    @validates('week_number')
    def validate_week_number(self, value):
        """Validate week number is positive."""
        if value <= 0:
            raise ValidationError("Week number must be positive")


class StudentAnalyticsFilterSchema(Schema):
    """Schema for student analytics filter validation."""
    module_id = fields.Str(allow_none=True)
    week_start = fields.Int(allow_none=True)
    week_end = fields.Int(allow_none=True)
    assignment_type = fields.Str(allow_none=True)
    
    @validates('week_start')
    def validate_week_start(self, value):
        """Validate week start is positive."""
        if value is not None and value <= 0:
            raise ValidationError("Week start must be positive")
    
    @validates('week_end')
    def validate_week_end(self, value):
        """Validate week end is positive."""
        if value is not None and value <= 0:
            raise ValidationError("Week end must be positive")


class CourseComparisonSchema(Schema):
    """Schema for course student comparison validation."""
    metric = fields.Str(missing='attendance')
    week_start = fields.Int(allow_none=True)
    week_end = fields.Int(allow_none=True)
    
    @validates('metric')
    def validate_metric(self, value):
        """Validate comparison metric."""
        valid_metrics = ['attendance', 'grades', 'wellbeing', 'submissions', 'all']
        if value not in valid_metrics:
            raise ValidationError(f"Metric must be one of: {', '.join(valid_metrics)}")
    
    @validates('week_start')
    def validate_week_start(self, value):
        """Validate week start is positive."""
        if value is not None and value <= 0:
            raise ValidationError("Week start must be positive")
    
    @validates('week_end')
    def validate_week_end(self, value):
        """Validate week end is positive."""
        if value is not None and value <= 0:
            raise ValidationError("Week end must be positive")


def validate_email(email):
    """
    Validate email format using regex.
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email))


def validate_request_data(schema_class, data):
    """
    Validate request data against a schema.
    
    Args:
        schema_class: Marshmallow schema class
        data: Data to validate
    
    Returns:
        tuple: (validated_data, errors)
            - validated_data: Validated and deserialized data (None if errors)
            - errors: Validation errors (None if valid)
    """
    schema = schema_class()
    try:
        validated_data = schema.load(data)
        return validated_data, None
    except ValidationError as e:
        return None, e.messages
