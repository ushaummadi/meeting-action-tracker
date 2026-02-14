import sqlite3
import json
import os
import pandas as pd

DB_PATH = "data/transcripts.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcript TEXT,
            action_items TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS action_items (
            id INTEGER,
            ts_id INTEGER,
            task TEXT,
            owner TEXT,
            due_date TEXT,
            done BOOLEAN DEFAULT 0,
            PRIMARY KEY (id, ts_id),
            FOREIGN KEY (ts_id) REFERENCES transcripts (id)
        )
    ''')

    conn.commit()
    conn.close()


def add_transcript(transcript, action_items):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO transcripts (transcript, action_items) VALUES (?, ?)",
        (transcript, json.dumps(action_items))
    )
    ts_id = c.lastrowid
    conn.commit()
    conn.close()
    return ts_id


def get_recent_transcripts(limit=5):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM transcripts ORDER BY created_at DESC LIMIT ?",
        conn,
        params=(limit,)
    )
    conn.close()

    if df.empty:
        return []

    df['action_items'] = df['action_items'].apply(json.loads)
    df['created_at'] = pd.to_datetime(df['created_at'])
    return df.to_dict('records')


def save_action_items(ts_id, items):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("DELETE FROM action_items WHERE ts_id=?", (ts_id,))

    for i, item in enumerate(items):
        c.execute(
            "INSERT INTO action_items (id, ts_id, task, owner, due_date, done) VALUES (?, ?, ?, ?, ?, ?)",
            (i, ts_id, item.get('task', ''), item.get('owner', ''),
             item.get('due_date', ''), False)
        )

    conn.commit()
    conn.close()


def get_action_items(ts_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM action_items WHERE ts_id=? ORDER BY id",
        conn,
        params=(ts_id,)
    )
    conn.close()

    if df.empty:
        return []

    return df.to_dict('records')


def update_action_item(item_id, ts_id, task, owner, due_date, done):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE action_items SET task=?, owner=?, due_date=?, done=? WHERE id=? AND ts_id=?",
        (task, owner, due_date, done, item_id, ts_id)
    )
    conn.commit()
    conn.close()


def delete_action_item(item_id, ts_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM action_items WHERE id=? AND ts_id=?", (item_id, ts_id))
    conn.commit()
    conn.close()


def delete_transcript(ts_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM transcripts WHERE id=?", (ts_id,))
    c.execute("DELETE FROM action_items WHERE ts_id=?", (ts_id,))
    conn.commit()
    conn.close()
