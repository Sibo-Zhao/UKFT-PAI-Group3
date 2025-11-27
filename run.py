"""
Flask application entry point.
"""
from app import create_app
from app.config import Config, DatabaseConnector

app_config = Config()
connector = DatabaseConnector(app_config)
connector.connect()
app = create_app(config_class=Config)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)