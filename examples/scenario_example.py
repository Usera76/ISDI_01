import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.gpt_client import GPTClient
from scenarios.scenario_generator import ScenarioGenerator

def main():
    # Datos de ejemplo
    company_info = """
    Empresa de software B2B especializada en soluciones de IA
    - 5 años en el mercado
    - 50 empleados
    - Presencia en España y Portugal
    """
    
    financial_data = {
        "ingresos_actuales": 1000000,
        "gastos_actuales": 800000,
        "margen_actual": 200000,
        "crecimiento_historico": "20%",
        "industria": "Tecnología",
        "mercado": "B2B",
        "metricas_clave": {
            "churn_rate": "5%",
            "cac": 1000,
            "ltv": 5000
        }
    }
    
    # Inicializar generador de escenarios
    gpt_client = GPTClient()
    generator = ScenarioGenerator(gpt_client)
    
    # Generar escenarios
    print("Generando escenarios...")
    scenarios = generator.generate_scenarios(company_info, financial_data)
    
    # Mostrar escenarios
    print("\nEscenarios generados:")
    for scenario_name, scenario_data in scenarios.items():
        print(f"\n{scenario_name.upper()}:")
        print(f"Descripción: {scenario_data['descripcion']}")
        print("Proyecciones:", scenario_data['proyecciones'])
        print("Supuestos:", scenario_data['supuestos'])
    
    # Generar análisis detallado
    print("\nGenerando análisis detallado...")
    analysis = generator.generate_detailed_analysis(scenarios)
    print("\nAnálisis detallado:")
    print(analysis)

if __name__ == "__main__":
    main()