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
