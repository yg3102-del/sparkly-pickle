import time
import time
import streamlit as st
import pandas as pd
import altair as alt
from google.oauth2 import service_account
from google.cloud import bigquery

start_time = time.time()

st.title("Motor Vehicle Collisions — Merged Dataset (2026 Live)")
st.write(
    """
    Combining crash-level and person-level BigQuery data to examine
    temporal trends, geographic patterns, and contributing factors.
    """
)

# ─────────────────────────────────────────────
# BigQuery client — unchanged from original
# ─────────────────────────────────────────────

PROJECT_ID = "sipa-adv-c-sparkly-pickle"


def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials, project=PROJECT_ID)


# ─────────────────────────────────────────────
# Data loaders
# ─────────────────────────────────────────────


@st.cache_data(ttl=3600)
def load_kpi():
    client = get_bigquery_client()
    query = """
    SELECT
        SUM(crashes)                          AS total_crashes,
        MAX(crashes)                          AS peak_day_crashes,
        (SELECT date FROM `sipa-adv-c-sparkly-pickle.nyc_data.daily_crash_counts_2026`
         ORDER BY crashes DESC LIMIT 1)       AS peak_date
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.daily_crash_counts_2026`
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False).iloc[0]


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
    WHERE borough IS NOT NULL AND TRIM(borough) != ''
    ORDER BY crashes DESC
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False)


@st.cache_data(ttl=3600)
def load_contributing_factors():
    client = get_bigquery_client()
    query = """
    SELECT
        contributing_factor_vehicle_1 AS factor,
        COUNT(*) AS crashes
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
    WHERE contributing_factor_vehicle_1 IS NOT NULL
      AND LOWER(contributing_factor_vehicle_1) NOT IN ('unspecified', '')
      AND EXTRACT(YEAR FROM crash_date) = 2026
    GROUP BY factor
    ORDER BY crashes DESC
    LIMIT 10
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False)


