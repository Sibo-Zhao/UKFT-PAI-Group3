"""
Assignment Controller Module.

This module handles CRUD operations for academic assignments including
creation, updates, and deletion of assignment records.
"""
from flask import jsonify
from app.models import Assignment, Module, db
from app.views.schemas import assignment_schema
from datetime import datetime


def create_assignment(assignment_data):
    """
    Create a new assignment in the database.
    
    Validates that the module exists and the assignment ID is unique before
    creating the new assignment record.
    
    Args:
        assignment_data (dict): Dictionary containing assignment information.
            Required keys:
                - assignment_id (str): Unique assignment identifier
                - module_id (str): ID of the module this assignment belongs to
                - title (str): Assignment title
                - due_date (str): ISO format datetime string
            Optional keys:
                - description (str): Assignment description
                - max_score (int): Maximum achievable score (default: 100)
                - weightage_percent (float): Percentage weight in final grade
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with created assignment
            - int: HTTP status code
                - 201: Assignment created successfully
                - 400: Missing required fields or assignment ID already exists
                - 404: Module not found
                - 500: Server error
    
    Example:
        >>> create_assignment({
        ...     "assignment_id": "A001",
        ...     "module_id": "MOD101",
        ...     "title": "Midterm Exam",
        ...     "due_date": "2025-12-01T00:00:00Z",
        ...     "max_score": 100
        ... })
    """
    try:
        # Check if module exists
        module = db.session.get(Module, assignment_data.get('module_id'))
        if not module:
            return jsonify({"error": "Module not found"}), 404
        
        # Check if assignment_id already exists
        existing = db.session.get(Assignment, assignment_data.get('assignment_id'))
        if existing:
            return jsonify({"error": "Assignment ID already exists"}), 400
        
        # Create new assignment
        new_assignment = Assignment(
            assignment_id=assignment_data['assignment_id'],
            module_id=assignment_data['module_id'],
            title=assignment_data['title'],
            description=assignment_data.get('description'),
            due_date=datetime.fromisoformat(assignment_data['due_date'].replace('Z', '+00:00')),
            max_score=assignment_data.get('max_score', 100),
            weightage_percent=assignment_data.get('weightage_percent')
        )
        
        db.session.add(new_assignment)
        db.session.commit()
        
        result = assignment_schema.dump(new_assignment)
        return jsonify(result), 201
        
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"error": f"Invalid data: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def update_assignment(assignment_id, update_data):
    """
    Update an existing assignment's information.
    
    Allows partial updates - only provided fields will be modified.
    
    Args:
        assignment_id (str): The unique identifier of the assignment to update.
        update_data (dict): Dictionary containing fields to update.
            Allowed keys:
                - title (str): New assignment title
                - description (str): New description
                - due_date (str): New due date (ISO format)
                - max_score (int): New maximum score
                - weightage_percent (float): New weightage percentage
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with updated assignment
            - int: HTTP status code
                - 200: Update successful
                - 400: Invalid data format
                - 404: Assignment not found
                - 500: Server error
    """
    try:
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404
        
        # Update fields if provided
        if 'title' in update_data:
            assignment.title = update_data['title']
        if 'description' in update_data:
            assignment.description = update_data['description']
        if 'due_date' in update_data:
            assignment.due_date = datetime.fromisoformat(update_data['due_date'].replace('Z', '+00:00'))
        if 'max_score' in update_data:
            assignment.max_score = update_data['max_score']
        if 'weightage_percent' in update_data:
            assignment.weightage_percent = update_data['weightage_percent']
        
        db.session.commit()
        
        result = assignment_schema.dump(assignment)
        return jsonify(result), 200
        
    except ValueError as e:
        return jsonify({"error": f"Invalid data: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def delete_assignment(assignment_id):
    """
    Delete an assignment from the database.
    
    Permanently removes the assignment record. Related submissions will be
    handled according to the database cascade rules.
    
    Args:
        assignment_id (str): The unique identifier of the assignment to delete.
    
    Returns:
        tuple: A tuple containing:
            - flask.Response: JSON response with success message
            - int: HTTP status code
                - 200: Deletion successful
                - 404: Assignment not found
                - 500: Server error
    """
    try:
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404
        
        db.session.delete(assignment)
        db.session.commit()
        
        return jsonify({"message": f"Assignment {assignment_id} deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
