"""
Flask application entry point.
Run this file to start the development server.
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True, host='0.0.0.0', port=5001)


