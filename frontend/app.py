import streamlit as st
import pandas as pd
import json
import logging
from datetime import datetime
from typing import Dict, Any
import base64
from config.gpt_client import GPTClient
from scenarios.scenario_generator import ScenarioGenerator
from visualization.scenario_visualizer import ScenarioVisualizer
from ml_analysis.clustering import FinancialClustering
from utils.demo_data_generator import DemoDataGenerator
from utils.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECTORES = ["Tecnología", "Industria", "Servicios", "Comercio", "Construcción", "Agricultura"]
REGIONES = ["Andalucía", "Aragón", "Asturias", "Baleares", "Canarias", "Cantabria", 
           "Castilla y León", "Castilla-La Mancha", "Cataluña", "Valencia", "Extremadura", 
           "Galicia", "Madrid", "Murcia", "Navarra", "País Vasco", "La Rioja"]

def get_base64_of_bin_file(bin_file):
   with open(bin_file, 'rb') as f:
       data = f.read()
   return base64.b64encode(data).decode()

def set_background():
   try:
       bin_str = get_base64_of_bin_file('Foto.jpg')
       page_bg_img = f'''
       <style>
       .stApp {{
           background-image: url("data:image/jpg;base64,{bin_str}");
           background-size: cover;
       }}
       </style>
       '''
       st.markdown(page_bg_img, unsafe_allow_html=True)
   except Exception as e:
       logger.error(f"Error setting background: {e}")

def initialize_session_state():
   default_states = {
       'financial_data': None,
       'scenarios': None,
       'company_context': None,
       'historical_data': None
   }
   for key, default_value in default_states.items():
       if key not in st.session_state:
           st.session_state[key] = default_value

def company_context_form():
    if st.session_state.company_context is None:
        st.header("🏢 Configuración Inicial de la Empresa")
        with st.form("company_context_form"):
            sector = st.selectbox("Sector", SECTORES)
            region = st.selectbox("Comunidad Autónoma", REGIONES)
            submit = st.form_submit_button("Guardar Configuración")
            
            if submit:
                with st.spinner("Generando contexto empresarial..."):
                    try:
                        # Inicializar GPT client
                        gpt_client = GPTClient()
                        
                        # Generar y guardar contexto
                        gpt_client.generate_company_context(sector, region)
                        
                        st.session_state.company_context = {
                            "sector": sector,
                            "region": region
                        }
                        st.success("✅ Configuración guardada correctamente")
                        
                        # Mostrar el contexto generado
                        with st.expander("Ver Contexto Generado"):
                            with open("company_context.txt", "r", encoding="utf-8") as f:
                                context = f.read()
                            st.markdown(context)
                            
                        return True
                    except Exception as e:
                        st.error(f"❌ Error generando contexto: {str(e)}")
                        return False
        return False
    return True

def show_historical_data(db: DatabaseManager):
   st.header("📊 Histórico de Operaciones")
   
   col1, col2, col3 = st.columns(3)
   with col1:
       concepto_filter = st.text_input("Filtrar por Concepto")
   with col2:
       entidad_filter = st.text_input("Filtrar por Entidad")
   with col3:
       tipo_filter = st.selectbox("Tipo", ["Todos", "Ingreso", "Gasto"])

   with st.form("new_operation_form"):
       st.subheader("Nueva Operación")
       fecha = st.date_input("Fecha", datetime.now())
       concepto = st.text_input("Concepto")
       entidad = st.text_input("Entidad")
       tipo = st.selectbox("Tipo", ["Ingreso", "Gasto"])
       importe = st.number_input("Importe", min_value=0.0)
       submit = st.form_submit_button("Añadir Operación")
       
       if submit:
           try:
               db.add_operation(fecha, concepto, entidad, tipo, importe)
               st.success("✅ Operación guardada correctamente")
           except Exception as e:
               st.error(f"❌ Error al guardar: {str(e)}")

   try:
       data = db.get_historical_data(
           concepto=concepto_filter,
           entidad=entidad_filter,
           tipo=tipo_filter if tipo_filter != "Todos" else None
       )
       
       if not data.empty:
           st.dataframe(data)
           
           col1, col2 = st.columns(2)
           with col1:
               st.metric("Total Ingresos", f"€{data[data['tipo']=='Ingreso']['importe'].sum():,.2f}")
           with col2:
               st.metric("Total Gastos", f"€{data[data['tipo']=='Gasto']['importe'].sum():,.2f}")
           
           csv = data.to_csv(index=False)
           st.download_button("Descargar CSV", csv, "historical_data.csv", "text/csv")
       else:
           st.info("ℹ️ No se encontraron datos con los filtros actuales")
           
   except Exception as e:
       st.error(f"❌ Error al cargar datos: {str(e)}")

