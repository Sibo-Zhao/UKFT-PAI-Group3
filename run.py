"""
Flask Application Entry Point.

This script initializes and runs the Flask application. It sets up the
configuration, validates database connectivity, and starts the development
server.

Usage:
    python run.py

The application will run on http://0.0.0.0:5001 with debug mode enabled.
"""
from app import create_app
from app.config import Config, DatabaseConnector

app_config = Config()
connector = DatabaseConnector(app_config)
connector.connect()
app = create_app(config_class=Config)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)