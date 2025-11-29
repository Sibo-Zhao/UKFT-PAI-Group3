from flask import Blueprint
from app.controllers import reports_controller

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/module/<string:module_id>/academic', methods=['GET'])
def get_module_academic_report(module_id):
    """Get academic report for a module (grades, attendance, submissions)."""
    return reports_controller.get_module_academic_report(module_id)


@reports_bp.route('/student/<string:student_id>/academic', methods=['GET'])
def get_student_academic_report(student_id):
    """Get academic report for a specific student."""
    return reports_controller.get_student_academic_report(student_id)