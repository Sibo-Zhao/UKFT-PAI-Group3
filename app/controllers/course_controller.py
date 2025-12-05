"""
Course Controller Module.

This module handles course, module, and assignment retrieval operations.
Provides endpoints for accessing course catalog information and related data.
"""
from flask import jsonify
from app.models import Course, Module, Assignment
from app.views.schemas import courses_schema, modules_schema, assignments_schema
from app.utils.error_handlers import handle_error, log_request_error
import logging

logger = logging.getLogger(__name__)


def get_all_courses():
    """
    Retrieve all courses from the database.
    
    Fetches all course records and serializes them using the course schema.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with list of courses
            - int: HTTP status code
                - 200: Success
                - 500: Server error
    
    Example Response:
        [
            {
                "course_id": "CS101",
                "course_name": "Introduction to Computer Science",
                "total_credits": 180,
                "created_at": "2025-01-01T00:00:00"
            }
        ]
    """
    try:
        logger.info("Fetching all courses")
        courses = Course.query.all()
        result = courses_schema.dump(courses)
        logger.info(f"Successfully retrieved {len(courses)} courses")
        return jsonify(result), 200
    except Exception as e:
        log_request_error("get_all_courses", e)
        return handle_error(e, "in get_all_courses")

def get_course_modules(course_id):
    """
    Retrieve all modules associated with a specific course.
    
    Fetches all module records for the given course ID and serializes them.
    Validates that the course exists before retrieving modules.
    
    Args:
        course_id (str): The unique identifier of the course.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with course info and modules
            - int: HTTP status code
                - 200: Success
                - 404: Course not found
                - 500: Server error
    
    Example Response:
        {
            "course_id": "CS101",
            "course_name": "Introduction to Computer Science",
            "modules": [
                {
                    "module_id": "MOD101",
                    "course_id": "CS101",
                    "module_name": "Programming Fundamentals",
                    "duration_weeks": 12
                }
            ],
            "total_modules": 1
        }
    """
    try:
        logger.info(f"Fetching modules for course: {course_id}")
        
        # Validate course exists
        course = db.session.get(Course, course_id)
        if not course:
            logger.warning(f"Course not found: {course_id}")
            return jsonify({"error": "Course not found"}), 404
        
        modules = Module.query.filter_by(course_id=course_id).all()
        modules_data = modules_schema.dump(modules)
        
        result = {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "total_credits": course.total_credits,
            "modules": modules_data,
            "total_modules": len(modules_data)
        }
        
        logger.info(f"Successfully retrieved {len(modules)} modules for course: {course_id}")
        return jsonify(result), 200
    except Exception as e:
        log_request_error("get_course_modules", e, course_id=course_id)
        return handle_error(e, f"in get_course_modules for course_id={course_id}")

def get_module_assignments(module_id):
    """
    Retrieve all assignments associated with a specific module.
    
    Fetches all assignment records for the given module ID and serializes them.
    Validates that the module exists before retrieving assignments.
    
    Args:
        module_id (str): The unique identifier of the module.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with module info and assignments
            - int: HTTP status code
                - 200: Success
                - 404: Module not found
                - 500: Server error
    
    Example Response:
        {
            "module_id": "MOD101",
            "module_name": "Programming Fundamentals",
            "course_id": "CS101",
            "assignments": [
                {
                    "assignment_id": "A001",
                    "module_id": "MOD101",
                    "title": "Final Project",
                    "description": "Complete the final project",
                    "due_date": "2025-12-15T23:59:59",
                    "max_score": 100,
                    "weightage_percent": 30.0
                }
            ],
            "total_assignments": 1
        }
    """
    try:
        logger.info(f"Fetching assignments for module: {module_id}")
        
        # Validate module exists
        module = db.session.get(Module, module_id)
        if not module:
            logger.warning(f"Module not found: {module_id}")
            return jsonify({"error": "Module not found"}), 404
        
        assignments = Assignment.query.filter_by(module_id=module_id).all()
        assignments_data = assignments_schema.dump(assignments)
        
        result = {
            "module_id": module.module_id,
            "module_name": module.module_name,
            "course_id": module.course_id,
            "duration_weeks": module.duration_weeks,
            "assignments": assignments_data,
            "total_assignments": len(assignments_data)
        }
        
        logger.info(f"Successfully retrieved {len(assignments)} assignments for module: {module_id}")
        return jsonify(result), 200
    except Exception as e:
        log_request_error("get_module_assignments", e, module_id=module_id)
        return handle_error(e, f"in get_module_assignments for module_id={module_id}")


