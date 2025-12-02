# Python Docstring Style Guide

This project follows **Google's Python Style Guide** for docstrings. This document provides quick reference examples for maintaining consistency.

## Module-Level Docstrings

Every Python module should start with a docstring:

```python
"""
Module Name and Purpose.

Detailed description of what this module does, its main responsibilities,
and how it fits into the larger application.

Classes:
    ClassName1: Brief description
    ClassName2: Brief description

Functions:
    function_name: Brief description

Usage:
    from module import function_name
    result = function_name(param)
"""
```

## Function Docstrings

### Basic Function

```python
def get_student(student_id):
    """
    Retrieve a student by ID.
    
    Args:
        student_id (str): The unique identifier of the student.
    
    Returns:
        dict: Student information including name, email, and enrollment data.
    """
```

### Function with Multiple Return Types

```python
def update_student(student_id, data):
    """
    Update student information.
    
    Args:
        student_id (str): The unique identifier of the student.
        data (dict): Dictionary containing fields to update.
            Allowed keys:
                - first_name (str): New first name
                - last_name (str): New last name
                - email (str): New email address
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with updated student
            - int: HTTP status code
                - 200: Update successful
                - 400: Invalid data
                - 404: Student not found
                - 500: Server error
    
    Raises:
        ValueError: If email format is invalid.
    """
```

### Function with Examples

```python
def calculate_risk_score(stress, sleep, attendance):
    """
    Calculate student risk score based on wellbeing metrics.
    
    Args:
        stress (int): Stress level (1-5 scale).
        sleep (float): Average sleep hours.
        attendance (float): Attendance percentage.
    
    Returns:
        float: Risk score between 0 and 10.
    
    Example:
        >>> calculate_risk_score(5, 4.0, 60.0)
        8.5
        >>> calculate_risk_score(2, 8.0, 95.0)
        1.2
    """
```

### Function with Notes and Warnings

```python
def delete_student(student_id):
    """
    Delete a student and all related records.
    
    Performs cascade deletion of:
    - Module registrations
    - Weekly surveys
    - Attendance records
    - Submissions
    
    Args:
        student_id (str): The unique identifier of the student.
    
    Returns:
        tuple: Success message and HTTP status code.
    
    Note:
        This operation cannot be undone. Consider archiving instead
        of deleting for audit purposes.
    
    Warning:
        This permanently removes all student data. Ensure proper
        authorization before calling this function.
    """
```

## Class Docstrings

### Model Classes

```python
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
        enrolled_year (int): Year the student enrolled (optional).
    
    Relationships:
        course (Course): The course the student is currently enrolled in.
        registrations (list[ModuleRegistration]): All module registrations.
    
    Example:
        >>> student = Student(
        ...     student_id="S001",
        ...     first_name="John",
        ...     last_name="Doe",
        ...     email="john@example.com"
        ... )
    """
```

### Test Classes

```python
class TestStudentAPI:
    """
    Test suite for student API endpoints.
    
    Tests CRUD operations for student management including creation,
    retrieval, updates, and deletion with proper error handling.
    
    TDD Phase: GREEN - All tests should pass with current implementation.
    """
    
    def test_get_student_success(self, client, sample_data):
        """
        Test successful retrieval of student information.
        
        Verifies that a valid student ID returns the correct student
        data with all expected fields.
        
        TDD Phase: GREEN - Basic functionality test.
        """
```

## Test Function Docstrings

```python
def test_update_student_invalid_email(self, client, sample_data):
    """
    Test email validation during student update.
    
    Verifies that providing an invalid email format returns a 400 Bad
    Request status with an appropriate error message.
    
    TDD Phase: RED/GREEN - Tests input validation.
    
    Expected Behavior:
        - Invalid email format should be rejected
        - Response should include error message
        - Database should remain unchanged
    """
```

## Fixture Docstrings

```python
@pytest.fixture
def sample_survey_data(app):
    """
    Create sample survey data for testing.
    
    Populates the test database with:
    - One course (C001)
    - One module (M001)
    - One student (S001)
    - One module registration
    - Two weekly survey responses
    
    Args:
        app (Flask): The Flask application fixture.
    
    Yields:
        list[WeeklySurvey]: List of created survey objects.
    
    Note:
        All data is automatically cleaned up after the test.
    """
```

## Common Sections

### Args Section
```python
Args:
    param_name (type): Description of parameter.
    optional_param (type, optional): Description. Defaults to None.
    complex_param (dict): Description.
        Expected structure:
            - key1 (str): Description
            - key2 (int): Description
```

### Returns Section
```python
Returns:
    type: Description of return value.

# OR for multiple values

Returns:
    tuple: A tuple containing:
        - type1: Description
        - type2: Description
```

### Raises Section
```python
Raises:
    ValueError: If input validation fails.
    KeyError: If required key is missing.
    DatabaseError: If database operation fails.
```

### Example Section
```python
Example:
    >>> function_name(arg1, arg2)
    expected_output
    
    >>> function_name(different_args)
    different_output
```

### Note Section
```python
Note:
    Important information about usage, behavior, or limitations.
```

### Warning Section
```python
Warning:
    Critical information about security, data loss, or breaking changes.
```

## HTTP Status Code Documentation

For API endpoints, always document possible status codes:

```python
Returns:
    tuple: A tuple containing:
        - flask.Response: JSON response
        - int: HTTP status code
            - 200: Success
            - 201: Created
            - 400: Bad request (validation error)
            - 401: Unauthorized
            - 403: Forbidden
            - 404: Not found
            - 500: Server error
```

## TDD Phase Indicators

For test functions, include TDD phase:

```python
"""
Test description.

TDD Phase: RED - Test written before implementation.
TDD Phase: GREEN - Implementation makes test pass.
TDD Phase: REFACTOR - Code improved while tests pass.
"""
```

## Quick Tips

1. **First line**: Brief one-line summary (imperative mood: "Get", "Update", "Delete")
2. **Blank line**: After first line before detailed description
3. **Args**: Document all parameters with types
4. **Returns**: Always document return values
5. **Examples**: Include for complex functions
6. **Notes**: Add for important behavior
7. **Warnings**: Add for security or data integrity concerns
8. **Keep updated**: Update docstrings when code changes

## Tools

Generate documentation from docstrings:
```bash
# Install Sphinx
pip install sphinx

# Generate HTML docs
sphinx-apidoc -o docs/ app/
cd docs && make html
```

## References

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Sphinx Documentation](https://www.sphinx-doc.org/)

---

*Follow this guide to maintain consistent, high-quality documentation across the project.*
