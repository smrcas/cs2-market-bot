import sqlite3

DB = "market.db"

def init():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS watches(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            skin TEXT,
            last_price REAL DEFAULT 0
        )
        """)
        conn.commit()

def add_watch(user_id, skin):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT INTO watches(user_id, skin) VALUES(?, ?)",
            (user_id, skin)
        )
        conn.commit()

def remove_watch(user_id, skin):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "DELETE FROM watches WHERE user_id=? AND skin=?",
            (user_id, skin)
        )
        conn.commit()

def get_user_watches(user_id):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT skin FROM watches WHERE user_id=?",
            (user_id,)
        )
        return [x[0] for x in c.fetchall()]

def get_all():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        return c.execute("SELECT * FROM watches").fetchall()

def update_price(i, price):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "UPDATE watches SET last_price=? WHERE id=?",
            (price, i)
        )
        conn.commit()