import streamlit as st
from university_board.utils.fetch_api import fetch_summary

def show():
    data = fetch_summary()
    st.subheader("📊 Key Statistics")
    col1, col2 = st.columns(2)
    col1.metric("Total Universities", data.get("total_universities", "N/A"))
    col2.metric("Avg Student-Staff Ratio", f"{data.get('avg_student_staff_ratio', 0):.2f}")
