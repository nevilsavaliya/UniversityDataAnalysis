import requests
import streamlit as st

API_URL = "http://127.0.0.1:5000/analytics"

@st.cache_data(ttl=60)
def fetch_summary():
    try:
        res = requests.get(API_URL)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"API fetch failed: {e}")
        return {}
