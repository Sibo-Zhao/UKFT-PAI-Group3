"""
Flask application factory.
University Wellbeing API - Flask application setup.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.models import db
from app.views.schemas import ma
from app.routes.surveys import surveys_bp
from app.routes.courses import courses_bp
from app.routes.assignments import assignments_bp
from app.routes.academic import academic_bp
from app.routes.students import students_bp
from app.routes.reports import reports_bp
from app.routes.auth import auth_bp

def create_app(config_class=Config):
    """
    Application factory pattern.
    """
    app = Flask(__name__)

    # 1. Instantiate Config
    config_instance = config_class()

    # 2. Load Standard Configs (DEBUG, TESTING, SECRET_KEY)
    app.config.from_object(config_instance)

    # Flask-SQLAlchemy needs 'SQLALCHEMY_DATABASE_URI', but our Config
    # holds it in the property 'database_url'. We assign it manually here.
    app.config['SQLALCHEMY_DATABASE_URI'] = config_instance.database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 4. Initialize Extensions
    db.init_app(app)
    ma.init_app(app)
    CORS(app)

    # 5. Register Blueprints
    app.register_blueprint(surveys_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(academic_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(auth_bp)

    # 6. Global/Health Routes
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
        # Optional: Add a real DB check here if you want "deep" health monitoring
        return jsonify({"status": "healthy"})

    return app