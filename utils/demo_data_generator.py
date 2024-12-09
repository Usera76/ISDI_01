import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from fpdf import FPDF
import json
import sqlite3
from .database import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class DemoDataGenerator:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.demo_dir = os.path.join(self.base_dir, 'data', 'demo')
        self._ensure_demo_directory()
        
    def _ensure_demo_directory(self):
        """Asegura que existe el directorio de datos demo"""
        if not os.path.exists(self.demo_dir):
            os.makedirs(self.demo_dir)
    
    def _cleanup_all_data(self):
        """Limpia los datos de operaciones preservando la caché de GPT"""
        try:
            # Limpiar archivos
            for filename in os.listdir(self.demo_dir):
                file_path = os.path.join(self.demo_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            # Limpiar solo la tabla de operaciones
            db = DatabaseManager()
            with sqlite3.connect(db.db_path) as conn:
                conn.execute("DELETE FROM operations")
                # Reiniciar el autoincrement
                conn.execute("DELETE FROM sqlite_sequence WHERE name='operations'")
            
            logger.info("Limpieza de datos de operaciones realizada")
        except Exception as e:
            logger.error(f"Error durante la limpieza de datos: {str(e)}")
            raise

    def generate_historical_data(self, years: int = 5) -> pd.DataFrame:
        """Genera datos históricos con conceptos y entidades realistas"""
        # Gastos fijos mensuales más realistas para una empresa pequeña
        gastos_fijos = {
            'Electricidad': {'entidad': 'Iberdrola', 'base': 250, 'variacion': 50},
            'Agua': {'entidad': 'Canal Isabel II', 'base': 80, 'variacion': 20},
            'Internet y Telefonía': {'entidad': 'Movistar', 'base': 120, 'variacion': 15},
            'Alquiler': {'entidad': 'Inmobiliaria Centro', 'base': 800, 'variacion': 0},
            'Material Oficina': {'entidad': 'Office Depot', 'base': 150, 'variacion': 50},
            'Seguros': {'entidad': 'Mapfre', 'base': 200, 'variacion': 0},
            'Mantenimiento': {'entidad': 'ServiTech', 'base': 150, 'variacion': 50},
            'Nóminas': {'entidad': 'Personal', 'base': 3500, 'variacion': 500},
            'Seguridad Social': {'entidad': 'TGSS', 'base': 1200, 'variacion': 150},
            'Gestoría': {'entidad': 'AsesoresPlus', 'base': 150, 'variacion': 0},
            'Software y Licencias': {'entidad': 'Varios', 'base': 200, 'variacion': 100}
        }
        
        clientes = [
            'TechSolutions SA', 'Innovatech', 'Desarrollo Digital SL', 
            'Consultoría Avanzada', 'Sistemas Integrados'
        ]
        
        # Definir estacionalidad (1.0 = normal, >1.0 = más actividad, <1.0 = menos actividad)
        estacionalidad = {
            1: 0.8,   # Enero (después de navidades, menos actividad)
            2: 0.9,
            3: 1.0,
            4: 1.1,
            5: 1.2,
            6: 1.1,
            7: 0.7,   # Julio (verano)
            8: 0.5,   # Agosto (vacaciones)
            9: 1.1,   # Septiembre (vuelta al trabajo)
            10: 1.2,
            11: 1.1,
            12: 0.9    # Diciembre (navidades)
        }
        
        data = []
        end_date = datetime.now()
        
        for i in range(years * 12):
            date = end_date - timedelta(days=30*i)
            mes = date.month
            factor_estacional = estacionalidad[mes]
            
            # Gastos fijos mensuales
            for concepto, info in gastos_fijos.items():
                # Algunos gastos como alquiler o seguros no tienen estacionalidad
                es_gasto_estacional = concepto not in ['Alquiler', 'Seguros', 'Gestoría']
                factor = factor_estacional if es_gasto_estacional else 1.0
                
                base_adjusted = info['base'] * factor
                importe = base_adjusted + np.random.normal(0, info['variacion'])
                data.append({
                    'fecha': date.strftime('%Y-%m-%d'),
                    'concepto': concepto,
                    'entidad': info['entidad'],
                    'tipo': 'Gasto',
                    'importe': round(max(importe, 0), 2)
                })
            
            # Ingresos variables más realistas
            num_facturas = np.random.randint(1, 4)  # 1-3 facturas por mes
            for _ in range(num_facturas):
                cliente = np.random.choice(clientes)
                # Base entre 3000-7000€ por factura con estacionalidad
                base_factura = np.random.normal(5000, 1000) * factor_estacional
                # Añadir variación del 20%
                importe = base_factura * np.random.normal(1, 0.2)
                data.append({
                    'fecha': date.strftime('%Y-%m-%d'),
                    'concepto': 'Servicios Profesionales',
                    'entidad': cliente,
                    'tipo': 'Ingreso',
                    'importe': round(max(importe, 0), 2)
                })
        
        df = pd.DataFrame(data)
        df['fecha'] = pd.to_datetime(df['fecha'])
        return df.sort_values('fecha')

    def generate_sample_pdf(self) -> str:
        """Genera un PDF con un informe financiero de ejemplo"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 16)
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Ajustar el ancho efectivo de la página
        page_width = pdf.w - 2 * pdf.l_margin
        
        df = self.generate_historical_data(years=1)
        totals = df.groupby('tipo')['importe'].sum()
        
        sections = [
            ("Resumen Financiero Anual", [
                f"Período: {df['fecha'].min().strftime('%Y-%m-%d')} a {df['fecha'].max().strftime('%Y-%m-%d')}",
                f"Total Ingresos: {totals.get('Ingreso', 0):,.2f} EUR",
                f"Total Gastos: {totals.get('Gasto', 0):,.2f} EUR",
                f"Beneficio Neto: {(totals.get('Ingreso', 0) - totals.get('Gasto', 0)):,.2f} EUR"
            ]),
            ("Análisis de Gastos", [
                "Desglose por concepto:",
                *[f"- {concepto}: {df[df['concepto']==concepto]['importe'].sum():,.2f} EUR"
                  for concepto in df[df['tipo']=='Gasto']['concepto'].unique()]
            ]),
            ("Análisis de Ingresos", [
                "Desglose por cliente:",
                *[f"- {cliente}: {df[df['entidad']==cliente]['importe'].sum():,.2f} EUR"
                  for cliente in df[df['tipo']=='Ingreso']['entidad'].unique()]
            ])
        ]
        
        for title, content in sections:
                pdf.cell(page_width, 10, title, align='C')
                pdf.ln()
                pdf.set_font('Helvetica', '', 12)
                for line in content:
                    pdf.multi_cell(page_width, 10, line)
                pdf.ln(5)
                pdf.set_font('Helvetica', 'B', 16)

        pdf_path = os.path.join(self.demo_dir, "informe_financiero_2023.pdf")
        pdf.output(pdf_path)
        return pdf_path

    def generate_all_demo_data(self):
        """Genera todos los datos de demostración"""
        try:
            # Primero limpiar todos los datos
            self._cleanup_all_data()
            
            # Generar datos históricos
            df = self.generate_historical_data()
            
            # Guardar CSV
            csv_path = os.path.join(self.demo_dir, "datos_historicos.csv")
            df.to_csv(csv_path, index=False)
            
            # Guardar en base de datos
            db = DatabaseManager()
            for _, row in df.iterrows():
                db.add_operation(
                    fecha=pd.to_datetime(row['fecha']),  # Convertir a datetime
                    concepto=row['concepto'],
                    entidad=row['entidad'],
                    tipo=row['tipo'],
                    importe=row['importe']
                )
            
            # Generar PDF
            pdf_path = self.generate_sample_pdf()
            
            # Generar metadata
            metadata = {
                'fecha_generacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'archivos_generados': [
                    'datos_historicos.csv',
                    'informe_financiero_2023.pdf'
                ],
                'registros_totales': len(df),
                'resumen_financiero': {
                    'total_ingresos': float(df[df['tipo']=='Ingreso']['importe'].sum()),
                    'total_gastos': float(df[df['tipo']=='Gasto']['importe'].sum())
                }
            }
            
            metadata_path = os.path.join(self.demo_dir, 'metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            return {
                'csv_path': csv_path,
                'pdf_path': pdf_path,
                'metadata_path': metadata_path
            }
            
        except Exception as e:
            logger.error(f"Error generando datos demo: {str(e)}")
            raise