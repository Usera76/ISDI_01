from typing import Dict, Any, Union, Optional
import pandas as pd
import json
import logging
import re
from config.gpt_client import GPTClient

logger = logging.getLogger(__name__)

class ScenarioGenerator:
   def __init__(self, gpt_client: GPTClient):
       self.gpt_client = gpt_client

   def generate_scenarios(self, financial_data: Dict[str, float], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        prompt = self._format_financial_data(financial_data)
        context = context or {}
        scenarios_str = self.gpt_client.generate_scenarios(prompt, context)
        
        try:
            scenarios = json.loads(scenarios_str)
            return self._validate_scenarios(scenarios)
        except json.JSONDecodeError:
            return self._format_unstructured_response(scenarios_str)
    except Exception as e:
        logger.error(f"Error generating scenarios: {e}")
        raise

   def generate_detailed_analysis(self, scenarios: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
       return self.gpt_client.generate_financial_opinion(json.dumps(scenarios), context or {})

   def _format_financial_data(self, data: Dict[str, float]) -> str:
    return f"""Por favor, analiza la siguiente situación financiera y genera tres escenarios (base, optimista y pesimista) con el siguiente formato estructurado:

    Datos Actuales:
    - Ingresos: {data.get('ingresos', 0):,.2f}€
    - Gastos: {data.get('gastos', 0):,.2f}€
    - Margen: {data.get('ingresos', 0) - data.get('gastos', 0):,.2f}€

    Te pido que tengas en cuenta:
    1. Las proyecciones tienen que tener lógica con los datos actuales
    2. La proyección pesimista debe tener en cuenta cómo se ven afectados ingresos y gastos si se realizan los escenarios negativos para el sector de referencia 
    en la provincia de referencia.
    3. La proyección optimista debe tener en cuenta cómo se ven afectados ingresos y gastos si se realizan los escenarios positivos para el sector de referencia 
    en la provincia de referencia.
    4. Es lógico que el escenario pesimista ofrezca un margen menor al base y éste menor al optimista.

    Para cada escenario, incluye:
    1. Una descripción detallada
    2. Proyecciones numéricas de ingresos, gastos, beneficio y margen
    3. Lista de supuestos clave

    Responde en formato JSON con esta estructura:
    {{
        "base": {{
            "descripcion": "",
            "proyecciones": {{"ingresos": 0, "gastos": 0, "beneficio": 0, "margen": 0}},
            "supuestos": []
        }},
        "optimista": {{...}},
        "pesimista": {{...}}
    }}"""

   def _validate_scenarios(self, scenarios: Dict[str, Any]) -> Dict[str, Any]:
       required_scenarios = {'base', 'optimista', 'pesimista'}
       required_fields = {'descripcion', 'proyecciones', 'supuestos'}
       
       missing_scenarios = required_scenarios - set(scenarios.keys())
       if missing_scenarios:
           raise ValueError(f"Faltan escenarios: {missing_scenarios}")
           
       for name, data in scenarios.items():
           missing_fields = required_fields - set(data.keys())
           if missing_fields:
               raise ValueError(f"Faltan campos en {name}: {missing_fields}")
       
       return scenarios

   def _format_unstructured_response(self, response: str) -> Dict[str, Any]:
       scenarios = {
           'base': {'descripcion': '', 'proyecciones': {}, 'supuestos': []},
           'optimista': {'descripcion': '', 'proyecciones': {}, 'supuestos': []},
           'pesimista': {'descripcion': '', 'proyecciones': {}, 'supuestos': []}
       }

       current_scenario = None
       current_section = None
       
       for line in response.split('\n'):
           line = line.strip()
           if not line: continue

           lower_line = line.lower()
           for scenario in scenarios:
               if f"escenario {scenario}" in lower_line:
                   current_scenario = scenario
                   current_section = 'descripcion'
                   break
                   
           if not current_scenario: continue

           if 'supuestos' in lower_line:
               current_section = 'supuestos'
           elif current_section == 'descripcion':
               scenarios[current_scenario]['descripcion'] += line + '\n'
           elif current_section == 'supuestos' and line.startswith('-'):
               scenarios[current_scenario]['supuestos'].append(line[1:].strip())
           
           for metric in ['ingresos', 'gastos', 'beneficio', 'margen']:
               if metric in lower_line:
                   value = float(re.findall(r'[-+]?\d*\.?\d+', line.replace(',', ''))[0])
                   scenarios[current_scenario]['proyecciones'][metric] = value

       return scenarios