"""
Flask application factory.
University Wellbeing API - Flask application setup.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config, TestConfig
from app.models import db
from app.views.schemas import ma


def create_app(config_class=Config):
    """
    Application factory pattern.
    
    Args:
        config_class: Configuration class to use (Config or TestConfig)
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes.surveys import surveys_bp
    from app.routes.courses import courses_bp
    from app.routes.assignments import assignments_bp
    from app.routes.academic import academic_bp
    from app.routes.students import students_bp
    from app.routes.reports import reports_bp  
    from app.routes.auth import auth_bp  
    app.register_blueprint(surveys_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(academic_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(reports_bp)  # Add this
    app.register_blueprint(auth_bp) 
    
    # Root route
    @app.route('/')
    def index():
        return jsonify({
            "message": "University Wellbeing API",
            "status": "running",
            "version": "1.0.0",
            "framework": "Flask"
        })
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy"})
    
    return app
