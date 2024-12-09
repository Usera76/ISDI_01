import pytest
from visualization.scenario_visualizer import ScenarioVisualizer
import plotly.graph_objects as go
import os
import numpy as np

@pytest.fixture
def visualizer():
    return ScenarioVisualizer()

@pytest.fixture
def sample_scenarios():
    return {
        'base': {
            'proyecciones': {
                'ingresos': 1000000,
                'crecimiento_ingresos': '10%',
                'margen': '15%'
            }
        },
        'optimista': {
            'proyecciones': {
                'ingresos': 1200000,
                'crecimiento_ingresos': '20%',
                'margen': '18%'
            }
        },
        'pesimista': {
            'proyecciones': {
                'ingresos': 800000,
                'crecimiento_ingresos': '5%',
                'margen': '12%'
            }
        }
    }

def test_create_comparison_chart(visualizer, sample_scenarios):
    fig = visualizer.create_comparison_chart(sample_scenarios, 'ingresos')
    
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert len(fig.data[0].x) == 3
    assert len(fig.data[0].y) == 3
    
    # Verificar valores usando numpy para comparar los valores numéricos
    expected = np.array([1000000, 1200000, 800000])
    np.testing.assert_array_equal(np.array(fig.data[0].y), expected)

def test_create_metrics_dashboard(visualizer, sample_scenarios):
    metrics = ['ingresos', 'margen']
    fig = visualizer.create_metrics_dashboard(sample_scenarios, metrics)
    
    assert isinstance(fig, go.Figure)
    # Para 2 métricas y 3 escenarios, deberíamos tener 6 barras
    assert len(fig.data) == 6

def test_create_timeline_chart(visualizer, sample_scenarios):
    fig = visualizer.create_timeline_chart(sample_scenarios, 'ingresos')
    
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 3  # Un trazo por escenario
    
    # Verificar que cada línea tiene 4 puntos (períodos por defecto)
    for trace in fig.data:
        assert len(trace.x) == 4
        assert len(trace.y) == 4

def test_export_to_html(visualizer, sample_scenarios, tmp_path):
    # Crear un gráfico
    fig = visualizer.create_comparison_chart(sample_scenarios, 'ingresos')
    
    # Exportar a un archivo temporal
    export_path = os.path.join(tmp_path, "test_chart.html")
    visualizer.export_to_html(fig, export_path)
    
    # Verificar que el archivo existe y no está vacío
    assert os.path.exists(export_path)
    assert os.path.getsize(export_path) > 0