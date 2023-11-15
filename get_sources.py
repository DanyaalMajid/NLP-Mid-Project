import requests
import pandas as pd
def get_and_save_sources(api_key, csv_filename='sources.csv'):
    sources_url = 'https://newsapi.org/v2/sources'
    parameters = {'apiKey': api_key}
    
    response = requests.get(sources_url, params=parameters)
    
    if response.status_code == 200:
        sources_data = response.json()
        
        # Extract source names and save to CSV
        source_names = [source['id'] for source in sources_data['sources']]
        pd.DataFrame(source_names, columns=['Source']).to_csv(csv_filename, index=False)
        print(f"Sources saved to {csv_filename}")
    else:
        print(f"Error fetching sources: {response.status_code} - {response.text}")

get_and_save_sources("ed16694cb0d3426fa8a38cadd324a361")