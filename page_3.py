import time
import streamlit as st
import altair as alt
from google.oauth2 import service_account
from google.cloud import bigquery

start_time = time.time()

st.title("Motor Vehicle Collisions - Merged Dataset (2026 Live)")
st.write(
    """
    This page merges two live 2026 NYC collision datasets to support broader exploratory analysis.
    By combining person-level and crash-level data, we can examine trends across time and location.
    """
)

# =====================================================
# 1️⃣ real-time data loading for 2026
# =====================================================

PROJECT_ID = "sipa-adv-c-sparkly-pickle"


def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials, project=PROJECT_ID)


# =====================================================
# 2️⃣ Crash data loading for 2026
# =====================================================


@st.cache_data(ttl=3600)
def load_daily_counts():
    client = get_bigquery_client()

    query = """
    SELECT
        DATE(p.crash_date) AS date,
        COUNT(DISTINCT p.collision_id) AS crashes
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person` AS p
    INNER JOIN `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash` AS c
        ON p.collision_id = c.collision_id
    WHERE p.crash_date >= '2026-01-01'
    GROUP BY date
    ORDER BY date
    """

    return client.query(query).to_dataframe(create_bqstorage_client=False)


@st.cache_data(ttl=3600)
def load_borough_counts():
    client = get_bigquery_client()

    query = """
    SELECT
        c.borough,
        COUNT(DISTINCT p.collision_id) AS crashes
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person` AS p
    INNER JOIN `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash` AS c
        ON p.collision_id = c.collision_id
    WHERE p.crash_date >= '2026-01-01'
      AND c.borough IS NOT NULL
    GROUP BY c.borough
    ORDER BY crashes DESC
    """

    return client.query(query).to_dataframe(create_bqstorage_client=False)


# =====================================================
# 3️⃣ load data
# =====================================================

with st.spinner("Loading data from BigQuery..."):
    daily_counts = load_daily_counts()
    borough_counts = load_borough_counts()


# =====================================================
# 4️⃣ Merge
# =====================================================


st.markdown("### Why merge the datasets?")
st.write(
    """
    Combining the two datasets helps connect person-level information with crash-level
    location information. This supports a broader view of collision patterns across time
    and geography.
    """
)

st.markdown("### Daily Trend Analysis")
st.write(
    """
    This line chart shows how the number of crashes changes over time.
    It helps us see whether crash counts remain relatively stable or fluctuate across days.
    """
)

daily_chart = (
    alt.Chart(daily_counts)
    .mark_line()
    .encode(x="date:T", y="crashes:Q", tooltip=["date", "crashes"])
)

st.subheader("Crashes by Day (BigQuery)")
st.altair_chart(daily_chart, width="stretch")

# =====================================================
# Daily Trend
# =====================================================


st.markdown("### Daily Trend Takeaway")
st.write(
    """
    The daily trend chart provides a simple view of short-term variation in collision activity.
    It helps identify whether there are spikes, drops, or recurring patterns over time.
    """
)

st.markdown("### Key Insights")
st.write(
    """
The chart shows that daily crash counts in New York City vary over time rather than remaining constant.
Most days fall within a moderate range, suggesting a relatively stable baseline level of collision activity.

Some days still show noticeable spikes, which may reflect changes in traffic volume, commuting patterns,
weather conditions, or other short-term factors.

Overall, the pattern suggests that collisions occur consistently across time, with moderate daily variation.
"""
)

st.markdown("### Borough Analysis")
st.write(
    """
    This bar chart compares crash counts across boroughs.
    It helps show whether collisions are concentrated in specific parts of the city.
    """
)

if not borough_counts.empty:
    borough_chart = (
        alt.Chart(borough_counts)
        .mark_bar()
        .encode(x="borough:N", y="crashes:Q", tooltip=["borough", "crashes"])
    )

    st.subheader("Crashes by Borough (BigQuery)")
    st.altair_chart(borough_chart, width="stretch")

st.markdown("### Borough Takeaway")
st.write(
    """
    Borough-level comparison gives a spatial view of collision patterns.
    This helps users think about how traffic safety may vary across different parts of the city.
    """
)

st.markdown("### Key Insights")
st.write(
    """
The chart shows that motor vehicle collisions are not evenly distributed across the boroughs of New York City.
Some boroughs record substantially more crashes than others.

These differences may reflect variation in population density, traffic volume, and road network complexity.

This comparison highlights how geographic context plays an important role in understanding urban traffic safety patterns.
"""
)

st.markdown("### Future Work")
st.write(
    """
    In the future, we would like to extend this analysis with more variables and more detailed comparisons.
    We also want to connect these patterns to broader public safety questions.
    """
)

elapsed = time.time() - start_time
st.caption(f"Page loaded in {elapsed:.2f} seconds")
