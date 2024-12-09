import sqlite3
import json
from datetime import datetime, timedelta
import pandas as pd
from typing import Optional, Dict, Any

class DatabaseManager:
    def __init__(self, db_path: str = "data/finance.db"):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            # Tabla para operaciones financieras
            conn.execute("""
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha DATE,
                    concepto TEXT,
                    entidad TEXT,
                    tipo TEXT CHECK(tipo IN ('Ingreso', 'Gasto')),
                    importe REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla para caché de GPT
            conn.execute("""
                CREATE TABLE IF NOT EXISTS gpt_cache (
                    prompt_hash TEXT PRIMARY KEY,
                    prompt TEXT,
                    response TEXT,
                    timestamp DATETIME,
                    expires_at DATETIME
                )
            """)
            
            # Índices
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fecha ON operations(fecha)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tipo ON operations(tipo)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_concepto ON operations(concepto)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entidad ON operations(entidad)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON gpt_cache(expires_at)")

    def add_operation(self, fecha: datetime, concepto: str, entidad: str, 
                     tipo: str, importe: float):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO operations (fecha, concepto, entidad, tipo, importe)
                    VALUES (?, ?, ?, ?, ?)
                """, (fecha.strftime('%Y-%m-%d'), concepto, entidad, tipo, importe))
        except Exception as e:
            raise Exception(f"Error al añadir operación: {str(e)}")

    def get_historical_data(self, concepto: Optional[str] = None,
                          entidad: Optional[str] = None,
                          tipo: Optional[str] = None) -> pd.DataFrame:
        query = "SELECT * FROM operations WHERE 1=1"
        params = []

        if concepto:
            query += " AND concepto LIKE ?"
            params.append(f"%{concepto}%")
        if entidad:
            query += " AND entidad LIKE ?"
            params.append(f"%{entidad}%")
        if tipo:
            query += " AND tipo = ?"
            params.append(tipo)

        query += " ORDER BY fecha DESC"

        try:
            with sqlite3.connect(self.db_path) as conn:
                return pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            raise Exception(f"Error al recuperar datos históricos: {str(e)}")

    def cache_gpt_response(self, prompt: str, response: str):
        try:
            expires_at = datetime.now() + timedelta(seconds=86400)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO gpt_cache 
                    (prompt_hash, prompt, response, timestamp, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (hash(prompt), prompt, response, datetime.now(), expires_at))
        except Exception as e:
            raise Exception(f"Error al cachear respuesta: {str(e)}")

    def get_cached_response(self, prompt: str) -> Optional[str]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute("""
                    SELECT response 
                    FROM gpt_cache 
                    WHERE prompt_hash = ? AND expires_at > ?
                """, (hash(prompt), datetime.now())).fetchone()
                return result[0] if result else None
        except Exception as e:
            raise Exception(f"Error al recuperar caché: {str(e)}")