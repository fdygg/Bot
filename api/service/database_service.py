import sqlite3
from typing import Optional, Dict, List, Any
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    _instance = None
    _conn = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.startup_time = datetime.now(UTC)
        logger.info(f"""
        DatabaseService initialized:
        Time: 2025-05-28 17:13:34
        User: fdygg
        """)

    def get_connection(self) -> sqlite3.Connection:
        """Get SQLite connection with row factory"""
        if not self._conn:
            self._conn = sqlite3.connect('shop.db', check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            cursor = self._conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA journal_mode = WAL")
        return self._conn

    async def execute_query(self, query: str, params: tuple = None, fetch: bool = True) -> Optional[List[Dict]]:
        """Execute SQL query and return results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            if fetch:
                result = [dict(row) for row in cursor.fetchall()]
                return result
            conn.commit()
            return None
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {str(e)}")
            conn.rollback()
            raise