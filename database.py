import sqlite3


def get_db_connection():
    connection = sqlite3.connect("resume_analyzer.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_applications_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant_name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            job_title TEXT NOT NULL,
            match_percentage INTEGER NOT NULL,
            application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_applications_table()
    print("Applications table created successfully!")