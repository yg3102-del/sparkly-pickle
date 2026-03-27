import time
import streamlit as st
import pandas as pd
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

@st.cache_data(ttl=3600)
def load_person_from_bigquery():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

    query = """
    SELECT collision_id, crash_date
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person`
    """

    df = client.query(query).to_dataframe(create_bqstorage_client=False)
    return df


# =====================================================
# 2️⃣ Crash data loading for 2026
# =====================================================


@st.cache_data(ttl=3600)
def load_crash_from_bigquery():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

    query = """
    SELECT collision_id, crash_date, borough
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
    """

    df = client.query(query).to_dataframe(create_bqstorage_client=False)
    return df


# =====================================================
# 3️⃣ load data
# =====================================================

with st.spinner("Loading data from BigQuery..."):
    person_df = load_person_from_bigquery()
    crash_df = load_crash_from_bigquery()

if person_df.empty or crash_df.empty:
    st.warning("No data available.")
    st.stop()

person_df["crash_date"] = pd.to_datetime(person_df["crash_date"], errors="coerce")
crash_df["crash_date"] = pd.to_datetime(crash_df["crash_date"], errors="coerce")

# =====================================================
# 4️⃣ Merge
# =====================================================

merged_df = pd.merge(person_df, crash_df, on="collision_id", how="inner")

st.subheader("Merged Dataset Summary")

st.write("Person rows:", person_df.shape[0])
st.write("Crash rows:", crash_df.shape[0])
st.write("Merged rows:", merged_df.shape[0])
st.write("Merged columns:", merged_df.shape[1])

st.dataframe(merged_df.head(20), width="stretch")

st.markdown("### Why merge the datasets?")
st.write(
    """
    Merging the two datasets allows us to connect information from different levels of the collision records.
    This gives us a broader view of crash patterns and helps support more meaningful analysis.
    """
)

# =====================================================
# 5️⃣ crashes by day of week analysis
# =====================================================

unique_crashes = merged_df.drop_duplicates(subset="collision_id").copy()

# =====================================================
# Daily Trend
# =====================================================
st.markdown("### Daily Trend Analysis")
st.write(
    """
    This line chart shows how the number of crashes changes over time in 2026.
    It helps us see whether crash counts remain stable or fluctuate across different days.
    """
)

unique_crashes["date"] = unique_crashes["crash_date_x"].dt.date

daily_counts = unique_crashes.groupby("date").size().reset_index(name="crashes")

daily_chart = (
    alt.Chart(daily_counts)
    .mark_line()
    .encode(x="date:T", y="crashes:Q", tooltip=["date", "crashes"])
)

st.subheader("Crashes by Day (BigQuery)")
st.altair_chart(daily_chart, width="stretch")

# markdowm
st.markdown("### Daily Trend Takeaway")
st.write(
    """
    The daily trend visualization helps us monitor short-term variation in crash activity.
    This is useful for identifying peaks, drops, or irregular patterns in the live dataset.
    """
)
st.markdown("### Key Insights")

st.write("""
The chart shows that daily crash counts in New York City fluctuate throughout the year rather than remaining constant. 
Most days fall between roughly 180 and 260 crashes, indicating a relatively stable baseline level of collision activity.

Several spikes above 300 crashes appear during the period, suggesting that certain days experience unusually high collision activity. 
These fluctuations may be influenced by factors such as traffic volume, commuting patterns, weather conditions, or special events.

Overall, the data suggests that motor vehicle collisions occur consistently across time, with moderate daily variation but no clear long-term trend during the observed period.
""")

st.write("""
Future analysis could explore whether these daily fluctuations are associated with specific factors such as weekday patterns, borough differences, or weather conditions.
""")


# Borough analysis
st.markdown("### Borough Analysis")
st.write(
    """
    This chart compares crash counts across boroughs.
    It helps us understand whether collisions are concentrated in specific parts of the city.
    """
)

if "borough" in unique_crashes.columns:
    borough_counts = unique_crashes["borough"].value_counts().reset_index()

    borough_counts.columns = ["borough", "crashes"]

    borough_chart = (
        alt.Chart(borough_counts)
        .mark_bar()
        .encode(x="borough:N", y="crashes:Q", tooltip=["borough", "crashes"])
    )

    st.subheader("Crashes by Borough (2026 Live)")
    st.altair_chart(borough_chart, use_container_width=True)

# markdown
st.markdown("### Borough Takeaway")
st.write(
    """
    Comparing borough-level crash counts provides a spatial view of the dataset.
    This can help users think about geographic differences in traffic safety patterns.
    """
)

st.markdown("### Key Insights")

st.write("""
The chart shows that motor vehicle collisions are not evenly distributed across the five boroughs of New York City. 
Brooklyn records the highest number of crashes, followed by Queens, while Staten Island has the lowest crash count.

These differences may reflect variations in population density, traffic volume, and road network complexity across boroughs. 
Areas with larger populations and heavier traffic flows tend to experience more collisions.

This spatial comparison highlights how geographic context plays an important role in understanding urban traffic safety patterns.
""")

st.markdown("### Future Work")
st.write(
    """
    In the future, we would like to use these datasets to explore more complex and more realistic public safety questions.
    We also want to deepen the analysis by adding more comparisons, clearer interpretation, and stronger real-world context.
    """
)

elapsed = time.time() - start_time
st.caption(f"Page loaded in {elapsed:.2f} seconds")