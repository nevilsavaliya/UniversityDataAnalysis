import streamlit as st
import pandas as pd
import plotly.express as px
from university_board.utils.fetch_api import fetch_summary


def show():
    data = fetch_summary()
    st.subheader("🎯 Student & International Stats")

    # Metrics
    intl_pct = data.get("avg_international_students_pct", "N/A")
    total_students = data.get("avg_number_of_students", "N/A")
    female_male_ratio = data.get("avg_female_male_ratio", "N/A")
    proportion_of_isr = data.get("avg_proportion_of_isr", "N/A")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg % International Students", f"{intl_pct:.2f}" if isinstance(intl_pct, (float, int)) else intl_pct)
    col2.metric("Avg Total Students", f"{int(total_students):,}" if isinstance(total_students, (float, int)) else total_students)
    col3.metric("Avg Female:Male Ratio", f"{female_male_ratio:.2f}" if isinstance(female_male_ratio, (float, int)) else female_male_ratio)
    col4.metric("Avg Proportion of ISR", f"{proportion_of_isr:.2f}%" if isinstance(proportion_of_isr, (float, int)) else proportion_of_isr)

    st.markdown("These insights are based on available university statistics.")

    student_raw = pd.DataFrame(data.get("student_stats_raw_data", []))
    if not student_raw.empty:
        st.subheader("📊 Distribution of Total Students")
        fig1 = px.histogram(student_raw, x="Total Students", nbins=30, title="University Sizes")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📊 Female to Male Ratio Across Universities")
        fig2 = px.box(student_raw, y="Female:Male Ratio", title="Box Plot of Female:Male Ratios")
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📊 Proportion of ISR Distribution")
        fig3 = px.histogram(student_raw, x="Proportion of ISR", nbins=30, title="Proportion of International Students")
        st.plotly_chart(fig3, use_container_width=True)

        with st.expander("📄 Raw Student Stats Data"):
            st.dataframe(student_raw)
    else:
        st.warning("Student statistics data is not available from the API.")
