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
st.title("Lebedew | Chatbot | Fragen und Antworten")

# Sending GET Request with Basic Authentication
response = requests.get(base_url, auth=(username, password))

if response.status_code == 200:
    # Parse JSON response
    data = response.json()
    
    if 'data' in data:
        ids = [item['id'] for item in data['data']]
        
        @st.cache_data
        def load_data(ids, username, password):
            results = []
            for id_value in ids:
                details_response = requests.get(details_url.format(id=id_value), auth=(username, password))

                if details_response.status_code == 200:
                    details_data = details_response.json()
                    traces = details_data.get("traces", [])
                    
                    for trace in traces:
                        question = trace.get("input", {}).get("question")
                        output = trace.get("output")
                        timestamp = trace.get("timestamp")  # Full timestamp
                        release = trace.get("release")
                        
                        # Format timestamp to TT.MM.JJJJ HH:MM:SS
                        if timestamp:
                            try:
                                date_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d.%m.%Y %H:%M:%S")
                            except ValueError:
                                date_time = None
                        else:
                            date_time = None

                        if question and output:
                            results.append({
                                "Datum und Uhrzeit": date_time,
                                "Hotel": release,
                                "Frage": question,
                                "Antwort": output
                            })
            # Rückgabe des Ergebnisses als DataFrame
            return results

        # Laden der Daten
        results = load_data(ids, username, password)

        # Prüfen, ob Ergebnisse vorhanden sind
        if results:
            # DataFrame erstellen
            df = pd.DataFrame(results)
            df.columns = ["Datum und Uhrzeit", "Hotel", "Frage", "Antwort"]
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Keine Daten gefunden. Bitte überprüfen Sie die API-Daten.")
    else:
        st.error("Keine Daten gefunden.")
else:
    st.error(f"Fehler bei der API-Anfrage: {response.status_code}")
