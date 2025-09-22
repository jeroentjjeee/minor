import sys
print(sys.prefix)

import requests

# Endpoint van de Kadaster Labs API
url = "https://data.labs.kadaster.nl/cbs/woningwaarde/1"

# Optionele parameters (hier: alle buurten, jaar 2022)
query = {
    "select": ["gebied_naam", "jaar", "woningwaarde_gemiddeld"],
    "where": {
        "jaar": 2022
    },
    "limit": 10  # Beperk aantal rijen (voor demo)
}

# POST-verzoek sturen met JSON-payload
response = requests.post(url, json=query)

if response.status_code == 200:
    data = response.json()
    for row in data['data']:
        print(f"{row[0]} - {row[1]}: €{row[2]:,.0f}")
else:
    print("Fout:", response.status_code)


