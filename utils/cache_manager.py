import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from config.config import Config

class CacheManager:
    def __init__(self):
        self.db_path = Config.DB_PATH
        self._initialize_cache()

    def _initialize_cache(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS gpt_cache (
                    prompt_hash TEXT PRIMARY KEY,
                    prompt TEXT,
                    response TEXT,
                    timestamp DATETIME,
                    expires_at DATETIME
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON gpt_cache(expires_at)")

    def get(self, prompt: str) -> Optional[str]:
        prompt_hash = self._hash_prompt(prompt)
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "SELECT response FROM gpt_cache WHERE prompt_hash = ? AND expires_at > ?",
                (prompt_hash, datetime.now())
            ).fetchone()
            return result[0] if result else None

    def set(self, prompt: str, response: str):
        prompt_hash = self._hash_prompt(prompt)
        expires_at = datetime.now() + timedelta(seconds=Config.CACHE_TTL)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO gpt_cache VALUES (?, ?, ?, ?, ?)",
                (prompt_hash, prompt, response, datetime.now(), expires_at)
            )

    def _hash_prompt(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()