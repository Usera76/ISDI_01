import pytest
import os
from datetime import datetime
from utils.database import DatabaseManager

@pytest.fixture
def db_manager():
    test_db_path = "test_finance.db"
    db = DatabaseManager(test_db_path)
    yield db
    # Limpiar después de las pruebas
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_gpt_cache(db_manager):
    prompt = "test prompt"
    response = "test response"
    
    # Guardar en caché
    db_manager.cache_gpt_response(prompt, response)
    
    # Recuperar de caché
    cached = db_manager.get_cached_response(prompt)
    assert cached == response

def test_store_financial_data(db_manager):
    date = datetime.now()
    test_operations = [
        {
            'fecha': date,
            'concepto': 'Electricidad',
            'entidad': 'Iberdrola',
            'tipo': 'Gasto',
            'importe': 500.0
        },
        {
            'fecha': date,
            'concepto': 'Servicios Profesionales',
            'entidad': 'Cliente A',
            'tipo': 'Ingreso',
            'importe': 1500.0
        }
    ]
    
    for op in test_operations:
        db_manager.add_operation(**op)
    
    data = db_manager.get_historical_data()
    assert len(data) == 2
    assert data['importe'].sum() == 2000.0

def test_historical_data_filtering(db_manager):
    # Insertar datos de prueba
    date = datetime.now()
    test_data = [
        {'fecha': date, 'concepto': 'Test1', 'entidad': 'Corp1', 'tipo': 'Ingreso', 'importe': 1000.0},
        {'fecha': date, 'concepto': 'Test2', 'entidad': 'Corp2', 'tipo': 'Gasto', 'importe': 500.0}
    ]
    
    for data in test_data:
        db_manager.add_operation(**data)
    
    # Probar filtros
    ingresos = db_manager.get_historical_data(tipo='Ingreso')
    assert len(ingresos) == 1
    assert ingresos.iloc[0]['importe'] == 1000.0
    
    filtered_by_entity = db_manager.get_historical_data(entidad='Corp1')
    assert len(filtered_by_entity) == 1
    assert filtered_by_entity.iloc[0]['entidad'] == 'Corp1'