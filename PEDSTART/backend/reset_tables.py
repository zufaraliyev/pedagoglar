import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    database="pedtayyor_db",
    charset="utf8mb4"
)
with conn.cursor() as cursor:
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("DROP TABLE IF EXISTS test_attempts, quiz_attempts, submissions, tests, tasks, lessons, modules, user_badges, badges, users;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
conn.close()
print("Barcha jadvallar tozalandi va qayta yaratilishga tayyor.")
