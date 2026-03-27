import time
import streamlit as st
import pandas as pd
import altair as alt
from google.oauth2 import service_account
from google.cloud import bigquery

start_time = time.time()

st.title("Motor Vehicle Collisions - Person (BigQuery)")

st.write(
    """
    This page uses the person-level motor vehicle collisions dataset stored in BigQuery.
    It focuses on how crash frequency varies by day of the week.
    """
)

PROJECT_ID = "sipa-adv-c-sparkly-pickle"


def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials, project=PROJECT_ID)


@st.cache_data(ttl=3600)
def load_weekday_counts():
    client = get_bigquery_client()

    query = """
    WITH unique_crashes AS (
        SELECT
            collision_id,
            MIN(crash_date) AS crash_date
        FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person`
        WHERE crash_date IS NOT NULL
        GROUP BY collision_id
    )
    SELECT
        FORMAT_DATE('%A', DATE(crash_date)) AS weekday,
        COUNT(*) AS crashes
    FROM unique_crashes
    GROUP BY weekday
    """

    df = client.query(query).to_dataframe(create_bqstorage_client=False)

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    df["weekday"] = pd.Categorical(
        df["weekday"], categories=weekday_order, ordered=True
    )
    df = df.sort_values("weekday")

    return df


with st.spinner("Loading data from BigQuery..."):
    weekday_counts = load_weekday_counts()

if weekday_counts.empty:
    st.warning("No data available.")
    st.stop()

st.markdown("### Page Goal")
st.write(
    """
    The goal of this page is to introduce the first dataset and provide an initial view of temporal patterns in collisions.
    """
)

st.markdown("### Why this chart matters")
st.write(
    """
    Looking at crashes by day of the week helps us identify whether collisions are distributed evenly
    or whether certain days show higher crash frequency.
    """
)

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

chart = (
    alt.Chart(weekday_counts)
    .mark_bar()
    .encode(
        x=alt.X("weekday:N", sort=weekday_order),
        y=alt.Y("crashes:Q"),
        tooltip=["weekday", "crashes"],
    )
)

st.subheader("Crashes by Day of Week (BigQuery)")
st.altair_chart(chart, width="stretch")

st.markdown("### Key Takeaway")
st.write(
    """
    This chart gives an initial overview of how crashes are distributed across the week.
    It helps us begin identifying whether weekdays or weekends show different collision patterns.
    """
)

st.markdown("### Key Insights")
st.write(
    """
The chart shows that motor vehicle collisions vary across different days of the week rather than being evenly distributed.

Crash counts gradually increase toward the end of the work week, with Friday recording the highest number of collisions.
This may reflect higher traffic volumes and increased travel activity as the week progresses.

Weekend patterns differ slightly, with Saturday remaining relatively high but Sunday showing the lowest crash count.
Overall, the pattern suggests that commuting behavior and traffic intensity likely play an important role in shaping collision risk.
"""
)

elapsed = time.time() - start_time
st.caption(f"Page loaded in {elapsed:.2f} seconds")
