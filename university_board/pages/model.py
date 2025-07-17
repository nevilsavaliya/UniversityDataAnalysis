import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st

from university_board.utils.fetch_api import fetch_summary


def show():
    st.subheader("🏫 Predict Rank by University Name")

    data = fetch_summary()
    df = data.get("raw_data", [])

    if not df:
        st.error("No university data found.")
        return

    university_names = sorted(
        {row["name"] for row in df if "name" in row and pd.notna(row["name"])}
    )

    selected_university = st.selectbox("Search and select university", university_names)

    if st.button("🔮 Predict Rank"):
        with st.spinner("Predicting..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:5000/predict_rank_by_name",
                    json={"university_name": selected_university},
                )
                if response.status_code == 200:
                    prediction = response.json()
                    st.success(
                        f"🎯 Predicted Rank for **{selected_university}**: {round(prediction['all_ranks'][0])}"
                    )

                    # Plot the graph
                    historical = prediction["historical_ranks"]
                    predicted = prediction["all_ranks"]

                    # Extract historical data
                    historical_years = [entry["year"] for entry in historical]
                    historical_ranks = [entry["rank"] for entry in historical]

                    # Last year in historical
                    last_year = historical_years[-1]

                    # Predicted years & ranks
                    predicted_years = [last_year + i + 1 for i in range(len(predicted))]
                    predicted_ranks = predicted

                    # Plot
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
                    ax.invert_yaxis()  # because lower rank is better
                    ax.grid(True)
                    ax.legend()

                    st.pyplot(fig)

                else:
                    st.error(f"❌ Error: {response.json().get('error')}")
            except Exception as e:
                st.error(f"🚫 Request failed: {e}")
