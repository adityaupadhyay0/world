import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

class EventLog:
    def __init__(self, db_path: str = "stratum_events.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    source_id TEXT,
                    data TEXT NOT NULL,
                    cause TEXT
                )
            """)
            conn.commit()

    def log_event(self, event_type: str, data: Dict[str, Any], source_id: Optional[str] = None, cause: Optional[str] = None):
        timestamp = datetime.now(timezone.utc).isoformat()
        data_json = json.dumps(data)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO events (timestamp, event_type, source_id, data, cause) VALUES (?, ?, ?, ?, ?)",
                (timestamp, event_type, source_id, data_json, cause)
            )
            conn.commit()

    def get_events(self, source_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        query = "SELECT * FROM events"
        params = []
        if source_id:
            query += " WHERE source_id = ?"
            params.append(source_id)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        events = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            for row in cursor:
                events.append({
                    "id": row[0],
                    "timestamp": row[1],
                    "event_type": row[2],
                    "source_id": row[3],
                    "data": json.loads(row[4]),
                    "cause": row[5]
                })
        return events
