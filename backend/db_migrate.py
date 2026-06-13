import sqlite3
import os

db_path = "resume_analyzer.db"

if not os.path.exists(db_path):
    print("Database not found at", db_path)
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE resumes ADD COLUMN analysis_status VARCHAR DEFAULT 'Pending'")
    print("Added analysis_status column successfully.")
except sqlite3.OperationalError as e:
    print("analysis_status column might already exist:", e)

try:
    cursor.execute("ALTER TABLE resumes ADD COLUMN ats_score FLOAT")
    print("Added ats_score column successfully.")
except sqlite3.OperationalError as e:
    print("ats_score column might already exist:", e)

conn.commit()
conn.close()
print("Migration completed.")
