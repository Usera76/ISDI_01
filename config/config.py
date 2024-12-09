import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    @classmethod
    def get_api_key(cls):
        return os.getenv('OPENAI_API_KEY')

    MODEL_PRIMARY = "gpt-4"
    MODEL_FALLBACK = "gpt-3.5-turbo"
    MAX_TOKENS = 2000
    
    DB_PATH = "data/finance.db"
    CACHE_ENABLED = True
    CACHE_TTL = 86400  # 24 hours
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    DEMO_DIR = os.path.join(DATA_DIR, 'demo')
    
    @classmethod
    def validate_config(cls):
        """Valida la configuración y crea directorios necesarios"""
        if not cls.get_api_key():
            raise ValueError("OPENAI_API_KEY no está configurada")
            
        # Crear directorios necesarios
        for dir_path in [cls.DATA_DIR, cls.DEMO_DIR]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)