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


@reports_bp.route('/weekly', methods=['GET'])
def get_weekly_report():
    """Get general weekly report (stress, sleep, attendance)."""
    return reports_controller.get_weekly_report()


@reports_bp.route('/weekly/attendance', methods=['GET'])
def get_weekly_attendance_report():
    """Get weekly attendance report (rate and changes)."""
    return reports_controller.get_weekly_attendance_report()


@reports_bp.route('/weekly/absences', methods=['GET'])
def get_absent_students_report():
    """Get report of all students with their total absence count."""
    return reports_controller.get_absent_students_report()


@reports_bp.route('/weekly/grade-decline', methods=['GET'])
def get_grade_decline_report():
    """Identify students whose grades have shown a significant decline."""
    return reports_controller.get_grade_decline_report()