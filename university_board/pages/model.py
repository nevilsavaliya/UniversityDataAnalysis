import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from university_board.utils.fetch_api import fetch_scatter_data, fetch_university_ranks

from university_board.utils.fetch_api import fetch_summary


def show():
    st.subheader("🏫 Predict Rank by University Name")

    data = fetch_summary()
    student_stats = pd.DataFrame(data.get("student_stats_raw_data", []))

    if student_stats.empty:
        st.error("No university data found.")
        return

    university_names = sorted(student_stats["University Name"].dropna().unique().tolist())

    selected_university = st.selectbox("Search and select university", university_names)

    if st.button("🔮 Predict Rank"):
        with st.spinner("Predicting..."):
            try:
                response = fetch_university_ranks(selected_university)
                if response.status_code == 200:
                    prediction = response.json()
                    st.success(
                        f"🎯 Predicted Rank for **{selected_university}**: {round(prediction['all_ranks'][0])}"
                    )

                    # Plot prediction
                    historical = prediction["historical_ranks"]
                    predicted = prediction["all_ranks"]

                    historical_years = [entry["year"] for entry in historical]
                    historical_ranks = [entry["rank"] for entry in historical]

                    last_year = historical_years[-1]

                    predicted_years = [last_year + i + 1 for i in range(len(predicted))]
                    predicted_ranks = predicted

                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(
                        historical_years,
                        historical_ranks,
                        marker="o",
                        label="Historical Rank",
                        color="blue",
                    )
                    ax.plot(
                        predicted_years,
                        predicted_ranks,
                        marker="o",
                        linestyle="--",
                        label="Predicted Rank",
                        color="orange",
                    )

                    ax.set_title(f"Rank Prediction for {selected_university.title()}")
                    ax.set_xlabel("Year")
                    ax.set_ylabel("Rank (lower is better)")
                    ax.invert_yaxis()
                    ax.grid(True)
                    ax.legend()

                    st.pyplot(fig)

                else:
                    st.error(f"❌ Error: {response.json().get('error')}")
            except Exception as e:
                st.error(f"🚫 Request failed: {e}")
