from app import create_app
from app.schemas import course_schema, assignment_schema

app = create_app()
with app.app_context():
    print("Schemas imported successfully")
    try:
        # Try to dump some data
        print("Testing dump...")
        data = {
            "course_id": "C001",
            "course_name": "Test",
            "total_credits": 100
        }
        result = course_schema.dump(data)
        print(f"Dump result: {result}")
    except Exception as e:
        print(f"Dump error: {e}")
        import traceback
        traceback.print_exc()
