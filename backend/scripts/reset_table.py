import os
import sys

# Add backend directory to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.db.database import engine
from app.db.models import ResumeAnalysis

def reset_table():
    print("Dropping ResumeAnalysis table...")
    ResumeAnalysis.__table__.drop(engine, checkfirst=True)
    print("Recreating ResumeAnalysis table...")
    ResumeAnalysis.__table__.create(engine, checkfirst=True)
    print("Done!")

if __name__ == "__main__":
    reset_table()
