import sqlite3


def get_db_connection():
    connection = sqlite3.connect("users.db", timeout=5)
    connection.row_factory = sqlite3.Row
    return connection


def create_user_table():
    try:
        conn = get_db_connection()
        curs = conn.cursor()
        curs.execute("""
            CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            username TEXT NOT NULL UNIQUE,
            gmail TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email_verified BOOLEAN DEFAULT FALSE);""")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def create_quests_table():
    try: 
        conn = get_db_connection()
        curs = conn.cursor()
        curs.execute("""
            CREATE TABLE IF NOT EXISTS quests (
            quest_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            name TEXT NOT NULL UNIQUE,
            points INTEGER NOT NULL,
            description TEXT NOT NULL UNIQUE,
            answer TEXT NOT NULL);""")
        conn.commit()
    except sqlite3.Error as e:
        error_message = str(e).lower()
        if "unique constraint" in error_message:
            if "name" in error_message:
                print("Error: Duplicate quest name found")
            elif "description" in error_message:
                print("Error: Duplicate quest description found")
        else:
            print(f"Database error: {e}")
    finally:
        conn.close()


def create_profile_table():
    try: 
        conn = get_db_connection()
        curs = conn.cursor()
        curs.execute("""
            CREATE TABLE IF NOT EXISTS profile (
            profile_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            user_id INTEGER NOT NULL UNIQUE,
            photo TEXT,
            prof_description TEXT,
            points INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE);""")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def create_completed_quests_table():
    try:
        conn = get_db_connection()
        curs = conn.cursor()
        curs.execute("""
            CREATE TABLE IF NOT EXISTS completed_quests (
            comp_quest_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            user_id INTEGER NOT NULL,
            quest_id INTEGER NOT NULL,
            completion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
            FOREIGN KEY (quest_id) REFERENCES quests (quest_id) ON DELETE CASCADE,
            UNIQUE(user_id, quest_id));""")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def create_feedback_table():
    try:
        conn = get_db_connection()
        curs = conn.cursor()
        curs.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            text TEXT NOT NULL,
            rating INTEGER NOT NULL);""")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def create_registration_log_table():
    try:
        conn = get_db_connection()
        curs = conn.cursor()
        curs.execute("""
            CREATE TABLE IF NOT EXISTS registration_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            username TEXT NOT NULL,
            gmail TEXT NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def log_registration(username, gmail):
    try:
        conn = get_db_connection()
        curs = conn.cursor()
        curs.execute("""
            INSERT INTO registration_log (username, gmail)
            VALUES (?, ?)""", (username, gmail))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error logging registration: {e}")
    finally:
        conn.close()


def create_tables():
    create_user_table()
    create_quests_table()
    create_profile_table()
    create_completed_quests_table()
    create_feedback_table()
    create_registration_log_table()
