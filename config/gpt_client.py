import openai
import base64
import json
import logging
import time
import os
from typing import Dict, Any, Optional, List
from .config import Config
from utils.database import DatabaseManager
from googleapiclient.discovery import build
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class GPTClient:
    def __init__(self):
        load_dotenv()
        Config.validate_config()
        self.api_key = Config.get_api_key()
        self.search_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        openai.api_key = self.api_key
        self.model = Config.MODEL_PRIMARY
        self.db = DatabaseManager(Config.DB_PATH)
        self.rate_limit_delay = 1
        self.context_file = "company_context.txt"

    def _search_chrome(self, sector: str, region: str) -> str:
        """Realiza búsqueda en Chrome usando Custom Search API"""
        try:
            service = build("customsearch", "v1", developerKey=self.search_api_key)
            query = f"Información relevante para realizar proyecciones financieras para el {sector} en {region} durante los próximos meses"
            
            result = service.cse().list(
                q=query,
                cx=self.search_engine_id,
                num=5
            ).execute()

            search_results = []
            for item in result.get('items', []):
                search_results.append({
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', '')
                })

            return json.dumps(search_results, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error en búsqueda Chrome: {e}")
            return ""

    def generate_company_context(self, sector: str, region: str) -> None:
        """Genera y guarda el contexto de la empresa basado en búsqueda y análisis GPT"""
        try:
            # Eliminar contexto anterior si existe
            if os.path.exists(self.context_file):
                os.remove(self.context_file)

            # Realizar búsqueda en Chrome
            search_results = self._search_chrome(sector, region)

            # Generar contexto con GPT
            messages = [
                {"role": "system", "content": """Eres un experto analista financiero. 
                Genera un contexto detallado para proyecciones financieras basado en la información proporcionada."""},
                {"role": "user", "content": f"""
                    Analiza la siguiente información sobre el sector {sector} en {region} 
                    y genera un contexto detallado para proyecciones financieras:

                    {search_results}

                    El contexto debe incluir:
                    1. Situación actual del sector en la región
                    2. Tendencias principales
                    3. Factores de riesgo
                    4. Oportunidades de crecimiento
                    5. Indicadores clave a monitorear
                """}
            ]

            context = self._make_request(messages, temperature=0.7)

            # Guardar contexto en archivo
            with open(self.context_file, 'w', encoding='utf-8') as f:
                f.write(context)

            logger.info(f"Contexto generado y guardado para {sector} en {region}")

        except Exception as e:
            logger.error(f"Error generando contexto: {e}")
            raise

    def _get_saved_context(self) -> str:
        """Recupera el contexto guardado si existe"""
        try:
            if os.path.exists(self.context_file):
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception as e:
            logger.error(f"Error leyendo contexto: {e}")
            return ""

    def _make_request(self, messages: list, temperature: float = 0.7) -> str:
        cache_key = str(messages)
        cached_response = self.db.get_cached_response(cache_key)
        if cached_response:
            return cached_response

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=Config.MAX_TOKENS
            )
            result = response.choices[0].message.content
            self.db.cache_gpt_response(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error en GPT request: {e}")
            if self.model == Config.MODEL_PRIMARY:
                self.model = Config.MODEL_FALLBACK
                time.sleep(self.rate_limit_delay)
                return self._make_request(messages, temperature)
            raise

    def generate_financial_opinion(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Genera una opinión financiera basada en los datos proporcionados"""
        try:
            saved_context = self._get_saved_context()
            
            messages = [
                {"role": "system", "content": f"""Eres un experto en análisis financiero.
                
                Contexto actual del sector:
                {saved_context}"""},
                {"role": "user", "content": f"""
                    Sector: {context.get('sector', 'No especificado')}
                    Región: {context.get('region', 'No especificada')}
                    
                    Analiza estos datos y proporciona recomendaciones concretas:
                    {json.dumps(data, ensure_ascii=False, indent=2)}
                """}
            ]
            return self._make_request(messages)
        except Exception as e:
            logger.error(f"Error generando opinión financiera: {e}")
            raise

    def generate_scenarios(self, financial_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Genera escenarios financieros basados en los datos y contexto proporcionados"""
        try:
            # Obtener el contexto guardado
            saved_context = self._get_saved_context()
            
            messages = [
                {"role": "system", "content": f"""Eres un experto analista financiero 
                especializado en generar escenarios detallados.
                
                Contexto actual del sector:
                {saved_context}"""},
                {"role": "user", "content": f"""
                    Analiza, considerando lo expuesto en el contexto anterior la siguiente situación para una empresa del sector
                    {context.get('sector', 'No especificado')} 
                    en {context.get('region', 'No especificada')}:

                    {financial_data}
                """}
            ]
            return self._make_request(messages, temperature=0.7)
            
        except Exception as e:
            logger.error(f"Error generando escenarios: {e}")
            raise

    def process_pdf(self, file_data) -> dict:
        try:
            import PyPDF2
            if hasattr(file_data, 'read'):
                pdf = PyPDF2.PdfReader(file_data)
            else:
                with open(file_data, 'rb') as f:
                    pdf = PyPDF2.PdfReader(f)
            
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            
            chunks = [text[i:i+2000] for i in range(0, len(text), 2000)]
            
            all_entries = []
            for chunk in chunks:
                time.sleep(self.rate_limit_delay)
                result = self._make_extraction_request(chunk)
                all_entries.extend(result.get('entries', []))

            best_entries = self._select_best_entries(all_entries)
            summary = self._generate_summary(best_entries)
            
            return {
                'entries': best_entries,
                'summary': summary
            }

        except Exception as e:
            logger.error(f"Error procesando PDF: {e}")
            raise

    def _make_extraction_request(self, text: str) -> dict:
        messages = [
            {"role": "system", "content": """Eres un experto en extracción de datos financieros.
            Solo extrae entradas cuando tengas alta confianza en la información."""},
            {"role": "user", "content": f"""
                Extrae las operaciones financieras donde identifiques claramente estos campos:
                - Fecha (YYYY-MM-DD)
                - Concepto
                - Entidad
                - Importe
                - Tipo (Ingreso/Gasto)
                
                Devuelve un JSON con este formato:
                {{
                    "entries": [
                        {{
                            "fecha": "YYYY-MM-DD",
                            "concepto": "texto",
                            "entidad": "texto",
                            "importe": 0.0,
                            "tipo": "Ingreso/Gasto",
                            "confianza": 0.0
                        }}
                    ]
                }}
            """},
            {"role": "user", "content": text}
        ]
        
        result = self._make_request(messages, temperature=0.1)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"entries": []}

    def _select_best_entries(self, all_entries: list) -> list:
        valid_entries = [entry for entry in all_entries if entry.get('confianza', 0) > 0.7]
        
        unique_entries = {}
        for entry in valid_entries:
            key = f"{entry['fecha']}-{entry['concepto']}-{entry['entidad']}"
            if key not in unique_entries or entry.get('confianza', 0) > unique_entries[key].get('confianza', 0):
                unique_entries[key] = entry
        
        final_entries = list(unique_entries.values())
        for entry in final_entries:
            entry.pop('confianza', None)
        
        return final_entries

    def _generate_summary(self, entries: list) -> str:
        try:
            total_ingresos = sum(float(entry['importe']) for entry in entries if entry.get('tipo') == 'Ingreso')
            total_gastos = sum(float(entry['importe']) for entry in entries if entry.get('tipo') == 'Gasto')
            
            resumen_prompt = f"""
            Genera un resumen ejecutivo breve con esta información:
            - Total de operaciones: {len(entries)}
            - Total ingresos: {total_ingresos:,.2f}€
            - Total gastos: {total_gastos:,.2f}€
            - Balance: {total_ingresos - total_gastos:,.2f}€
            """
            
            messages = [
                {"role": "system", "content": "Eres un experto en análisis financiero. Genera resúmenes concisos y ejecutivos."},
                {"role": "user", "content": resumen_prompt}
            ]
            
            return self._make_request(messages, temperature=0.3)
        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return "No se pudo generar el resumen"