def get_course_details(course_id):
    """
    Retrieve complete course details including modules and assignments.
    
    Fetches course information along with all its modules and their assignments
    in a hierarchical structure.
    
    Args:
        course_id (str): The unique identifier of the course.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with complete course hierarchy
            - int: HTTP status code
                - 200: Success
                - 404: Course not found
                - 500: Server error
    
    Example Response:
        {
            "course_id": "CS101",
            "course_name": "Introduction to Computer Science",
            "total_credits": 180,
            "created_at": "2025-01-01T00:00:00",
            "modules": [
                {
                    "module_id": "MOD101",
                    "module_name": "Programming Fundamentals",
                    "duration_weeks": 12,
                    "assignments": [
                        {
                            "assignment_id": "A001",
                            "title": "Final Project",
                            "due_date": "2025-12-15T23:59:59",
                            "max_score": 100
                        }
                    ],
                    "total_assignments": 1
                }
            ],
            "total_modules": 1,
            "total_assignments": 1
        }
    """
    try:
        logger.info(f"Fetching complete details for course: {course_id}")
        
        # Validate course exists
        course = db.session.get(Course, course_id)
        if not course:
            logger.warning(f"Course not found: {course_id}")
            return jsonify({"error": "Course not found"}), 404
        
        # Get modules for this course
        modules = Module.query.filter_by(course_id=course_id).all()
        
        modules_data = []
        total_assignments = 0
        
        for module in modules:
            # Get assignments for each module
            assignments = Assignment.query.filter_by(module_id=module.module_id).all()
            assignments_data = assignments_schema.dump(assignments)
            
            module_info = {
                "module_id": module.module_id,
                "module_name": module.module_name,
                "duration_weeks": module.duration_weeks,
                "assignments": assignments_data,
                "total_assignments": len(assignments_data)
            }
            
            modules_data.append(module_info)
            total_assignments += len(assignments_data)
        
        result = {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "total_credits": course.total_credits,
            "created_at": course.created_at.isoformat() if course.created_at else None,
            "modules": modules_data,
            "total_modules": len(modules_data),
            "total_assignments": total_assignments
        }
        
        logger.info(f"Successfully retrieved complete details for course: {course_id} "
                   f"({len(modules_data)} modules, {total_assignments} assignments)")
        return jsonify(result), 200
        
    except Exception as e:
        log_request_error("get_course_details", e, course_id=course_id)
        return handle_error(e, f"in get_course_details for course_id={course_id}")


def get_course(course_id):
    """
    Retrieve a specific course by ID.
    
    Args:
        course_id (str): The unique identifier of the course.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with course data
            - int: HTTP status code
                - 200: Success
                - 404: Course not found
                - 500: Server error
    """
    try:
        logger.info(f"Fetching course: {course_id}")
        course = db.session.get(Course, course_id)
        if not course:
            logger.warning(f"Course not found: {course_id}")
            return jsonify({"error": "Course not found"}), 404
        
        result = {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "total_credits": course.total_credits,
            "created_at": course.created_at.isoformat() if course.created_at else None
        }
        
        logger.info(f"Successfully retrieved course: {course_id}")
        return jsonify(result), 200
    except Exception as e:
        log_request_error("get_course", e, course_id=course_id)
        return handle_error(e, f"in get_course for course_id={course_id}")


def get_course_students(course_id):
    """
    Retrieve all students enrolled in a specific course.
    
    Args:
        course_id (str): The unique identifier of the course.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with course info and enrolled students
            - int: HTTP status code
                - 200: Success
                - 404: Course not found
                - 500: Server error
    
    Example Response:
        {
            "course_id": "CS101",
            "course_name": "Introduction to Computer Science",
            "total_credits": 180,
            "students": [
                {
                    "student_id": "S001",
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "enrolled_year": 2023,
                    "contact_no": "+1234567890"
                }
            ],
            "total_students": 1
        }
    """
    try:
        logger.info(f"Fetching students for course: {course_id}")
        
        # Validate course exists
        course = db.session.get(Course, course_id)
        if not course:
            logger.warning(f"Course not found: {course_id}")
            return jsonify({"error": "Course not found"}), 404
        
        # Get all students enrolled in this course
        students = Student.query.filter_by(current_course_id=course_id).all()
        
        students_data = []
        for student in students:
            students_data.append({
                "student_id": student.student_id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "email": student.email,
                "enrolled_year": student.enrolled_year,
                "contact_no": student.contact_no
            })
        
        result = {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "total_credits": course.total_credits,
            "created_at": course.created_at.isoformat() if course.created_at else None,
            "students": students_data,
            "total_students": len(students_data)
        }
        
        logger.info(f"Successfully retrieved {len(students_data)} students for course: {course_id}")
        return jsonify(result), 200
        
    except Exception as e:
        log_request_error("get_course_students", e, course_id=course_id)
        return handle_error(e, f"in get_course_students for course_id={course_id}")
