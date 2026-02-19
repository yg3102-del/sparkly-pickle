import streamlit as st
import pandas as pd
import altair as alt

# Page Title

st.title("NYC Motor Vehicle Collisions – 2021 Overview")

# Load Data

@st.cache_data
def load_data():
    url = "https://data.cityofnewyork.us/resource/h9gi-nx95.json?$limit=20000"
    return pd.read_json(url)


df = load_data()
st.subheader("Raw Data Preview")
st.dataframe(df.head(100))

st.markdown("---")

st.write(f"Total crashes in 2021 (from sample): {len(df)}")

# Clean Data

df["crash_date"] = pd.to_datetime(df["crash_date"], errors="coerce")
df = df.dropna(subset=["crash_date"])

# 只保留 2021
df_2021 = df[df["crash_date"].dt.year == 2021]

st.write(f"Total crashes in 2021 (from sample): {len(df_2021)}")

st.markdown("---")

# Monthly Trend

st.subheader("Crashes by Month (2021)")

df_2021["month"] = df_2021["crash_date"].dt.month

monthly_counts = df_2021.groupby("month").size().reset_index(name="crashes")

chart_month = (
    alt.Chart(monthly_counts)
    .mark_line(point=True)
    .encode(
        x=alt.X("month:O", title="Month"),
        y=alt.Y("crashes:Q", title="Number of Crashes"),
        tooltip=["month", "crashes"],
    )
)

st.altair_chart(chart_month, use_container_width=True)

st.markdown("---")

#  Borough Distribution

st.subheader("Crashes by Borough (2021)")

# Keep only the five valid boroughs
valid_boroughs = [
    "BRONX",
    "BROOKLYN",
    "MANHATTAN",
    "QUEENS",
    "STATEN ISLAND"
]

df_2021_clean = df_2021[df_2021["borough"].isin(valid_boroughs)]

# Count crashes
borough_counts = (
    df_2021_clean["borough"]
    .value_counts()
    .reset_index()
)

borough_counts.columns = ["borough", "crashes"]

# Create bar chart
chart_borough = (
    alt.Chart(borough_counts)
    .mark_bar()
    .encode(
        x=alt.X("borough:N", title="Borough"),
        y=alt.Y("crashes:Q", title="Number of Crashes"),
        tooltip=["borough", "crashes"]
    )
)

st.altair_chart(chart_borough, width="stretch")
