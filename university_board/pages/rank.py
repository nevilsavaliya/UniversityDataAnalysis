import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st
from university_board.utils.fetch_api import fetch_university_data

def show():
    st.subheader("🏫 Predict Rank by University Data")

    st.markdown(
        "Fill the university details below, select subjects, and predict ranks for the next 4 years."
    )

    with st.form("rank_prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("University Name", value="Ziauddin University")
            location = st.text_input("Location", value="Pakistan")
            year = st.number_input("Year", min_value=2010, max_value=2100, value=2024)
            closed = st.selectbox("Closed", [0, 1], index=0)
            unaccredited = st.selectbox("Unaccredited", [0, 1], index=0)

        with col2:
            scores_overall = st.number_input("Scores Overall", value=66.7)
            scores_teaching = st.number_input("Scores Teaching", value=55.8)
            scores_international_outlook = st.number_input(
                "Scores International Outlook", value=67.3
            )
            scores_industry_income = st.number_input(
                "Scores Industry Income", value=85.0
            )
            scores_research = st.number_input("Scores Research", value=52.7)
            scores_citations = st.number_input("Scores Citations", value=88.4)

        st.subheader("📚 Subjects")
        subject_options = [
            "Accounting & Finance",
            "Agriculture & Forestry",
            "Archaeology",
            "Architecture",
            "Art",
            "Biological Sciences",
            "Business & Management",
            "Chemical Engineering",
            "Chemistry",
            "Civil Engineering",
            "Communication & Media Studies",
            "Computer Science",
            "Data Science",
            "Earth & Marine Sciences",
            "Economics & Econometrics",
            "Education",
            "Electrical & Electronic Engineering",
            "Environmental",
            "General Engineering",
            "Geography",
            "Geology",
            "History",
            "Languages",
            "Law",
            "Literature & Linguistics",
            "Mathematics & Statistics",
            "Mechanical & Aerospace Engineering",
            "Medicine & Dentistry",
            "Other Health",
            "Performing Arts & Design",
            "Philosophy",
            "Philosophy & Theology",
            "Physics & Astronomy",
            "Politics & International Studies (incl Development Studies)",
            "Psychology",
            "Sociology",
            "Sport Science",
            "Veterinary Science",
        ]

        subjects_studying = st.multiselect(
            "Search & Select Subjects",
            options=subject_options,
            default=["Computer Science", "Data Science"],
        )

        st.subheader("📊 Stats")
        col3, col4 = st.columns(2)

        with col3:
            stats_number_students = st.number_input("Number of Students", value=5672.0)
            stats_student_staff_ratio = st.number_input(
                "Student Staff Ratio", value=9.2
            )

        with col4:
            stats_pc_intl_students = st.number_input(
                "Percent International Students", value=0.0
            )
            stats_female_male_ratio = st.number_input("Female/Male Ratio", value=138.1)
            stats_proportion_of_isr = st.number_input("Proportion of ISR", value=5.0)

        submitted = st.form_submit_button("Predict Rank")

    if submitted:
        input_payload = {
            "name": name,
            "location": location,
            "year": year,
            "scores_overall": scores_overall,
            "scores_teaching": scores_teaching,
            "scores_international_outlook": scores_international_outlook,
            "scores_industry_income": scores_industry_income,
            "scores_research": scores_research,
            "scores_citations": scores_citations,
            "closed": closed,
            "unaccredited": unaccredited,
            "stats_number_students": stats_number_students,
            "stats_student_staff_ratio": stats_student_staff_ratio,
            "stats_pc_intl_students": stats_pc_intl_students,
            "stats_female_male_ratio": stats_female_male_ratio,
            "stats_proportion_of_isr": stats_proportion_of_isr,
            "subjects_studying": subjects_studying,
        }

        with st.spinner("Predicting..."):
            try:
                response = fetch_university_data(input_payload)
                if response.status_code != 200:
                    st.error(f"❌ Error: {response.text}")
                    return

                data = response.json()
                predictions = data.get("predictions", [])

                if not predictions:
                    st.warning("No predictions returned.")
                    return

                df_pred = pd.DataFrame(predictions)

                st.success("✅ Prediction Successful!")
                st.write(df_pred)

                # Plot predictions
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(
                    df_pred["year"],
                    df_pred["predicted_rank"],
                    marker="o",
                    color="orange",
                    linestyle="--",
                    label="Predicted Rank",
                )

                ax.set_title(f"4-Year Rank Prediction for {name}")
                ax.set_xlabel("Year")
                ax.set_ylabel("Predicted Rank (lower is better)")
                ax.invert_yaxis()
                ax.grid(True)
                ax.legend()

                st.pyplot(fig)

            except Exception as e:
                st.error(f"🚫 Request failed: {e}")
