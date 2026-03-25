import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from google.oauth2 import service_account
from google.cloud import bigquery

st.title("Motor Vehicle Collisions - Person (BigQuery)")

st.write(
    """
    This page uses the 2026 live person-level motor vehicle collisions dataset from NYC Open Data.
    It provides a basic summary of the dataset and explores how crash frequency varies by day of the week.
    """
)

# =====================================================
# 1️⃣ 2026-01-01 till now
# =====================================================

PROJECT_ID = "sipa-adv-c-sparkly-pickle"

def load_person_2026_from_bigquery():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )

    client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

    query = """
    SELECT *
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person`
    """

    df = client.query(query).to_dataframe()
    return df

# =====================================================
# 2️⃣ load data
# =====================================================

with st.spinner("Loading 2026 live data..."):
    person_df = load_person_2026_from_bigquery()

if person_df.empty:
    st.warning("No 2026 data available yet.")
    st.stop()


person_df["crash_date"] = pd.to_datetime(person_df["crash_date"], errors="coerce")
person_df = person_df.dropna(subset=["crash_date"])

# =====================================================
# 3️⃣ basic summary and raw data preview
# =====================================================
st.markdown("### Page Goal")
st.write(
    """
    The goal of this page is to introduce the first dataset and provide an initial view of temporal patterns in collisions.
    """
)

st.subheader("Dataset Summary (BigQuery)")

st.write("Rows loaded:", person_df.shape[0])
st.write(
    "Date range:", person_df["crash_date"].min(), "to", person_df["crash_date"].max()
)

st.write("Last updated at:", datetime.now())

st.subheader("Raw Data Preview")
st.dataframe(person_df.head(20), use_container_width=True)

# =====================================================
# 4️⃣ crashes by day of week analysis
# =====================================================

unique_crashes = person_df.drop_duplicates(subset="collision_id").copy()

unique_crashes["weekday"] = unique_crashes["crash_date"].dt.day_name()

weekday_counts = unique_crashes["weekday"].value_counts().reset_index()

weekday_counts.columns = ["weekday", "crashes"]

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

# =====================================================
# 5️⃣ Visualization
# =====================================================
st.markdown("### Why this chart matters")
st.write(
    """
    Looking at crashes by day of the week helps us identify whether collisions are distributed evenly
    or whether certain days show higher crash frequency.
    """
)

chart = (
    alt.Chart(weekday_counts)
    .mark_bar()
    .encode(
        x=alt.X("weekday:N", sort=weekday_order),
        y="crashes:Q",
        tooltip=["weekday", "crashes"],
    )
)

st.subheader("Crashes by Day of Week (BigQuery)")
st.altair_chart(chart, use_container_width=True)

# markdowm
st.markdown("### Key Takeaway")
st.write(
    """
    This chart gives an initial overview of how crashes are distributed across the week.
    It helps us begin identifying whether weekdays or weekends show different collision patterns.
    """
)
st.markdown("### Key Insights")

st.write("""
The chart shows that motor vehicle collisions vary across different days of the week rather than being evenly distributed.

Crash counts gradually increase toward the end of the work week, with Friday recording the highest number of collisions. 
This may reflect higher traffic volumes and increased travel activity as the week progresses.

Weekend patterns differ slightly, with Saturday remaining relatively high but Sunday showing the lowest crash count.
Overall, the pattern suggests that commuting behavior and traffic intensity likely play an important role in shaping collision risk.
""")
