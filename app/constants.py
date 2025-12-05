"""
Application Constants.

This module defines all constants used throughout the University Wellbeing API
to avoid magic numbers and improve maintainability.

Constants are organized by domain:
- Academic performance thresholds
- Risk assessment criteria
- Validation limits
- Default values
"""

# Academic Performance Thresholds
ATTENDANCE_THRESHOLD_LOW = 70.0  # Below this percentage is considered low attendance
ATTENDANCE_THRESHOLD_CRITICAL = 50.0  # Below this percentage is critical
GRADE_THRESHOLD_FAILING = 40.0  # Below this grade is considered failing
GRADE_THRESHOLD_EXCELLENT = 90.0  # Above this grade is excellent

# Risk Assessment Criteria
RISK_SCORE_HIGH_STRESS = 4  # Stress level above this is high risk
RISK_SCORE_LOW_SLEEP = 6.0  # Sleep hours below this is concerning
RISK_SCORE_LOW_SOCIAL = 2  # Social connection below this is concerning

# Risk Score Weights
RISK_WEIGHT_ATTENDANCE = 2.5
RISK_WEIGHT_HIGH_STRESS = 3.0
RISK_WEIGHT_LOW_SLEEP = 2.0
RISK_WEIGHT_LOW_SOCIAL = 2.0
RISK_WEIGHT_FAILING_GRADES = 3.5

# Validation Limits
MAX_STRESS_LEVEL = 5
MIN_STRESS_LEVEL = 1
MAX_SOCIAL_CONNECTION = 5
MIN_SOCIAL_CONNECTION = 1
MAX_SLEEP_HOURS = 24.0
MIN_SLEEP_HOURS = 0.0
MAX_WEEK_NUMBER = 52
MIN_WEEK_NUMBER = 1

# Default Values
DEFAULT_MODULE_DURATION_WEEKS = 12
DEFAULT_ASSIGNMENT_MAX_SCORE = 100
DEFAULT_COURSE_CREDITS = 180
DEFAULT_REGISTRATION_STATUS = 'Active'

# Pagination Limits
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200

# Date Formats
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# Valid Enum Values
VALID_REGISTRATION_STATUSES = ['Active', 'Completed', 'Withdrawn']
VALID_COMPARISON_METRICS = ['attendance', 'grades', 'wellbeing', 'submissions', 'all']
VALID_SUBMISSION_STATUSES = ['early', 'on_time', 'late']

# Error Messages
ERROR_STUDENT_NOT_FOUND = "Student not found"
ERROR_COURSE_NOT_FOUND = "Course not found"
ERROR_MODULE_NOT_FOUND = "Module not found"
ERROR_ASSIGNMENT_NOT_FOUND = "Assignment not found"
ERROR_REGISTRATION_NOT_FOUND = "Registration not found"
ERROR_DUPLICATE_STUDENT_ID = "Student ID already exists"
ERROR_DUPLICATE_EMAIL = "Email already exists"
ERROR_INVALID_EMAIL_FORMAT = "Invalid email format"
ERROR_MISSING_REQUIRED_FIELDS = "Missing required fields: {fields}"
ERROR_INVALID_DATE_FORMAT = "Invalid date format. Use YYYY-MM-DD"
ERROR_INVALID_DATETIME_FORMAT = "Invalid datetime format. Use ISO format"

# Success Messages
SUCCESS_STUDENT_CREATED = "Student created successfully"
SUCCESS_STUDENT_UPDATED = "Student updated successfully"
SUCCESS_STUDENT_DELETED = "Student {student_id} and all related records deleted successfully"
SUCCESS_ATTENDANCE_RECORDED = "Attendance recorded successfully"
SUCCESS_SUBMISSION_GRADED = "Submission graded successfully"