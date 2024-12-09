import pandas as pd
from config.gpt_client import GPTClient
from ml_analysis.clustering import FinancialClustering

def main():
    # Crear algunos datos de ejemplo
    data = pd.DataFrame({
        'ingresos': [1000000, 1200000, 800000, 2000000, 1500000],
        'gastos': [800000, 900000, 700000, 1500000, 1200000],
        'margen': [200000, 300000, 100000, 500000, 300000],
        'empleados': [50, 60, 40, 100, 75]
    })
    
    # Inicializar el cliente GPT y el clustering
    gpt_client = GPTClient()
    clustering = FinancialClustering(gpt_client)
    
    # Preparar los datos
    features = ['ingresos', 'gastos', 'margen']
    prepared_data = clustering.prepare_data(data, features)
    
    # Realizar el clustering
    data_with_clusters, results = clustering.fit_predict(prepared_data)
    
    # Imprimir resultados
    print("\nDatos con clusters asignados:")
    print(data_with_clusters)
    
    print("\nResumen de clusters:")
    for cluster, info in results['summary'].items():
        print(f"\n{cluster}:")
        print(f"Tamaño: {info['size']} empresas ({info['percentage']:.2f}%)")
        print("Centroide:", info['centroid'])
    
    print("\nInterpretación GPT:")
    print(results['interpretation'])

if __name__ == "__main__":
    main()