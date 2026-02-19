import streamlit as st
import pandas as pd
import altair as alt

st.title("📌 Page 2: Part 1 Dataset (NYC Crashes)")

@st.cache_data
def load_data():
    url = "https://data.cityofnewyork.us/resource/f55k-p6yu.json?$limit=20000"
    return pd.read_json(url)

df = load_data()

st.write("Rows:", len(df))
st.dataframe(df.head(15), use_container_width=True)

st.markdown("---")
st.subheader("Meaningful Visualization: Monthly Trend of Injuries vs Fatalities")

needed = ["crash_date", "number_of_persons_injured", "number_of_persons_killed"]
missing = [c for c in needed if c not in df.columns]

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

df["crash_date"] = pd.to_datetime(df["crash_date"], errors="coerce")
df["number_of_persons_injured"] = pd.to_numeric(df["number_of_persons_injured"], errors="coerce").fillna(0)
df["number_of_persons_killed"] = pd.to_numeric(df["number_of_persons_killed"], errors="coerce").fillna(0)

df = df.dropna(subset=["crash_date"])


monthly = (
    df.assign(month=df["crash_date"].dt.to_period("M").dt.to_timestamp())
      .groupby("month", as_index=False)[["number_of_persons_injured", "number_of_persons_killed"]]
      .sum()
)


monthly_long = monthly.melt(
    id_vars="month",
    value_vars=["number_of_persons_injured", "number_of_persons_killed"],
    var_name="metric",
    value_name="count",
)


monthly_long["metric"] = monthly_long["metric"].map({
    "number_of_persons_injured": "Injured",
    "number_of_persons_killed": "Killed"
})

chart = (
    alt.Chart(monthly_long)
    .mark_line(point=True)
    .encode(
        x=alt.X("month:T", title="Month"),
        y=alt.Y("count:Q", title="People (sum)"),
        color=alt.Color("metric:N", title="Outcome"),
        tooltip=[alt.Tooltip("month:T", title="Month"), "metric:N", alt.Tooltip("count:Q", format=",")]
    )
    .properties(height=420)
)

st.altair_chart(chart, use_container_width=True)

st.caption("This chart shows how total injuries and fatalities change over time (monthly sums) in the NYC crashes dataset.")