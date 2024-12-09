import os
import pytest
from config.config import Config
import shutil

def test_config_validation_with_api_key():
    # Simular que existe la API key
    os.environ['OPENAI_API_KEY'] = 'test_key'
    
    try:
        Config.validate_config()
        assert True
    except ValueError:
        assert False, "La validación falló con una API key válida"

# def test_config_validation_without_api_key():
    # Guardar el contenido actual del .env si existe
#    env_backup = None
#    renamed = False  # Indicador para saber si renombramos el archivo
#    try:
#        if os.path.exists('.env'):
#            # Hacer un backup del contenido actual
#            with open('.env', 'r') as f:
#                env_backup = f.read()
#            # Renombrar temporalmente el archivo
#            os.rename('.env', '.env.backup')
#            renamed = True

        # Eliminar la API key del entorno
#        if 'OPENAI_API_KEY' in os.environ:
#            del os.environ['OPENAI_API_KEY']

        # Verificar que la validación lanza el error esperado
#        with pytest.raises(ValueError, match="OPENAI_API_KEY no está configurada"):
#            Config.validate_config()
#    finally:
#        # Restaurar el archivo .env si fue renombrado
#        if renamed and os.path.exists('.env.backup'):
#            os.rename('.env.backup', '.env')

def test_data_directory_creation():
    # Eliminar el directorio de datos si existe
    if os.path.exists(Config.DATA_DIR):
        shutil.rmtree(Config.DATA_DIR)
    
    Config.validate_config()
    assert os.path.exists(Config.DATA_DIR), "El directorio de datos no fue creado"