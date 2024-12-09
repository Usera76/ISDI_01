import pytest
from scenarios.scenario_generator import ScenarioGenerator
from unittest.mock import Mock

@pytest.fixture
def mock_gpt_client():
    mock = Mock()
    mock.generate_scenarios.return_value = """
    {
        "base": {
            "descripcion": "Escenario base",
            "proyecciones": {"ingresos": 1000000},
            "supuestos": ["Supuesto 1"]
        },
        "optimista": {
            "descripcion": "Escenario optimista",
            "proyecciones": {"ingresos": 1200000},
            "supuestos": ["Supuesto 2"]
        },
        "pesimista": {
            "descripcion": "Escenario pesimista",
            "proyecciones": {"ingresos": 800000},
            "supuestos": ["Supuesto 3"]
        }
    }
    """
    mock.generate_financial_opinion.return_value = "Análisis detallado de prueba"
    return mock

@pytest.fixture
def scenario_generator(mock_gpt_client):
    return ScenarioGenerator(mock_gpt_client)

@pytest.fixture
def sample_financial_data():
    return {
        "ingresos_actuales": 1000000,
        "gastos_actuales": 800000,
        "margen_actual": 200000,
        "crecimiento_historico": "20%"
    }

def test_generate_scenarios(scenario_generator, sample_financial_data):
    context = {
        "sector": "Tecnología",
        "region": "Madrid"
    }
    
    scenarios = scenario_generator.generate_scenarios(str(sample_financial_data), context)
    assert isinstance(scenarios, dict)
    assert all(key in scenarios for key in ['base', 'optimista', 'pesimista'])
    
    for scenario in scenarios.values():
        assert 'descripcion' in scenario
        assert 'proyecciones' in scenario
        assert 'supuestos' in scenario

def test_generate_detailed_analysis(scenario_generator):
    test_scenarios = {
        "base": {
            "descripcion": "Escenario base con crecimiento moderado",
            "proyecciones": {"crecimiento": "10%"},
            "supuestos": ["Mercado estable", "Sin cambios regulatorios"]
        },
        "optimista": {
            "descripcion": "Escenario optimista con alto crecimiento",
            "proyecciones": {"crecimiento": "20%"},
            "supuestos": ["Expansión exitosa", "Nuevos productos"]
        },
        "pesimista": {
            "descripcion": "Escenario pesimista con desafíos",
            "proyecciones": {"crecimiento": "5%"},
            "supuestos": ["Recesión económica", "Competencia aumentada"]
        }
    }
    
    analysis = scenario_generator.generate_detailed_analysis(test_scenarios)
    assert isinstance(analysis, str)
    assert len(analysis) > 0

def test_format_unstructured_response(scenario_generator):
    unstructured_response = """
    Escenario Base:
    Crecimiento moderado del 10%
    Ingresos esperados: 1000000
    
    Escenario Optimista:
    Fuerte crecimiento del 20%
    Ingresos esperados: 1200000
    
    Escenario Pesimista:
    Crecimiento limitado del 5%
    Ingresos esperados: 800000
    """
    
    scenarios = scenario_generator._format_unstructured_response(unstructured_response)
    assert isinstance(scenarios, dict)
    assert all(key in scenarios for key in ['base', 'optimista', 'pesimista'])
    assert all('descripcion' in scenario for scenario in scenarios.values())

def test_validate_scenarios_missing_scenario(scenario_generator):
    incomplete_scenarios = {
        "base": {
            "descripcion": "test",
            "proyecciones": {},
            "supuestos": []
        },
        "optimista": {
            "descripcion": "test",
            "proyecciones": {},
            "supuestos": []
        }
    }
    
    with pytest.raises(ValueError, match="Faltan los siguientes escenarios:.*pesimista"):
        scenario_generator._validate_scenarios(incomplete_scenarios)

def test_validate_scenarios_missing_fields(scenario_generator):
    scenarios_missing_fields = {
        "base": {
            "descripcion": "test"
        },
        "optimista": {
            "descripcion": "test",
            "proyecciones": {},
            "supuestos": []
        },
        "pesimista": {
            "descripcion": "test",
            "proyecciones": {},
            "supuestos": []
        }
    }
    
    with pytest.raises(ValueError, match="Faltan campos en el escenario.*"):
        scenario_generator._validate_scenarios(scenarios_missing_fields)