@st.cache_data(ttl=3600)
def load_victim_trends():
    client = get_bigquery_client()
    query = """
    SELECT
        DATE_TRUNC(crash_date, MONTH)          AS month,
        SUM(number_of_pedestrians_killed)      AS pedestrians_killed,
        SUM(number_of_cyclist_killed)          AS cyclists_killed,
        SUM(number_of_motorist_killed)         AS motorists_killed
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_crash`
    WHERE EXTRACT(YEAR FROM crash_date) = 2026
    GROUP BY month
    ORDER BY month
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False)


# ─────────────────────────────────────────────
# Load all data
# ─────────────────────────────────────────────

with st.spinner("Loading data from BigQuery..."):
    kpi = load_kpi()
    daily_counts = load_daily_counts()
    borough_counts = load_borough_counts()
    factors_df = load_contributing_factors()
    victim_df = load_victim_trends()

if daily_counts.empty:
    st.warning("No data available.")
    st.stop()

# ─────────────────────────────────────────────
# KPI metrics row
# ─────────────────────────────────────────────

st.markdown("### At a glance")

col1, col2, col3 = st.columns(3)
col1.metric("Total crashes (YTD)", f"{int(kpi['total_crashes']):,}")
col2.metric("Peak single day", f"{int(kpi['peak_day_crashes']):,}")
col3.metric(
    "Worst borough",
    borough_counts.iloc[0]["borough"].title() if not borough_counts.empty else "N/A",
)

# ─────────────────────────────────────────────
# Chart 1 — Daily trend + 7-day rolling average
# ─────────────────────────────────────────────

st.markdown("---")
st.markdown("### Daily trend — crashes over time")
st.write(
    """
    The raw daily count (thin line) shows day-to-day volatility.
    The 7-day rolling average (thick line) smooths out noise to reveal the underlying trend.
    """
)

daily_counts["date"] = pd.to_datetime(daily_counts["date"])
daily_counts = daily_counts.sort_values("date")
daily_counts["rolling_7"] = (
    daily_counts["crashes"].rolling(7, min_periods=1).mean().round(1)
)

raw_line = (
    alt.Chart(daily_counts)
    .mark_line(opacity=0.35, strokeWidth=1)
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("crashes:Q", title="Crashes"),
        tooltip=[
            alt.Tooltip("date:T", title="Date"),
            alt.Tooltip("crashes:Q", title="Crashes"),
        ],
    )
)

rolling_line = (
    alt.Chart(daily_counts)
    .mark_line(strokeWidth=2.5, color="#185FA5")
    .encode(
        x="date:T",
        y=alt.Y("rolling_7:Q", title="Crashes"),
        tooltip=[
            alt.Tooltip("date:T", title="Date"),
            alt.Tooltip("rolling_7:Q", title="7-day avg", format=".1f"),
        ],
    )
)

st.altair_chart(
    (raw_line + rolling_line).properties(height=300), use_container_width=True
)

st.write(
    """
    Crash counts fluctuate day to day but the rolling average reveals a
    relatively stable baseline. Occasional spikes may reflect weather events,
    holidays, or other external factors.
    """
)

# ─────────────────────────────────────────────
# Chart 2 — Borough comparison (interactive)
# ─────────────────────────────────────────────

st.markdown("---")
st.markdown("### Crashes by borough")
st.write("Click a bar to highlight it. Hover for exact counts.")

borough_counts["borough"] = borough_counts["borough"].str.title()

selection = alt.selection_point(fields=["borough"])

borough_chart = (
    alt.Chart(borough_counts)
    .mark_bar()
    .encode(
        x=alt.X("crashes:Q", title="Number of crashes"),
        y=alt.Y("borough:N", sort="-x", title=None),
        color=alt.condition(selection, alt.value("#185FA5"), alt.value("#B5D4F4")),
        tooltip=[
            alt.Tooltip("borough:N", title="Borough"),
            alt.Tooltip("crashes:Q", title="Crashes", format=","),
        ],
    )
    .add_params(selection)
    .properties(height=220)
)

st.altair_chart(borough_chart, use_container_width=True)

st.write(
    """
    Collisions are unevenly distributed across the five boroughs.
    Brooklyn and Queens consistently lead, likely due to higher population
    density and traffic volume. Staten Island records the fewest crashes.
    """
)

# ─────────────────────────────────────────────
# Chart 3 — Top contributing factors
# ─────────────────────────────────────────────

st.markdown("---")
st.markdown("### Top 10 contributing factors")
st.write(
    "What causes most crashes? Based on the primary contributing factor recorded by police."
)

factors_chart = (
    alt.Chart(factors_df)
    .mark_bar(color="#1D9E75")
    .encode(
        x=alt.X("crashes:Q", title="Number of crashes"),
        y=alt.Y("factor:N", sort="-x", title=None),
        tooltip=[
            alt.Tooltip("factor:N", title="Factor"),
            alt.Tooltip("crashes:Q", title="Crashes", format=","),
        ],
    )
    .properties(height=320)
)

st.altair_chart(factors_chart, use_container_width=True)

st.write(
    """
    Driver inattention and distraction is typically the leading cause by a wide margin,
    followed by failure to yield and following too closely. These behavioral factors
    suggest that enforcement and awareness campaigns may be more effective than
    infrastructure changes alone.
    """
)

# ─────────────────────────────────────────────
# Chart 4 — Victim type killed per month
# ─────────────────────────────────────────────

if not victim_df.empty and victim_df["month"].notna().any():
    st.markdown("---")
    st.markdown("### Fatalities by victim type — monthly")
    st.write(
        "Tracking pedestrian, cyclist, and motorist fatalities over time "
        "to monitor Vision Zero progress."
    )

    victim_df["month"] = pd.to_datetime(victim_df["month"])

    victim_long = victim_df.melt(
        id_vars="month",
        value_vars=["pedestrians_killed", "cyclists_killed", "motorists_killed"],
        var_name="victim_type",
        value_name="killed",
    )
    victim_long["victim_type"] = victim_long["victim_type"].map(
        {
            "pedestrians_killed": "Pedestrian",
            "cyclists_killed": "Cyclist",
            "motorists_killed": "Motorist",
        }
    )

    victim_color = alt.Scale(
        domain=["Pedestrian", "Cyclist", "Motorist"],
        range=["#D85A30", "#1D9E75", "#185FA5"],
    )

    victim_chart = (
        alt.Chart(victim_long)
        .mark_line(point=True)
        .encode(
            x=alt.X("month:T", title="Month"),
            y=alt.Y("killed:Q", title="Fatalities"),
            color=alt.Color(
                "victim_type:N",
                scale=victim_color,
                legend=alt.Legend(title="Victim type", orient="top"),
            ),
            tooltip=[
                alt.Tooltip("month:T", title="Month"),
                alt.Tooltip("victim_type:N", title="Type"),
                alt.Tooltip("killed:Q", title="Killed"),
            ],
        )
        .properties(height=280)
    )

    st.altair_chart(victim_chart, use_container_width=True)

    st.write(
        """
        Pedestrians consistently account for the largest share of fatalities.
        Monitoring these trends monthly helps assess whether Vision Zero
        initiatives are reducing the most vulnerable road users' risk.
        """
    )

# ─────────────────────────────────────────────
# Download
# ─────────────────────────────────────────────

st.markdown("---")
with st.expander("Download underlying data"):
    st.download_button(
        label="Download daily counts (CSV)",
        data=daily_counts.to_csv(index=False),
        file_name="daily_crash_counts_2026.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download borough counts (CSV)",
        data=borough_counts.to_csv(index=False),
        file_name="borough_crash_counts_2026.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download contributing factors (CSV)",
        data=factors_df.to_csv(index=False),
        file_name="contributing_factors_2026.csv",
        mime="text/csv",
    )

# ─────────────────────────────────────────────
# Load time
# ─────────────────────────────────────────────

elapsed = time.time() - start_time
st.caption(f"Page loaded in {elapsed:.2f} seconds")
