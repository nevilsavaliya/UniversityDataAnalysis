import streamlit as st
import pandas as pd
import plotly.express as px

from university_board.utils.fetch_api import fetch_scatter_data


def show():
    st.subheader("📈 Teaching Score vs Student-Staff Ratio")

    try:
        scatter_data = fetch_scatter_data()
        scatter_df = pd.DataFrame(scatter_data)

        if scatter_df.empty:
            st.warning("No scatter data available from API.")
            return

        fig = px.scatter(
            scatter_df,
            x='Student-Staff Ratio',
            y='Teaching Score',
            color='Location',
            title="Teaching Score vs Student-Staff Ratio",
            opacity=0.7,
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📄 Raw Scatter Data"):
            st.dataframe(scatter_df)

    except Exception as e:
        st.error(f"🚫 Failed to load scatter data: {e}")
