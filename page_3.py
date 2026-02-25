import streamlit as st
import pandas as pd
from urllib.parse import urlencode

st.title("Motor Vehicle Collisions - Merged Dataset (2022 Only)")

# =====================================================
# 1️⃣ Load Person Data (2022)
# =====================================================

@st.cache_data
def load_person_2022():
    base_url = "https://data.cityofnewyork.us/resource/f55k-p6yu.json"
    limit = 50000
    offset = 0
    all_data = []

    while True:
        query_params = {
            "$where": "crash_date between '2022-01-01T00:00:00' and '2022-12-31T23:59:59'",
            "$limit": limit,
            "$offset": offset
        }

        url = f"{base_url}?{urlencode(query_params)}"
        df = pd.read_json(url)

        if df.empty:
            break

        all_data.append(df)
        offset += limit

    return pd.concat(all_data, ignore_index=True)


# =====================================================
# 2️⃣ Load Crash Data (2022)
# =====================================================

@st.cache_data
def load_crash_2022():
    base_url = "https://data.cityofnewyork.us/resource/h9gi-nx95.json"
    limit = 50000
    offset = 0
    all_data = []

    while True:
        query_params = {
            "$where": "crash_date between '2022-01-01T00:00:00' and '2022-12-31T23:59:59'",
            "$limit": limit,
            "$offset": offset
        }

        url = f"{base_url}?{urlencode(query_params)}"
        df = pd.read_json(url)

        if df.empty:
            break

        all_data.append(df)
        offset += limit

    return pd.concat(all_data, ignore_index=True)


# =====================================================
# 3️⃣ Load Both
# =====================================================

person_df = load_person_2022()
crash_df = load_crash_2022()

st.write("Person rows:", person_df.shape[0])
st.write("Crash rows:", crash_df.shape[0])


# =====================================================
# 4️⃣ Merge on collision_id
# =====================================================

merged_df = pd.merge(
    person_df,
    crash_df,
    on="collision_id",
    how="inner"
)

st.write("Merged rows:", merged_df.shape[0])
st.write("Merged columns:", merged_df.shape[1])

st.dataframe(merged_df.head(20))


import matplotlib.pyplot as plt


unique_crashes = merged_df.drop_duplicates(subset="collision_id").copy()


unique_crashes["crash_date"] = pd.to_datetime(unique_crashes["crash_date_y"])

unique_crashes["month"] = unique_crashes["crash_date"].dt.month
monthly_counts = unique_crashes["month"].value_counts().sort_index()

fig1, ax1 = plt.subplots()
monthly_counts.plot(kind="line", marker="o", ax=ax1)

ax1.set_title("Crashes by Month (2022)")
ax1.set_xlabel("Month")
ax1.set_ylabel("Number of Crashes")

st.pyplot(fig1)


borough_counts = unique_crashes["borough"].value_counts()

fig2, ax2 = plt.subplots()
borough_counts.plot(kind="bar", ax=ax2)

ax2.set_title("Crashes by Borough (2022)")
ax2.set_xlabel("Borough")
ax2.set_ylabel("Number of Crashes")

plt.xticks(rotation=45)

st.pyplot(fig2)