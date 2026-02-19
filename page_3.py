import streamlit as st
import pandas as pd
import altair as alt

st.title("Motor Vehicle Collisions – Full Dataset")

url = "https://data.cityofnewyork.us/resource/h9gi-nx95.json?$limit=20000"
df = pd.read_json(url)


df["crash_date"] = pd.to_datetime(df["crash_date"], errors="coerce")
df = df.dropna(subset=["crash_date"])

df["year"] = df["crash_date"].dt.year

st.subheader("Raw Data Preview")
st.dataframe(df.head(20), use_container_width=True)

year_counts = (
    df["year"]
    .value_counts()
    .sort_index()
    .reset_index()
)

year_counts.columns = ["year", "crashes"]

chart = (
    alt.Chart(year_counts)
    .mark_bar()
    .encode(
        x="year:O",
        y="crashes:Q",
        tooltip=["year", "crashes"]
    )
)

st.subheader("Crashes by Year")
st.altair_chart(chart, use_container_width=True)
