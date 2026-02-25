import streamlit as st
import pandas as pd
import altair as alt
from urllib.parse import urlencode

st.title("Motor Vehicle Collisions - Person (2022)")

@st.cache_data
def load_person_2022():
    base_url = "https://data.cityofnewyork.us/resource/f55k-p6yu.json"
    
    all_data = []
    limit = 50000
    offset = 0
    
    while True:
        query_params = {
            "$where": "crash_date between '2022-01-01T00:00:00' and '2022-12-31T23:59:59'",
            "$limit": limit,
            "$offset": offset
        }
        
        query_string = urlencode(query_params)
        url = f"{base_url}?{query_string}"
        
        df = pd.read_json(url)
        
        if df.empty:
            break
        
        all_data.append(df)
        offset += limit
        
    return pd.concat(all_data, ignore_index=True)

person_df = load_person_2022()

st.write("Rows loaded:", person_df.shape[0])
st.write("Date range:", person_df["crash_date"].min(), "to", person_df["crash_date"].max())

st.dataframe(person_df.head(20))



import matplotlib.pyplot as plt

# 确保 crash_date 是 datetime
person_df["crash_date"] = pd.to_datetime(person_df["crash_date"])

# 取唯一 crash（避免一个事故多个人重复计算）
unique_crashes = person_df.drop_duplicates(subset="collision_id")

# 生成 weekday
unique_crashes["weekday"] = unique_crashes["crash_date"].dt.day_name()

# 统计
weekday_counts = unique_crashes["weekday"].value_counts()

# 按顺序排列
order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
weekday_counts = weekday_counts.reindex(order)

# 画图
fig, ax = plt.subplots()
weekday_counts.plot(kind="bar", ax=ax)
ax.set_title("Crashes by Day of Week (2022)")
ax.set_ylabel("Number of Crashes")
ax.set_xlabel("Weekday")

st.pyplot(fig)
