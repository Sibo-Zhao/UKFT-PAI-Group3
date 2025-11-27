"""
Academic Assignments routes blueprint.
Flask blueprint for assignment CRUD operations.
"""
from flask import Blueprint, jsonify, request
from app.models import Assignment, Module, db
from app.schemas import assignment_schema, assignments_schema
from marshmallow import ValidationError
from datetime import datetime

# Create blueprint
assignments_bp = Blueprint('assignments', __name__, url_prefix='/academic')


@assignments_bp.route('/assignments', methods=['POST'])
def create_assignment():
    """
    Create a new assignment.
    
    Request Body:
        JSON with assignment details
        
    Returns:
        JSON response with created assignment (201) or error (400/404)
    """
    try:
        # Validate and deserialize input
        assignment_data = request.get_json()
        
        # Check if module exists
        # module = Module.query.get(assignment_data.get('module_id'))
        module = db.session.get(Module, assignment_data.get('module_id'))
        if not module:
            return jsonify({"error": "Module not found"}), 404
        
        # Check if assignment_id already exists
        # existing = Assignment.query.get(assignment_data.get('assignment_id'))
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


@assignments_bp.route('/assignments/<string:assignment_id>', methods=['PUT'])
def update_assignment(assignment_id):
    """
    Update an existing assignment.
    
    Args:
        assignment_id: Assignment identifier
        
    Request Body:
        JSON with fields to update
        
    Returns:
        JSON response with updated assignment (200) or error (404/400)
    """
    try:
        # assignment = Assignment.query.get(assignment_id)
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404
        
        update_data = request.get_json()
        
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


@assignments_bp.route('/assignments/<string:assignment_id>', methods=['DELETE'])
def delete_assignment(assignment_id):
    """
    Delete an assignment.
    
    Args:
        assignment_id: Assignment identifier
        
    Returns:
        JSON response with success message (200) or error (404)
    """
    try:
        # assignment = Assignment.query.get(assignment_id)
        assignment = db.session.get(Assignment, assignment_id)
        if not assignment:
            return jsonify({"error": "Assignment not found"}), 404
        
        db.session.delete(assignment)
        db.session.commit()
        
        return jsonify({"message": f"Assignment {assignment_id} deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
