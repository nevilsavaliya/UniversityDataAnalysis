import streamlit as st
import pandas as pd
import plotly.express as px
from university_board.utils.fetch_api import fetch_summary


def show():
    data = fetch_summary()
    st.subheader("📈 Teaching Score vs Student-Staff Ratio")
    scatter_df = pd.DataFrame(data.get("scatter_data", []))
    if not scatter_df.empty:
        st.plotly_chart(
            px.scatter(
                scatter_df,
                x='stats_student_staff_ratio',
                y='scores_teaching',
                color='location',
                title="Teaching Score vs Student-Staff Ratio"
            ),
            use_container_width=True
        )
        with st.expander("📄 Raw Scatter Data"):
            st.dataframe(scatter_df)
    else:
        st.warning("No scatter data available from API.")
