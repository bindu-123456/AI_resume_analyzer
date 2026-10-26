import sqlite3
import json
from datetime import datetime

DATABASE_NAME = "resume_analyzer.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_filename TEXT NOT NULL,
            job_title TEXT NOT NULL,
            match_percentage INTEGER NOT NULL,
            matching_skills TEXT NOT NULL,
            missing_skills TEXT NOT NULL,
            suggestions TEXT NOT NULL,
            analyzed_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_analysis(
    resume_filename,
    job_title,
    match_percentage,
    matching_skills,
    missing_skills,
    suggestions
):
    connection = get_db_connection()

    connection.execute("""
        INSERT INTO analysis_history (
            resume_filename,
            job_title,
            match_percentage,
            matching_skills,
            missing_skills,
            suggestions,
            analyzed_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        resume_filename,
        job_title,
        match_percentage,
        json.dumps(matching_skills),
        json.dumps(missing_skills),
        json.dumps(suggestions),
        datetime.now().isoformat(timespec="seconds")
    ))

    connection.commit()
    connection.close()