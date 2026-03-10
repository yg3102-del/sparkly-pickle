import streamlit as st
import pandas as pd
import altair as alt
from urllib.parse import urlencode
from datetime import datetime

st.title("Motor Vehicle Collisions - Merged Dataset (2026 Live)")

# =====================================================
# 1️⃣ real-time data loading for 2026
# =====================================================


@st.cache_data(ttl=3600)
def load_person_2026_live():
    base_url = "https://data.cityofnewyork.us/resource/f55k-p6yu.json"
    limit = 50000
    offset = 0
    all_data = []

    start_date = "2026-01-01T00:00:00"
    end_date = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")

    while True:
        query_params = {
            "$where": f"crash_date between '{start_date}' and '{end_date}'",
            "$limit": limit,
            "$offset": offset,
        }

        url = f"{base_url}?{urlencode(query_params)}"
        df = pd.read_json(url)

        if df.empty:
            break

        all_data.append(df)
        offset += limit

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


# =====================================================
# 2️⃣ Crash data loading for 2026
# =====================================================


@st.cache_data(ttl=3600)
def load_crash_2026_live():
    base_url = "https://data.cityofnewyork.us/resource/h9gi-nx95.json"
    limit = 50000
    offset = 0
    all_data = []

    start_date = "2026-01-01T00:00:00"
    end_date = datetime.today().strftime("%Y-%m-%dT%H:%M:%S")

    while True:
        query_params = {
            "$where": f"crash_date between '{start_date}' and '{end_date}'",
            "$limit": limit,
            "$offset": offset,
        }

        url = f"{base_url}?{urlencode(query_params)}"
        df = pd.read_json(url)

        if df.empty:
            break

        all_data.append(df)
        offset += limit

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


# =====================================================
# 3️⃣ load data
# =====================================================

with st.spinner("Loading 2026 live data..."):
    person_df = load_person_2026_live()
    crash_df = load_crash_2026_live()

if person_df.empty or crash_df.empty:
    st.warning("No 2026 data available yet.")
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

st.dataframe(merged_df.head(20), use_container_width=True)

# =====================================================
# 5️⃣ crashes by day of week analysis
# =====================================================

unique_crashes = merged_df.drop_duplicates(subset="collision_id").copy()

# =====================================================
# Daily Trend
# =====================================================

unique_crashes["date"] = unique_crashes["crash_date_x"].dt.date

daily_counts = unique_crashes.groupby("date").size().reset_index(name="crashes")

daily_chart = (
    alt.Chart(daily_counts)
    .mark_line()
    .encode(x="date:T", y="crashes:Q", tooltip=["date", "crashes"])
)

st.subheader("Crashes by Day (2026 Live)")
st.altair_chart(daily_chart, width="stretch")


# Borough analysis
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
