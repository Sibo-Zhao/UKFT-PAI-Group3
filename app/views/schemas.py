"""
Marshmallow schemas for serialization and validation.
"""
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate

ma = Marshmallow()

class StudentSchema(ma.Schema):
    """Schema for student serialization."""
    
    student_id = fields.Str(required=True)
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Str(required=True)
    contact_no = fields.Str(allow_none=True)
    enrolled_year = fields.Int()
    current_course_id = fields.Str(allow_none=True)
    
    class Meta:
        ordered = True

# Create schema instances
student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

class WeeklySurveySchema(ma.Schema):
    """Schema for weekly survey serialization."""
    
    survey_id = fields.Int(dump_only=True)
    registration_id = fields.Int(required=True)
    week_number = fields.Int(required=True, validate=validate.Range(min=1))
    submitted_at = fields.DateTime(dump_only=True)
    stress_level = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=5, error="Stress level must be between 1 and 5")
    )
    sleep_hours = fields.Float(
        required=True,
        as_string=False,
        validate=validate.Range(min=0, max=24, error="Sleep hours must be between 0 and 24")
    )
    social_connection_score = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=5, error="Social connection score must be between 1 and 5")
    )
    comments = fields.Str(allow_none=True)
    
    class Meta:
        ordered = True


class CourseSchema(ma.Schema):
    """Schema for course serialization."""
    
    course_id = fields.Str(required=True)
    course_name = fields.Str(required=True)
    total_credits = fields.Int()
    created_at = fields.DateTime(dump_only=True)
    
    class Meta:
        ordered = True


class ModuleSchema(ma.Schema):
    """Schema for module serialization."""
    
    module_id = fields.Str(required=True)
    course_id = fields.Str(required=True)
    module_name = fields.Str(required=True)
    duration_weeks = fields.Int()
    
    class Meta:
        ordered = True


class AssignmentSchema(ma.Schema):
    """Schema for assignment serialization."""
    
    assignment_id = fields.Str(required=True)
    module_id = fields.Str(required=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    due_date = fields.DateTime(required=True)
    max_score = fields.Int()
    weightage_percent = fields.Decimal(as_string=False, allow_none=True)
    
    class Meta:
        ordered = True


class SubmissionSchema(ma.Schema):
    """Schema for submission serialization."""
    
    submission_id = fields.Int(dump_only=True)
    registration_id = fields.Int(required=True)
    assignment_id = fields.Str(required=True)
    submitted_at = fields.DateTime(allow_none=True)
    grade_achieved = fields.Decimal(as_string=False, allow_none=True)
    grader_feedback = fields.Str(allow_none=True)
    
    class Meta:
        ordered = True


class AttendanceSchema(ma.Schema):
    """Schema for attendance serialization."""
    
    attendance_id = fields.Int(dump_only=True)
    registration_id = fields.Int(required=True)
    week_number = fields.Int(required=True, validate=validate.Range(min=1))
    class_date = fields.Date(required=True)
    is_present = fields.Bool(required=True)
    reason_absent = fields.Str(allow_none=True)
    
    class Meta:
        ordered = True


# Create schema instances
weekly_survey_schema = WeeklySurveySchema()
weekly_surveys_schema = WeeklySurveySchema(many=True)

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)

module_schema = ModuleSchema()
modules_schema = ModuleSchema(many=True)

assignment_schema = AssignmentSchema()
assignments_schema = AssignmentSchema(many=True)

submission_schema = SubmissionSchema()
submissions_schema = SubmissionSchema(many=True)

attendance_schema = AttendanceSchema()
attendances_schema = AttendanceSchema(many=True)
