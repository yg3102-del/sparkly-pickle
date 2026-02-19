import streamlit as st
import pandas as pd
import altair as alt

st.title("NYC Traffic Crashes")


url = "https://data.cityofnewyork.us/resource/f55k-p6yu.json?$limit=20000"
df = pd.read_json(url)

df["crash_date"] = pd.to_datetime(df["crash_date"], errors="coerce")
df = df.dropna(subset=["crash_date"])


df_2025 = df[df["crash_date"].dt.year == 2022]

st.subheader("Raw Data")
st.dataframe(df_2025.head(20), use_container_width=True)

st.subheader("Crashes by Day of Week ")


df_2025["weekday"] = df_2025["crash_date"].dt.day_name()

weekday_counts = (
    df_2025["weekday"]
    .value_counts()
    .reset_index()
)

weekday_counts.columns = ["weekday", "crashes"]

chart = (
    alt.Chart(weekday_counts)
    .mark_bar()
    .encode(
        x=alt.X("weekday:N", sort=[
            "Monday","Tuesday","Wednesday","Thursday",
            "Friday","Saturday","Sunday"
        ]),
        y="crashes:Q",
        tooltip=["weekday", "crashes"]
    )
)

st.altair_chart(chart, use_container_width=True)