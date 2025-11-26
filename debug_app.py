import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.getcwd()))

try:
    from app import create_app, db
    print("Import successful")
    
    app = create_app()
    print("App creation successful")
    
    with app.app_context():
        print("App context successful")
        # Try to access models
        from app.models import Student
        print("Models import successful")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
