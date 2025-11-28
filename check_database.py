"""
Database inspection script to check MySQL database status and tables.
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection details
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '13.40.85.93'),
    'user': os.getenv('DB_USER', 'pyuser'),
    'password': os.getenv('DB_PASSWORD', 'paigroup3'),
    'database': os.getenv('DB_NAME', 'uni_wellbeing_db'),
    'port': int(os.getenv('DB_PORT', 3306))
}

def check_database():
    """Check database connection and list all tables."""
    print("=" * 70)
    print("MySQL Database Inspector")
    print("=" * 70)
    print(f"\nConnecting to: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"User: {DB_CONFIG['user']}\n")
    
    try:
        # Connect to database
        connection = pymysql.connect(**DB_CONFIG)
        print("✓ Connection successful!\n")
        
        with connection.cursor() as cursor:
            # Show all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"Found {len(tables)} tables:")
                print("-" * 70)
                for i, table in enumerate(tables, 1):
                    table_name = table[0]
                    print(f"{i}. {table_name}")
                    
                    # Get row count for each table
                    cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
                    count = cursor.fetchone()[0]
                    print(f"   → {count} rows")
                print("-" * 70)
            else:
                print("⚠ No tables found in database!")
                print("\nThis could mean:")
                print("  1. Database schema hasn't been created yet")
                print("  2. You're connected to an empty database")
                print("  3. User doesn't have permission to see tables")
            
            # Check if specific tables exist
            print("\n\nChecking for expected tables:")
            expected_tables = [
                'students', 'courses', 'modules', 'assignments',
                'module_registrations', 'weekly_surveys', 
                'weekly_attendance', 'submissions'
            ]
            
            cursor.execute("SHOW TABLES")
            existing_tables = [t[0].lower() for t in cursor.fetchall()]
            
            for table in expected_tables:
                if table in existing_tables:
                    print(f"  ✓ {table}")
                else:
                    print(f"  ✗ {table} (MISSING)")
        
        connection.close()
        
    except pymysql.err.OperationalError as e:
        print(f"✗ Connection failed: {e}")
        print("\nPossible issues:")
        print("  1. Database server is down")
        print("  2. Incorrect credentials")
        print("  3. Firewall blocking connection")
        print("  4. Database doesn't exist")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 70)
    print("Web Access Information")
    print("=" * 70)
    print("\nTo access MySQL via browser, you can use phpMyAdmin:")
    print(f"  URL: http://{DB_CONFIG['host']}/phpmyadmin")
    print(f"  OR:  http://{DB_CONFIG['host']}:8080/phpmyadmin")
    print(f"\n  Username: {DB_CONFIG['user']}")
    print(f"  Password: {DB_CONFIG['password']}")
    print(f"  Database: {DB_CONFIG['database']}")
    print("\nNote: phpMyAdmin must be installed on the server")
    print("=" * 70)

if __name__ == "__main__":
    check_database()



