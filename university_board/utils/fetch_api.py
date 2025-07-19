import requests
import streamlit as st

API_URL = "http://127.0.0.1:5000"

@st.cache_data(ttl=60)
def fetch_summary():
    try:
        res = requests.get(f'{API_URL}/analytics')
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API fetch failed: {e}")
        return {}

def fetch_scatter_data():
    r = requests.get(f"{API_URL}/scatter_data")
    r.raise_for_status()
    return r.json()
