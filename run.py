"""
Flask application entry point.
Run this file to start the development server.
"""
from app import create_app
from app.models import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist (for testing)
        # In production, use migrations
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5001)
