import pymysql

# Test remote database connection
conn = pymysql.connect(
    host="13.40.85.93",
    user="pyuser", 
    password="paigroup3",
    database="uni_wellbeing_db",
    charset="utf8mb4"
)

cursor = conn.cursor()
sql = "SELECT * FROM courses LIMIT 5;"
cursor.execute(sql)
rows = cursor.fetchall()

for row in rows:
    print(row)

cursor.close()
conn.close()