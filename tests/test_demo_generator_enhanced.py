import pytest
from utils.demo_data_generator import DemoDataGenerator
import pandas as pd
import os
import json

@pytest.fixture
def generator():
    return DemoDataGenerator()

def test_historical_data_structure(generator):
    """Prueba la generación de datos históricos"""
    df = generator.generate_historical_data(years=1)
    
    # Verificar columnas requeridas actuales
    required_columns = ['fecha', 'concepto', 'entidad', 'tipo', 'importe']
    
    # Verificar estructura básica
    assert isinstance(df, pd.DataFrame)
    for col in required_columns:
        assert col in df.columns
        
    # Verificar que no hay valores nulos
    assert not df.isnull().any().any()
    
    # Verificar tipos de datos
    assert pd.to_datetime(df['fecha']).dtype == 'datetime64[ns]'
    assert df['importe'].dtype in ['float64', 'int64']
    assert set(df['tipo'].unique()) == {'Ingreso', 'Gasto'}

def test_generate_all_demo_data(generator):
    """Prueba la generación de todos los datos demo"""
    paths = generator.generate_all_demo_data()
    
    # Verificar que todos los archivos existen
    assert os.path.exists(paths['csv_path'])
    assert os.path.exists(paths['pdf_path'])
    assert os.path.exists(paths['metadata_path'])
    
    # Verificar contenido del CSV
    df = pd.read_csv(paths['csv_path'])
    assert len(df) > 0
    assert all(col in df.columns for col in ['fecha', 'concepto', 'entidad', 'tipo', 'importe'])

def test_data_consistency(generator):
    """Prueba la consistencia de los datos financieros"""
    df = generator.generate_historical_data()
    
    # Calcular totales por tipo
    ingresos = df[df['tipo'] == 'Ingreso']['importe'].sum()
    gastos = df[df['tipo'] == 'Gasto']['importe'].sum()
    
    # Verificar que los valores son razonables
    assert ingresos > 0
    assert gastos > 0
    assert ingresos > gastos  # El negocio debería ser rentable
    
    # Verificar que los gastos fijos están presentes
    gastos_fijos = ['Electricidad', 'Agua', 'Internet y Telefonía', 'Alquiler']
    for gasto in gastos_fijos:
        assert not df[df['concepto'] == gasto].empty