def prepare_clustering_data(financial_data: Dict[str, float]) -> pd.DataFrame:
   base_data = pd.DataFrame([financial_data])
   variations = []
   
   for variation in [-0.15, -0.10, -0.05, 0.05, 0.10, 0.15]:
       variation_data = {
           'ingresos': financial_data['ingresos'] * (1 + variation),
           'gastos': financial_data['gastos'] * (1 + variation)
       }
       variations.append(variation_data)
   
   return pd.concat([base_data, pd.DataFrame(variations)], ignore_index=True)

def display_pdf_data(pdf_data: dict, db: DatabaseManager):
   st.subheader("📝 Resumen Ejecutivo")
   st.info(pdf_data['summary'])
   
   st.subheader("📊 Registros Detectados")
   for idx, entry in enumerate(pdf_data['entries']):
       with st.expander(f"Registro {idx + 1}"):
           with st.form(f"entry_form_{idx}"):
               col1, col2 = st.columns(2)
               with col1:
                   fecha = st.date_input("Fecha", 
                       value=datetime.strptime(entry['fecha'], '%Y-%m-%d'))
                   concepto = st.text_input("Concepto", 
                       value=entry['concepto'])
               with col2:
                   entidad = st.text_input("Entidad", 
                       value=entry['entidad'])
                   importe = st.number_input("Importe", 
                       value=float(entry['importe']))
               tipo = st.selectbox("Tipo", ["Ingreso", "Gasto"])
               
               if st.form_submit_button("💾 Guardar Registro"):
                   db.add_operation(fecha, concepto, entidad, tipo, importe)
                   st.success("✅ Registro guardado correctamente")

def display_visualizations(scenarios: dict, visualizer: ScenarioVisualizer):
   try:
       st.subheader("📈 Comparativa de Ingresos")
       fig_ingresos = visualizer.create_comparison_chart(scenarios, 'ingresos')
       st.plotly_chart(fig_ingresos, use_container_width=True)
       
       st.subheader("📊 Dashboard de Métricas")
       metrics = ['ingresos', 'beneficio_neto', 'margen_bruto']
       fig_dashboard = visualizer.create_metrics_dashboard(scenarios, metrics)
       st.plotly_chart(fig_dashboard, use_container_width=True)
       
       st.subheader("📈 Proyección Temporal")
       fig_timeline = visualizer.create_timeline_chart(scenarios, 'ingresos')
       st.plotly_chart(fig_timeline, use_container_width=True)
   except Exception as e:
       st.error(f"❌ Error en visualizaciones: {str(e)}")


