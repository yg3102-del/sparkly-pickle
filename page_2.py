import streamlit as st
import pandas as pd
import altair as alt
from urllib.parse import urlencode
from datetime import datetime

st.title("Motor Vehicle Collisions - Person (2026 Live)")

# =====================================================
# 1️⃣ 2026-01-01 till now
# =====================================================


@st.cache_data(ttl=3600)  # 每小时刷新一次
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
# 2️⃣ load data
# =====================================================

with st.spinner("Loading 2026 live data..."):
    person_df = load_person_2026_live()

if person_df.empty:
    st.warning("No 2026 data available yet.")
    st.stop()

# 转换日期格式
person_df["crash_date"] = pd.to_datetime(person_df["crash_date"], errors="coerce")
person_df = person_df.dropna(subset=["crash_date"])

# =====================================================
# 3️⃣ basic summary and raw data preview
# =====================================================

st.subheader("Dataset Summary (2026 Live)")

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

chart = (
    alt.Chart(weekday_counts)
    .mark_bar()
    .encode(
        x=alt.X("weekday:N", sort=weekday_order),
        y="crashes:Q",
        tooltip=["weekday", "crashes"],
    )
)

st.subheader("Crashes by Day of Week (2026 Live)")
st.altair_chart(chart, use_container_width=True)
