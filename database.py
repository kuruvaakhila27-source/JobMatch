import sqlite3

DB_NAME = "jobmatch.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Saved Jobs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Search History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            location TEXT,
            jobs_found INTEGER DEFAULT 0,
            searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_job(title, company, location, url):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM saved_jobs
        WHERE title = ? AND company = ?
    """, (title, company))

    existing = cursor.fetchone()

    if not existing:
        cursor.execute("""
            INSERT INTO saved_jobs
            (title, company, location, url)
            VALUES (?, ?, ?, ?)
        """, (
            title,
            company,
            location,
            url
        ))

        conn.commit()

    conn.close()


def get_saved_jobs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            company,
            location,
            url,
            created_at
        FROM saved_jobs
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "company": row[2],
            "location": row[3],
            "url": row[4],
            "created_at": row[5]
        }
        for row in rows
    ]


def delete_job(job_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM saved_jobs
        WHERE id = ?
    """, (job_id,))

    conn.commit()
    conn.close()


# ---------------- SEARCH HISTORY ----------------

def save_search(role, location, jobs_found):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO search_history
        (role, location, jobs_found)
        VALUES (?, ?, ?)
    """, (
        role,
        location,
        jobs_found
    ))

    conn.commit()
    conn.close()


def get_search_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            role,
            location,
            jobs_found,
            searched_at
        FROM search_history
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "role": row[1],
            "location": row[2],
            "jobs_found": row[3],
            "searched_at": row[4]
        }
        for row in rows
    ]


def clear_search_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM search_history
    """)

    conn.commit()
    conn.close()