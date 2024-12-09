import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Dict, Any, Optional
import json
import logging
from config.gpt_client import GPTClient

logger = logging.getLogger(__name__)

class FinancialClustering:
    def __init__(self, gpt_client: GPTClient):
        self.gpt_client = gpt_client
        self.scaler = StandardScaler()
        self.kmeans = None
        self.features = None
        
    def prepare_data(self, data: pd.DataFrame, features: list) -> pd.DataFrame:
        """Prepara los datos para el clustering"""
        self.features = features
        numerical_data = data[features].copy()
        numerical_data = numerical_data.fillna(numerical_data.mean())
        return numerical_data
        
    def fit_predict(self, data: pd.DataFrame, n_clusters: int = 3, context: Optional[Dict[str, Any]] = None) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Realiza el clustering y obtiene interpretación"""
        try:
            # Escalar los datos
            scaled_data = self.scaler.fit_transform(data)
            
            # Realizar clustering
            self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = self.kmeans.fit_predict(scaled_data)
            
            # Añadir clusters al DataFrame original
            data_with_clusters = data.copy()
            data_with_clusters['Cluster'] = clusters
            
            # Calcular centroides en escala original
            centroids_scaled = self.kmeans.cluster_centers_
            centroids_original = self.scaler.inverse_transform(centroids_scaled)
            
            # Crear resumen de clusters
            cluster_summary = self._create_cluster_summary(data_with_clusters, centroids_original)
            
            # Obtener interpretación considerando contexto empresarial
            interpretation = self._get_gpt_interpretation(cluster_summary, context)
            
            return data_with_clusters, {
                'summary': cluster_summary,
                'interpretation': interpretation
            }
        except Exception as e:
            logger.error(f"Error en clustering: {str(e)}")
            raise
    
    def _create_cluster_summary(self, data: pd.DataFrame, centroids: np.ndarray) -> Dict[str, Any]:
        """Crea un resumen detallado de los clusters"""
        summary = {}
        for i in range(len(centroids)):
            cluster_data = data[data['Cluster'] == i]
            
            summary[f'cluster_{i}'] = {
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(data) * 100,
                'centroid': {
                    feature: float(centroid_value)
                    for feature, centroid_value in zip(self.features, centroids[i])
                },
                'min_values': {
                    feature: float(value)
                    for feature, value in cluster_data[self.features].min().items()
                },
                'max_values': {
                    feature: float(value)
                    for feature, value in cluster_data[self.features].max().items()
                },
                'mean_values': {
                    feature: float(value)
                    for feature, value in cluster_data[self.features].mean().items()
                }
            }
            
        return summary
    
    def _get_gpt_interpretation(self, cluster_summary: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """Obtiene interpretación de los clusters usando GPT para datos temporales"""
        context = context or {}
        sector = context.get('sector', 'No especificado')
        region = context.get('region', 'No especificada')
        
        prompt = f"""
        Analiza estos clusters de datos históricos de cobros y pagos de una empresa del sector {sector} en {region}. 
        Cada punto de datos representa un período temporal diferente de la misma empresa.
        
        Resumen de Clusters:
        {json.dumps(cluster_summary, indent=2)}
        
        Por favor proporciona:
        1. Características distintivas de cada cluster, interpretándolos como diferentes períodos financieros de la empresa
        2. Patrones temporales identificados en los cobros y pagos
        3. Análisis de la estabilidad financiera basado en la distribución de los clusters
        4. Posibles factores estacionales o cíclicos en los patrones de cobros y pagos
        5. Recomendaciones para optimizar la gestión de cobros y pagos basadas en los patrones identificados
        """
        
        return self.gpt_client.generate_financial_opinion(prompt, context)