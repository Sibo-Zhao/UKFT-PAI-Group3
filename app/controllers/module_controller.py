"""
Module Controller Module.

This module handles CRUD operations for course modules including
creation, updates, deletion, and module registration management.
"""
from flask import jsonify
from app.models import Module, Course, ModuleRegistration, Student, db
from app.views.schemas import module_schema, modules_schema
from app.utils.error_handlers import handle_error, log_request_error
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_all_modules():
    """
    Retrieve all modules from the database.
    
    Returns:
        tuple: JSON response with list of modules and HTTP status code
    """
    try:
        logger.info("Fetching all modules")
        modules = Module.query.all()
        result = modules_schema.dump(modules)
        logger.info(f"Successfully retrieved {len(modules)} modules")
        return jsonify(result), 200
    except Exception as e:
        log_request_error("get_all_modules", e)
        return handle_error(e, "in get_all_modules")


def get_module(module_id):
    """
    Retrieve a specific module by ID.
    
    Args:
        module_id (str): The unique identifier of the module
        
    Returns:
        tuple: JSON response with module data and HTTP status code
    """
    try:
        logger.info(f"Fetching module: {module_id}")
        module = db.session.get(Module, module_id)
        if not module:
            logger.warning(f"Module not found: {module_id}")
            return jsonify({"error": "Module not found"}), 404
        
        result = module_schema.dump(module)
        logger.info(f"Successfully retrieved module: {module_id}")
        return jsonify(result), 200
    except Exception as e:
        log_request_error("get_module", e, module_id=module_id)
        return handle_error(e, f"in get_module for module_id={module_id}")


def create_module(data):
    """
    Create a new module.
    
    Args:
        data (dict): Module data including module_id, course_id, module_name, duration_weeks
        
    Returns:
        tuple: JSON response with created module and HTTP status code
    """
    try:
        logger.info(f"Creating new module: {data.get('module_id')}")
        
        # Validate required fields
        required_fields = ['module_id', 'course_id', 'module_name']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Check if module_id already exists
        if db.session.get(Module, data['module_id']):
            return jsonify({"error": "Module ID already exists"}), 409
        
        # Validate course exists
        course = db.session.get(Course, data['course_id'])
        if not course:
            return jsonify({"error": "Course not found"}), 404
        
        # Create new module
        module = Module(
            module_id=data['module_id'],
            course_id=data['course_id'],
            module_name=data['module_name'],
            duration_weeks=data.get('duration_weeks', 12)
        )
        
        db.session.add(module)
        db.session.commit()
        
        result = module_schema.dump(module)
        logger.info(f"Successfully created module: {data['module_id']}")
        return jsonify(result), 201
        
    except Exception as e:
        db.session.rollback()
        log_request_error("create_module", e)
        return handle_error(e, "in create_module")


def update_module(module_id, data):
    """
    Update an existing module.
    
    Args:
        module_id (str): The unique identifier of the module
        data (dict): Updated module data
        
    Returns:
        tuple: JSON response with updated module and HTTP status code
    """
    try:
        logger.info(f"Updating module: {module_id}")
        module = db.session.get(Module, module_id)
        if not module:
            logger.warning(f"Module not found for update: {module_id}")
            return jsonify({"error": "Module not found"}), 404
        
        # Update allowed fields
        allowed_fields = ['module_name', 'duration_weeks', 'course_id']
        updated_fields = []
        
        for field in allowed_fields:
            if field in data:
                if field == 'course_id':
                    # Validate course exists
                    course = db.session.get(Course, data[field])
                    if not course:
                        return jsonify({"error": "Course not found"}), 404
                
                setattr(module, field, data[field])
                updated_fields.append(field)
        
        db.session.commit()
        logger.info(f"Successfully updated module {module_id}, fields: {', '.join(updated_fields)}")
        
        result = module_schema.dump(module)
        return jsonify(result), 200
        
    except Exception as e:
        db.session.rollback()
        log_request_error("update_module", e, module_id=module_id)
        return handle_error(e, f"in update_module for module_id={module_id}")