def main():
   try:
       st.set_page_config(page_title="Análisis Financiero con IA", layout="wide")
       set_background()
       st.title("📊 Análisis Financiero con IA Generativa")
       
       initialize_session_state()
       
       if not company_context_form():
           return
       
       try:
           gpt_client = GPTClient()
           scenario_generator = ScenarioGenerator(gpt_client)
           visualizer = ScenarioVisualizer()
           clustering = FinancialClustering(gpt_client)
           db = DatabaseManager()
       except Exception as e:
           st.error(f"❌ Error de inicialización: {str(e)}")
           return

       with st.sidebar:
           st.header("📝 Entrada de Datos")
           method = st.radio("Método de entrada", 
               ["Datos Demo", "Cargar CSV", "Cargar PDF", "Entrada Manual"])
           
           if method == "Datos Demo":
               if st.button("Cargar Datos de Demostración"):
                   try:
                       demo_gen = DemoDataGenerator()
                       paths = demo_gen.generate_all_demo_data()
                       df = pd.read_csv(paths['csv_path'])
                       st.session_state.financial_data = {
                           'ingresos': df[df['tipo'] == 'Ingreso']['importe'].sum(),
                           'gastos': df[df['tipo'] == 'Gasto']['importe'].sum()
                       }
                       st.success("✅ Datos de demostración cargados correctamente")
                       logger.info("Datos demo cargados exitosamente")
                   except Exception as e:
                       st.error(f"❌ Error al cargar datos demo: {str(e)}")
                       
           elif method == "Cargar CSV":
               uploaded_file = st.file_uploader("Cargar archivo CSV", type=['csv'])
               if uploaded_file:
                   try:
                       df = pd.read_csv(uploaded_file)
                       
                       # Convertir la columna fecha a datetime
                       df['fecha'] = pd.to_datetime(df['fecha'])
                        
                       # Insertar datos en la base de datos
                       db = DatabaseManager()
                       for _, row in df.iterrows():
                           db.add_operation(
                               fecha=row['fecha'],
                               concepto=row['concepto'],
                               entidad=row['entidad'],
                               tipo=row['tipo'],
                               importe=float(row['importe'])
                           )
                        
                       # Actualizar totales en session_state
                       st.session_state.financial_data = {
                           'ingresos': df[df['tipo'] == 'Ingreso']['importe'].sum(),
                           'gastos': df[df['tipo'] == 'Gasto']['importe'].sum()
                       }
                        
                       st.success("✅ CSV cargado y datos insertados correctamente en la base de datos")
                   except Exception as e:
                       st.error(f"❌ Error al procesar CSV: {str(e)}")
                       
           elif method == "Cargar PDF":
               uploaded_file = st.file_uploader("Cargar archivo PDF", type=['pdf'])
               if uploaded_file:
                   try:
                       with st.spinner("Procesando PDF..."):
                           pdf_data = gpt_client.process_pdf(uploaded_file)
                           display_pdf_data(pdf_data, db)
                           
                           # Actualizar financial_data con los totales
                           total_ingresos = sum(float(entry['importe']) for entry in pdf_data['entries'] 
                                              if entry.get('tipo') == 'Ingreso')
                           total_gastos = sum(float(entry['importe']) for entry in pdf_data['entries'] 
                                            if entry.get('tipo') == 'Gasto')
                           
                           st.session_state.financial_data = {
                               'ingresos': total_ingresos,
                               'gastos': total_gastos
                           }
                   except Exception as e:
                       st.error(f"❌ Error al procesar PDF: {str(e)}")
                       
           else:  # Entrada Manual
               with st.form("manual_input_form"):
                   st.subheader("Datos Financieros")
                   ingresos = st.number_input("Ingresos", value=1000000)
                   gastos = st.number_input("Gastos", value=800000)
                   
                   if st.form_submit_button("Guardar Datos"):
                       st.session_state.financial_data = {
                           'ingresos': ingresos,
                           'gastos': gastos
                       }
                       st.success("✅ Datos guardados correctamente")

       if st.session_state.financial_data is not None:
           tabs = st.tabs(["📈 Escenarios", "🔍 Clustering", "📊 Visualización", "📋 Histórico"])
           
           with tabs[0]:
               st.header("Generación de Escenarios")
               if st.button("Generar Escenarios"):
                   with st.spinner("🔄 Generando escenarios..."):
                       try:
                           logger.info(f"Financial data: {st.session_state.financial_data}")
                           logger.info(f"Context: {st.session_state.company_context}")
                           
                           st.session_state.scenarios = scenario_generator.generate_scenarios(
                               st.session_state.financial_data,
                               st.session_state.company_context
                           )
                           
                           if st.session_state.scenarios:
                               st.success("✅ Escenarios generados correctamente")
                               
                               for scenario_name, scenario_data in st.session_state.scenarios.items():
                                   with st.expander(f"Escenario {scenario_name.capitalize()}"):
                                       st.write("📝 Descripción:")
                                       st.write(scenario_data['descripcion'])
                                       
                                       st.write("🔢 Proyecciones:")
                                       st.dataframe(pd.DataFrame([scenario_data['proyecciones']]))
                                       
                                       st.write("📋 Supuestos:")
                                       for supuesto in scenario_data['supuestos']:
                                           st.write(f"• {supuesto}")
                               
                               display_visualizations(st.session_state.scenarios, visualizer)
                               
                               st.subheader("📝 Análisis Detallado")
                               analysis = scenario_generator.generate_detailed_analysis(
                                   st.session_state.scenarios,
                                   st.session_state.company_context
                               )
                               st.write(analysis)
                       except Exception as e:
                           st.error(f"❌ Error al generar escenarios: {str(e)}")
           
           with tabs[1]:
               st.header("Análisis de Clustering")
               if st.button("Realizar Clustering"):
                   with st.spinner("🔄 Analizando datos..."):
                       try:
                           data_dict = st.session_state.financial_data
                           #df = pd.DataFrame([data_dict])
                           df = prepare_clustering_data(data_dict)
                           if len(df.columns) < 2:
                               st.warning("⚠️ Se necesitan al menos dos columnas numéricas")
                           else:
                               prepared_data = clustering.prepare_data(df, df.columns.tolist())
                               clusters_data, results = clustering.fit_predict(
                                    prepared_data, 
                                    n_clusters=3,
                                    context=st.session_state.company_context  # Pasar el contexto
                               )
                               
                               st.success("✅ Análisis completado")
                               
                               st.subheader("📊 Resumen de Clusters")
                               for cluster_name, cluster_data in results['summary'].items():
                                   with st.expander(f"Cluster {cluster_name.split('_')[1]}"):
                                       st.metric("Tamaño", 
                                               f"{cluster_data['size']} registros",
                                               f"{cluster_data['percentage']:.1f}%")
                                       
                                       st.write("📈 Valores Promedio:")
                                       st.dataframe(pd.DataFrame(cluster_data['mean_values'], 
                                                              index=['Valor']).T)
                                       
                                       st.write("📊 Rango de Valores:")
                                       ranges = pd.DataFrame({
                                           'Mínimo': cluster_data['min_values'],
                                           'Máximo': cluster_data['max_values']
                                       })
                                       st.dataframe(ranges)
                               
                               st.subheader("📝 Interpretación")
                               st.write(results['interpretation'])
                               
                               st.subheader("🔍 Datos Asignados")
                               st.dataframe(clusters_data)
                       except Exception as e:
                           st.error(f"❌ Error en clustering: {str(e)}")
           
           with tabs[2]:
               st.header("Visualización de Resultados")
               
               if st.session_state.scenarios:
                   display_visualizations(st.session_state.scenarios, visualizer)
               else:
                   st.info("ℹ️ Genera escenarios primero para ver visualizaciones")
           
           with tabs[3]:
               show_historical_data(db)
       
       else:
           st.info("👈 Selecciona un método de entrada de datos en el panel lateral")

   except Exception as e:
       st.error(f"❌ Error en la aplicación: {str(e)}")
       logger.error(f"Error general en la aplicación: {str(e)}")

if __name__ == "__main__":
   main()