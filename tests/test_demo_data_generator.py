import pytest
import os
import pandas as pd
from utils.demo_data_generator import DemoDataGenerator
import json

@pytest.fixture
def generator():
    return DemoDataGenerator()

def test_directory_creation(generator):
    """Prueba la creación del directorio demo"""
    assert os.path.exists(generator.demo_dir)
    assert os.path.isdir(generator.demo_dir)

def test_historical_data_generation(generator):
    """Prueba la generación de datos históricos"""
    years = 2
    df = generator.generate_historical_data(years=years)
    
    # Verificar estructura del DataFrame
    assert isinstance(df, pd.DataFrame)
    
    # Verificar columnas requeridas
    required_columns = ['fecha', 'concepto', 'entidad', 'tipo', 'importe']
    assert all(col in df.columns for col in required_columns)
    
    # Verificar que los datos cubren el período correcto
    fecha_min = pd.Timestamp.now() - pd.DateOffset(years=years)
    assert all(pd.to_datetime(df['fecha']) >= fecha_min)
    
    # Verificar tipos de operaciones
    assert set(df['tipo'].unique()) == {'Ingreso', 'Gasto'}
    
    # Verificar que hay múltiples registros por mes (gastos fijos e ingresos variables)
    monthly_counts = df.groupby(pd.to_datetime(df['fecha']).dt.to_period('M')).size()
    assert all(count > 5 for count in monthly_counts)  # al menos 5 operaciones por mes

def test_sample_pdf_generation(generator):
    """Prueba la generación del PDF"""
    generator.generate_sample_pdf()
    pdf_path = os.path.join(generator.demo_dir, "informe_financiero_2023.pdf")
    
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0

def test_generate_all_demo_data(generator):
    """Prueba la generación de todos los datos demo"""
    paths = generator.generate_all_demo_data()
    
    # Verificar que todos los archivos existen
    assert os.path.exists(paths['csv_path'])
    assert os.path.exists(paths['pdf_path'])
    assert os.path.exists(paths['metadata_path'])
    
    # Verificar metadata
    with open(paths['metadata_path'], 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    assert 'fecha_generacion' in metadata
    assert 'archivos_generados' in metadata
    assert 'resumen_financiero' in metadata  # Cambiado de 'metricas_resumen'

if __name__ == '__main__':
    pytest.main([__file__])