import pytest
import pandas as pd
import numpy as np
from ml_analysis.clustering import FinancialClustering
from config.gpt_client import GPTClient

@pytest.fixture
def sample_data():
    """Crear datos de ejemplo para testing"""
    np.random.seed(42)
    
    # Crear datos financieros simulados
    n_samples = 100
    data = {
        'ingresos': np.random.normal(1000000, 200000, n_samples),
        'gastos': np.random.normal(800000, 150000, n_samples),
        'margen': np.random.normal(200000, 50000, n_samples),
        'empleados': np.random.normal(50, 10, n_samples)
    }
    
    return pd.DataFrame(data)

@pytest.fixture
def default_context():
    """Contexto por defecto para pruebas"""
    return {
        "sector": "Tecnología",
        "region": "Madrid"
    }

@pytest.fixture
def clustering_instance():
    """Crear instancia de FinancialClustering"""
    gpt_client = GPTClient()
    return FinancialClustering(gpt_client)

def test_prepare_data(clustering_instance, sample_data):
    features = ['ingresos', 'gastos', 'margen']
    prepared_data = clustering_instance.prepare_data(sample_data, features)
    
    assert isinstance(prepared_data, pd.DataFrame)
    assert list(prepared_data.columns) == features
    assert prepared_data.isna().sum().sum() == 0

def test_fit_predict(clustering_instance, sample_data, default_context):
    # Preparar datos
    features = ['ingresos', 'gastos', 'margen']
    prepared_data = clustering_instance.prepare_data(sample_data, features)
    
    # Realizar clustering con el contexto de prueba
    data_with_clusters, results = clustering_instance.fit_predict(prepared_data, context=default_context)
    
    # Verificar resultados
    assert isinstance(data_with_clusters, pd.DataFrame)
    assert 'Cluster' in data_with_clusters.columns
    assert isinstance(results, dict)
    assert 'summary' in results
    assert 'interpretation' in results
    
    # Verificar que tenemos 3 clusters (valor por defecto)
    unique_clusters = data_with_clusters['Cluster'].unique()
    assert len(unique_clusters) == 3
    
    # Verificar que el resumen contiene la información esperada
    for i in range(3):
        cluster_key = f'cluster_{i}'
        assert cluster_key in results['summary']
        cluster_info = results['summary'][cluster_key]
        assert 'size' in cluster_info
        assert 'percentage' in cluster_info
        assert 'centroid' in cluster_info
        assert 'min_values' in cluster_info
        assert 'max_values' in cluster_info
        assert 'mean_values' in cluster_info

def test_clustering_with_different_n_clusters(clustering_instance, sample_data):
    features = ['ingresos', 'gastos', 'margen']
    prepared_data = clustering_instance.prepare_data(sample_data, features)
    
    # Probar con 4 clusters
    data_with_clusters, results = clustering_instance.fit_predict(prepared_data, n_clusters=4)
    unique_clusters = data_with_clusters['Cluster'].unique()
    assert len(unique_clusters) == 4

if __name__ == '__main__':
    pytest.main([__file__])