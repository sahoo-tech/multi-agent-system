import sqlite3
import threading
import json
from datetime import datetime

class SharedMemory:
    def __init__(self, db_path='memory.db'):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._initialize_db()

    def _initialize_db(self):
        try:
            with self.lock, sqlite3.connect(self.db_path, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS metadata (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source TEXT,
                        type TEXT,
                        intent TEXT,
                        timestamp TEXT
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS extracted_fields (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        agent TEXT,
                        data TEXT,
                        timestamp TEXT
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT,
                        metadata TEXT,
                        timestamp TEXT
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise

    def add_metadata(self, metadata: dict):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO metadata (source, type, intent, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (
                metadata.get('source'),
                metadata.get('type'),
                metadata.get('intent'),
                metadata.get('timestamp', datetime.utcnow().isoformat())
            ))
            conn.commit()

    def add_extracted_fields(self, agent: str, data: dict):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO extracted_fields (agent, data, timestamp)
                VALUES (?, ?, ?)
            ''', (
                agent,
                json.dumps(data),
                datetime.utcnow().isoformat()
            ))
            conn.commit()

    def add_conversation(self, conversation_id: str, metadata: dict):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO conversations (conversation_id, metadata, timestamp)
                VALUES (?, ?, ?)
            ''', (
                conversation_id,
                json.dumps(metadata),
                datetime.utcnow().isoformat()
            ))
            conn.commit()

    def get_metadata(self):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM metadata')
            rows = cursor.fetchall()
            return rows

    def get_extracted_fields(self):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM extracted_fields')
            rows = cursor.fetchall()
            return rows

    def get_conversations(self):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM conversations')
            rows = cursor.fetchall()
            return rows
