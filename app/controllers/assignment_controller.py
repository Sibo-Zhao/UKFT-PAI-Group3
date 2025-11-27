from flask import jsonify
from app.models import Assignment, Module, db
from app.views.schemas import assignment_schema
from datetime import datetime

def create_assignment(assignment_data):
    """
    Create a new assignment.
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
    Update an existing assignment.
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
    Delete an assignment.
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
