import streamlit as st

from university_board.pages import country, model, overview, rank, student, teaching

st.set_page_config(page_title="University Dashboard", layout="wide")

st.sidebar.title("📁 Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Country Analytics",
        "Student Stats",
        "Teaching Quality",
        "Rank Prediction",
        "Data Rank Prediction",
    ],
)

if page == "Overview":
    overview.show()
elif page == "Country Analytics":
    country.show()
elif page == "Student Stats":
    student.show()
elif page == "Teaching Quality":
    teaching.show()
elif page == "Rank Prediction":  # ✅ Add this
    model.show()
elif page == "Data Rank Prediction":
    rank.show()
