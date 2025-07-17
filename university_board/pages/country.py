import pandas as pd
import plotly.express as px
import streamlit as st

from university_board.utils.fetch_api import fetch_summary


def show():
    data = fetch_summary()
    st.subheader("🌍 Universities by Location")

    countries = data.get("universities_by_location", {})
    if countries:
        df_country = pd.DataFrame(
            countries.items(), columns=["Country", "University Count"]
        )
        df_country = df_country[df_country["Country"] != "nan"].sort_values(
            by="University Count", ascending=False
        )

        # Bar Chart
        st.plotly_chart(
            px.bar(
                df_country,
                x="Country",
                y="University Count",
                title="University Distribution by Country",
            ),
            use_container_width=True,
        )

        # Choropleth Map
        st.subheader("🗺️ Universities Map by Country")
        fig = px.choropleth(
            df_country,
            locations="Country",
            locationmode="country names",
            color="University Count",
            color_continuous_scale="Blues",
            title="Universities Around the World",
            labels={"University Count": "Number of Universities"},
        )
        fig.update_geos(
            projection_type="natural earth", showcountries=True, countrycolor="white"
        )
        fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📄 Raw Country Data"):
            st.dataframe(df_country)

    else:
        st.warning("No country data available.")