def delete_module(module_id):
    """
    Delete a module and all related records.
    
    Args:
        module_id (str): The unique identifier of the module
        
    Returns:
        tuple: JSON response with success message and HTTP status code
    """
    try:
        logger.info(f"Attempting to delete module: {module_id}")
        module = db.session.get(Module, module_id)
        if not module:
            logger.warning(f"Module not found for deletion: {module_id}")
            return jsonify({"error": "Module not found"}), 404
        
        db.session.delete(module)
        db.session.commit()
        
        logger.info(f"Successfully deleted module: {module_id}")
        return jsonify({"message": f"Module {module_id} deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        log_request_error("delete_module", e, module_id=module_id)
        return handle_error(e, f"in delete_module for module_id={module_id}")


def register_student_to_module(data):
    """
    Register a student to a module.
    
    Args:
        data (dict): Registration data including student_id, module_id, start_date
        
    Returns:
        tuple: JSON response with registration details and HTTP status code
    """
    try:
        logger.info(f"Registering student {data.get('student_id')} to module {data.get('module_id')}")
        
        # Validate required fields
        required_fields = ['student_id', 'module_id']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400
        
        # Validate student exists
        student = db.session.get(Student, data['student_id'])
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        # Validate module exists
        module = db.session.get(Module, data['module_id'])
        if not module:
            return jsonify({"error": "Module not found"}), 404
        
        # Check if registration already exists
        existing_registration = ModuleRegistration.query.filter_by(
            student_id=data['student_id'],
            module_id=data['module_id']
        ).first()
        
        if existing_registration:
            return jsonify({"error": "Student already registered for this module"}), 409
        
        # Create registration
        registration = ModuleRegistration(
            student_id=data['student_id'],
            module_id=data['module_id'],
            status=data.get('status', 'Active'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None
        )
        
        db.session.add(registration)
        db.session.commit()
        
        logger.info(f"Successfully registered student {data['student_id']} to module {data['module_id']}")
        return jsonify({
            "message": "Student registered successfully",
            "registration_id": registration.registration_id,
            "student_id": registration.student_id,
            "module_id": registration.module_id,
            "status": registration.status
        }), 201
        
    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        log_request_error("register_student_to_module", e)
        return handle_error(e, "in register_student_to_module")


def get_module_registrations(module_id):
    """
    Get all student registrations for a specific module.
    
    Args:
        module_id (str): The unique identifier of the module
        
    Returns:
        tuple: JSON response with list of registrations and HTTP status code
    """
    try:
        logger.info(f"Fetching registrations for module: {module_id}")
        
        # Validate module exists
        module = db.session.get(Module, module_id)
        if not module:
            return jsonify({"error": "Module not found"}), 404
        
        registrations = ModuleRegistration.query.filter_by(module_id=module_id).all()
        
        result = []
        for reg in registrations:
            student = db.session.get(Student, reg.student_id)
            result.append({
                "registration_id": reg.registration_id,
                "student_id": reg.student_id,
                "student_name": f"{student.first_name} {student.last_name}" if student else "Unknown",
                "student_email": student.email if student else None,
                "status": reg.status,
                "start_date": reg.start_date.isoformat() if reg.start_date else None
            })
        
        # Get course information through module
        course = db.session.get(Course, module.course_id) if module.course_id else None
        
        logger.info(f"Successfully retrieved {len(registrations)} registrations for module: {module_id}")
        return jsonify({
            "module_id": module_id,
            "module_name": module.module_name,
            "course_id": module.course_id,
            "course_name": course.course_name if course else None,
            "duration_weeks": module.duration_weeks,
            "registrations": result,
            "total_registrations": len(result)
        }), 200
        
    except Exception as e:
        log_request_error("get_module_registrations", e, module_id=module_id)
        return handle_error(e, f"in get_module_registrations for module_id={module_id}")


def update_registration_status(registration_id, data):
    """
    Update the status of a module registration.
    
    Args:
        registration_id (int): The unique identifier of the registration
        data (dict): Update data including new status
        
    Returns:
        tuple: JSON response with updated registration and HTTP status code
    """
    try:
        logger.info(f"Updating registration status: {registration_id}")
        
        registration = db.session.get(ModuleRegistration, registration_id)
        if not registration:
            return jsonify({"error": "Registration not found"}), 404
        
        # Validate status
        valid_statuses = ['Active', 'Completed', 'Withdrawn']
        new_status = data.get('status')
        if new_status and new_status not in valid_statuses:
            return jsonify({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
        
        if new_status:
            registration.status = new_status
        
        db.session.commit()
        
        logger.info(f"Successfully updated registration {registration_id} status to {new_status}")
        return jsonify({
            "message": "Registration status updated successfully",
            "registration_id": registration.registration_id,
            "new_status": registration.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        log_request_error("update_registration_status", e, registration_id=registration_id)
        return handle_error(e, f"in update_registration_status for registration_id={registration_id}")