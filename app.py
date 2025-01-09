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
def fetch_session_ids(base_url, username, password):
    """
    Fetch session IDs from the API.
    """
    response = requests.get(base_url, auth=(username, password))
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            return [item['id'] for item in data['data']]
        else:
            return []
    else:
        st.error(f"Fehler bei der API-Anfrage: {response.status_code}")
        return []

@st.cache_data
def fetch_session_details(ids, details_url, username, password):
    """
    Fetch details for each session ID and process the data.
    """
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
                        "Frage": question,
                        "Antwort": output
                    })
    return results

# Abrufen der Session-IDs
ids = fetch_session_ids(base_url, username, password)

if ids:
    # Abrufen der Details für die Sessions
    results = fetch_session_details(ids, details_url, username, password)

    if results:
        # DataFrame erstellen und anzeigen
        df = pd.DataFrame(results)
        df.columns = ["Datum und Uhrzeit", "Frage", "Antwort"]
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Keine Daten gefunden.")
else:
    st.error("Keine Session-IDs gefunden.")
