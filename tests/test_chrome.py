import requests

def google_search(api_key, search_engine_id, query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query
    }
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

# Uso
api_key = "AIzaSyC2AmQ-RAkiBwloenraXB0iKd740PbcsJI"  # Clave de API obtenida de Google Cloud
search_engine_id = "b4a25510150834ab6"  # ID del motor de búsqueda personalizado
query = "Variables relevantes en el sector servicios en Madrid para 2024"
results = google_search(api_key, search_engine_id, query)

if results:
    for item in results.get("items", []):
        print(f"Título: {item['title']}")
        print(f"URL: {item['link']}")
        print(f"Snippet: {item['snippet']}\n")
