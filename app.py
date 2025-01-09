import requests
import pandas as pd
from datetime import datetime
import streamlit as st

# API Endpoint
base_url = "https://cloud.langfuse.com/api/public/sessions"
details_url = "https://cloud.langfuse.com/api/public/sessions/{id}"

# Basic Authentication Credentials
username = st.secrets["username"]
password = st.secrets["password"]

st.set_page_config(layout="wide")

# CSS für Textumbruch
st.markdown("""
    <style>
    .dataframe td {
        white-space: normal;
        word-wrap: break-word;
    }
    </style>
""", unsafe_allow_html=True)

# Streamlit App
st.title("TONI Park | Chatbot | Fragen und Antworten")

pd.set_option('display.max_colwidth', None)

@st.cache_data
def load_data(base_url, details_url, username, password):
    """
    Abrufen und Verarbeiten der Daten von der API.
    """
    # Ergebnisse werden in einer Liste gespeichert
    results = []

    # Abrufen der Session-IDs
    response = requests.get(base_url, auth=(username, password))
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            ids = [item['id'] for item in data['data']]
            
            # Abrufen der Details für jede Session-ID
            for id_value in ids:
                details_response = requests.get(details_url.format(id=id_value), auth=(username, password))
                if details_response.status_code == 200:
                    details_data = details_response.json()
                    traces = details_data.get("traces", [])
                    
                    # Verarbeitung der Traces
                    for trace in traces:
                        question = trace.get("input", {}).get("question")
                        output = trace.get("output")
                        timestamp = trace.get("timestamp")  # Full timestamp
                        
                        # Format timestamp to TT.MM.JJJJ HH:MM:SS
                        if timestamp:
                            try:
                                date_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d.%m.%Y %H:%M:%S")
                            except ValueError:
                                date_time = None
                        else:
                            date_time = None

                        # Speichern der relevanten Daten
                        if question and output:
                            results.append({
                                "Datum und Uhrzeit": date_time,
                                "Frage": question,
                                "Antwort": output
                            })
    else:
        st.error(f"Fehler bei der API-Anfrage: {response.status_code}")
    
    # Rückgabe der Ergebnisse
    return results

# Daten laden
results = load_data(base_url, details_url, username, password)

# Ergebnisse anzeigen
if results:
    # DataFrame erstellen
    df = pd.DataFrame(results)
    df.columns = ["Datum und Uhrzeit", "Frage", "Antwort"]
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Keine Daten gefunden.")
