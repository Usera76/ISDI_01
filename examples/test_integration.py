import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.demo_data_generator import DemoDataGenerator
from utils.database import DatabaseManager
from config.gpt_client import GPTClient

def main():
    print("Iniciando prueba de integración...")
    
    # 1. Generar datos de demo
    print("\n1. Generando datos de demo...")
    generator = DemoDataGenerator()
    paths = generator.generate_all_demo_data()
    print(f"Archivos generados en:")
    for key, path in paths.items():
        print(f"- {key}: {path}")
    
    # 2. Almacenar en base de datos
    print("\n2. Almacenando datos en base de datos...")
    db = DatabaseManager()
    df = generator.generate_historical_data()
    
    for _, row in df.iterrows():
        db.store_financial_data(
            data=row.to_dict(),
            provider_id=row['provider_id'],
            client_id=row['client_id'],
            invoice_number=row['invoice_number'],
            date=row['fecha']
        )
    
    # 3. Probar caché de GPT
    print("\n3. Probando caché de GPT...")
    gpt_client = GPTClient()
    prompt = "Analiza el siguiente ratio financiero: ROE = 15%"
    
    print("- Primera llamada (sin caché)...")
    response1 = gpt_client._make_request([{"role": "user", "content": prompt}])
    print("- Segunda llamada (desde caché)...")
    response2 = gpt_client._make_request([{"role": "user", "content": prompt}])
    
    print("¿Respuestas iguales?", response1 == response2)
    
    # 4. Recuperar datos históricos
    print("\n4. Recuperando datos históricos...")
    historical_data = db.get_historical_data()
    print(f"Registros recuperados: {len(historical_data)}")
    
    print("\nPrueba de integración completada con éxito!")

if __name__ == "__main__":
    main()