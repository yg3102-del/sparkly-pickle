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
    SELECT date, crashes
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.daily_crash_counts_2026`
    ORDER BY date
    """

    return client.query(query).to_dataframe(create_bqstorage_client=False)


@st.cache_data(ttl=3600)
def load_borough_counts():
    client = get_bigquery_client()

    query = """
    SELECT borough, crashes
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.borough_crash_counts_2026`
    ORDER BY crashes DESC
    """

    return client.query(query).to_dataframe(create_bqstorage_client=False)


# =====================================================
# 3️⃣ load data
# =====================================================

with st.spinner("Loading data from BigQuery..."):
    daily_counts = load_daily_counts()
    borough_counts = load_borough_counts()

if daily_counts.empty:
    st.warning("No data available.")
    st.stop()

# =====================================================
# Daily Trend
# =====================================================


st.markdown("### Daily Trend Analysis")

st.write(
    """
    This chart shows how crash counts change over time.
    It helps identify fluctuations and short-term patterns in collision activity.
    """
)

daily_chart = (
    alt.Chart(daily_counts)
    .mark_line()
    .encode(
        x="date:T",
        y="crashes:Q",
        tooltip=["date", "crashes"],
    )
)

st.subheader("Crashes by Day (BigQuery)")
st.altair_chart(daily_chart, width="stretch")

st.markdown("### Key Insight")

st.write(
    """
Crash counts fluctuate across time rather than remaining constant.
Most days fall within a moderate range, suggesting a relatively stable baseline level of collisions.

Occasional spikes indicate days with unusually high activity, which may be influenced by traffic patterns,
weather conditions, or other external factors.
"""
)

# =====================================================
# Borough Analysis
# =====================================================
st.markdown("### Borough Analysis")

st.write(
    """
This chart compares crash counts across boroughs,
highlighting geographic differences in collision patterns.
"""
)

borough_chart = (
    alt.Chart(borough_counts)
    .mark_bar()
    .encode(
        x="borough:N",
        y="crashes:Q",
        tooltip=["borough", "crashes"],
    )
)

st.subheader("Crashes by Borough (BigQuery)")
st.altair_chart(borough_chart, width="stretch")

st.markdown("### Key Insight")

st.write(
    """
The borough-level comparison reveals that motor vehicle collisions are unevenly distributed across New York City. Some boroughs experience significantly higher crash counts, indicating spatial concentration of traffic risk.
These differences are likely driven by variations in population density, traffic volume, and urban infrastructure. Boroughs with higher levels of economic activity and mobility tend to exhibit greater exposure to collision risk.
This spatial inequality suggests that traffic safety challenges are not uniform across the city. Instead, they are context-dependent and require localized policy responses. For example, high-risk boroughs may benefit from targeted interventions such as traffic calming measures, improved pedestrian infrastructure, and stricter enforcement.
From a policy perspective, the findings highlight the importance of geographically differentiated strategies rather than one-size-fits-all solutions when addressing urban traffic safety.
"""
)

# =====================================================
# Load time
# =====================================================
elapsed = time.time() - start_time
st.caption(f"Page loaded in {elapsed:.2f} seconds")
