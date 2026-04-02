import time

import altair as alt
import pandas as pd
import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

start_time = time.time()

st.title("Motor Vehicle Collisions - Person (BigQuery)")

st.write(
    """
    This page uses the person-level motor vehicle collisions dataset stored in BigQuery.
    It explores temporal patterns, who gets hurt, and the role of safety equipment.
    """
)

PROJECT_ID = "sipa-adv-c-sparkly-pickle"


def get_bigquery_client():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return bigquery.Client(credentials=credentials, project=PROJECT_ID)


@st.cache_data(ttl=3600)
def load_kpi_metrics():
    client = get_bigquery_client()
    query = """
    SELECT
        COUNT(DISTINCT collision_id)                                      AS total_crashes,
        COUNTIF(LOWER(person_injury) = 'injured')                        AS total_injured,
        COUNTIF(LOWER(person_injury) = 'killed')                         AS total_killed,
        ROUND(
            COUNTIF(LOWER(person_injury) = 'killed') * 100.0
            / NULLIF(COUNT(*), 0), 2
        )                                                                 AS fatality_rate
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person`
    WHERE crash_date IS NOT NULL
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False).iloc[0]


@st.cache_data(ttl=3600)
def load_weekday_person_type():
    client = get_bigquery_client()
    query = """
    SELECT
        FORMAT_DATE('%A', DATE(crash_date)) AS weekday,
        CASE
            WHEN LOWER(person_type) LIKE '%pedestrian%' THEN 'Pedestrian'
            WHEN LOWER(person_type) LIKE '%bicyclist%'  THEN 'Cyclist'
            WHEN LOWER(person_type) LIKE '%driver%'     THEN 'Driver'
            WHEN LOWER(person_type) LIKE '%occupant%'   THEN 'Occupant'
            ELSE 'Other'
        END AS person_type,
        COUNT(*) AS people
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person`
    WHERE crash_date IS NOT NULL
      AND person_type IS NOT NULL
    GROUP BY weekday, person_type
    """
    df = client.query(query).to_dataframe(create_bqstorage_client=False)
    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    df["weekday"] = pd.Categorical(
        df["weekday"], categories=weekday_order, ordered=True
    )
    return df.sort_values("weekday")


@st.cache_data(ttl=3600)
def load_hour_weekday_heatmap():
    client = get_bigquery_client()
    query = """
    SELECT
        FORMAT_DATE('%A', DATE(crash_date)) AS weekday,
        EXTRACT(HOUR FROM crash_date)       AS hour,
        COUNT(DISTINCT collision_id)        AS crashes
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person`
    WHERE crash_date IS NOT NULL
    GROUP BY weekday, hour
    """
    df = client.query(query).to_dataframe(create_bqstorage_client=False)
    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    df["weekday"] = pd.Categorical(
        df["weekday"], categories=weekday_order, ordered=True
    )
    return df


@st.cache_data(ttl=3600)
def load_safety_equipment():
    client = get_bigquery_client()
    query = """
    SELECT
        CASE
            WHEN safety_equipment IS NULL OR TRIM(safety_equipment) = ''
                THEN 'Unknown / Not recorded'
            WHEN LOWER(safety_equipment) LIKE '%lap belt%'
              OR LOWER(safety_equipment) LIKE '%shoulder%'
              OR LOWER(safety_equipment) LIKE '%harness%'
                THEN 'Seatbelt worn'
            WHEN LOWER(safety_equipment) LIKE '%none%'
                THEN 'No safety equipment'
            WHEN LOWER(safety_equipment) LIKE '%helmet%'
                THEN 'Helmet worn'
            WHEN LOWER(safety_equipment) LIKE '%air bag%'
              OR LOWER(safety_equipment) LIKE '%airbag%'
                THEN 'Airbag deployed'
            ELSE 'Other equipment'
        END AS equipment,
        CASE
            WHEN LOWER(person_injury) = 'killed'  THEN 'Killed'
            WHEN LOWER(person_injury) = 'injured' THEN 'Injured'
            ELSE 'No injury'
        END AS outcome,
        COUNT(*) AS people
    FROM `sipa-adv-c-sparkly-pickle.nyc_data.motor_vehicle_collisions_person`
    WHERE person_type IN ('Driver', 'Occupant')
      AND person_injury IS NOT NULL
    GROUP BY equipment, outcome
    """
    return client.query(query).to_dataframe(create_bqstorage_client=False)


with st.spinner("Loading data from BigQuery..."):
    kpi = load_kpi_metrics()
    weekday_df = load_weekday_person_type()
    heatmap_df = load_hour_weekday_heatmap()
    safety_df = load_safety_equipment()

if weekday_df.empty:
    st.warning("No data available.")
    st.stop()

st.markdown("### At a glance")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total crashes", f"{int(kpi['total_crashes']):,}")
col2.metric("People injured", f"{int(kpi['total_injured']):,}")
col3.metric("Fatalities", f"{int(kpi['total_killed']):,}")
col4.metric("Fatality rate", f"{kpi['fatality_rate']:.2f}%")

st.markdown("---")
st.markdown("### Who gets hurt, and when?")
st.write(
    """
    Each bar shows the total number of people involved in crashes on that day,
    broken down by their role - driver, occupant, pedestrian, or cyclist.
    This reveals not just when crashes peak, but who bears the risk.
    """
)

weekday_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

type_color_scale = alt.Scale(
    domain=["Driver", "Occupant", "Pedestrian", "Cyclist", "Other"],
    range=["#185FA5", "#85B7EB", "#D85A30", "#1D9E75", "#888780"],
)

selection = alt.selection_point(fields=["person_type"], bind="legend")

stacked_bar = (
    alt.Chart(weekday_df)
    .mark_bar()
    .encode(
        x=alt.X(
            "weekday:N",
            sort=weekday_order,
            title="Day of week",
            axis=alt.Axis(labelAngle=0),
        ),
        y=alt.Y("people:Q", title="Number of people"),
        color=alt.Color(
            "person_type:N",
            scale=type_color_scale,
            legend=alt.Legend(title="Person type", orient="top"),
        ),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
        tooltip=[
            alt.Tooltip("weekday:N", title="Day"),
            alt.Tooltip("person_type:N", title="Person type"),
            alt.Tooltip("people:Q", title="Count", format=","),
        ],
    )
    .add_params(selection)
    .properties(height=320)
)

st.altair_chart(stacked_bar, use_container_width=True)

st.write(
    """
    Fridays consistently show the highest overall count, driven mainly by driver and occupant
    involvement. Pedestrian risk remains relatively stable across the week but spikes slightly
    on weekends, likely reflecting night-time activity patterns.
    """
)

st.markdown("---")
st.markdown("### When do crashes happen? Hour x day heatmap")
st.write(
    """
    Each cell encodes crash count for that hour-day combination.
    Darker cells mean more crashes. This reveals commuter peaks, late-night patterns,
    and how weekends differ from weekdays.
    """
)

heatmap_df["hour_label"] = heatmap_df["hour"].apply(
    lambda h: (
        "12a"
        if h == 0
        else ("12p" if h == 12 else (f"{h}a" if h < 12 else f"{h - 12}p"))
    )
)

hour_label_order = [
    "12a",
    "1a",
    "2a",
    "3a",
    "4a",
    "5a",
    "6a",
    "7a",
    "8a",
    "9a",
    "10a",
    "11a",
    "12p",
    "1p",
    "2p",
    "3p",
    "4p",
    "5p",
    "6p",
    "7p",
    "8p",
    "9p",
    "10p",
    "11p",
]

brush = alt.selection_interval(encodings=["x"])

heatmap = (
    alt.Chart(heatmap_df)
    .mark_rect()
    .encode(
        x=alt.X(
            "hour_label:O",
            sort=hour_label_order,
            title="Hour of day",
            axis=alt.Axis(labelAngle=0, labelFontSize=10),
        ),
        y=alt.Y("weekday:O", sort=weekday_order, title=None),
        color=alt.Color(
            "crashes:Q",
            scale=alt.Scale(scheme="blues"),
            legend=alt.Legend(title="Crashes"),
        ),
        tooltip=[
            alt.Tooltip("weekday:N", title="Day"),
            alt.Tooltip("hour_label:O", title="Hour"),
            alt.Tooltip("crashes:Q", title="Crashes", format=","),
        ],
    )
    .add_params(brush)
    .properties(height=220)
)

st.altair_chart(heatmap, use_container_width=True)

st.write(
    """
    The classic double-peak commuter pattern appears strongly on weekdays -
    8-9am and 4-6pm. Weekend nights (Friday and Saturday after 10pm) show a
    distinct elevated risk band absent on weekdays, consistent with recreational travel.
    """
)

st.markdown("---")
st.markdown("### Does safety equipment make a difference?")
st.write(
    """
    Among drivers and occupants, this chart compares injury outcomes across
    different safety equipment states, offering a direct look at the protective
    effect of seatbelts and airbags.
    """
)

safety_filtered = safety_df[
    safety_df["equipment"].isin(
        ["Seatbelt worn", "No safety equipment", "Airbag deployed", "Other equipment"]
    )
    & safety_df["outcome"].isin(["Killed", "Injured", "No injury"])
].copy()

outcome_color_scale = alt.Scale(
    domain=["No injury", "Injured", "Killed"],
    range=["#1D9E75", "#EF9F27", "#E24B4A"],
)

safety_chart = (
    alt.Chart(safety_filtered)
    .mark_bar()
    .encode(
        x=alt.X(
            "people:Q",
            title="Number of people",
            stack="normalize",
            axis=alt.Axis(format="%"),
        ),
        y=alt.Y("equipment:N", title=None, sort="-x"),
        color=alt.Color(
            "outcome:N",
            scale=outcome_color_scale,
            legend=alt.Legend(title="Outcome", orient="top"),
        ),
        tooltip=[
            alt.Tooltip("equipment:N", title="Equipment"),
            alt.Tooltip("outcome:N", title="Outcome"),
            alt.Tooltip("people:Q", title="Count", format=","),
        ],
    )
    .properties(height=200)
)

st.altair_chart(safety_chart, use_container_width=True)

st.write(
    """
    People with no safety equipment show a notably higher proportion of serious injuries
    and fatalities compared to those wearing seatbelts. The 'Unknown / Not recorded'
    category is large - a known limitation of police-reported data - so interpret
    absolute proportions with caution.
    """
)

st.markdown("---")
with st.expander("Download underlying data"):
    st.download_button(
        label="Download weekday x person type (CSV)",
        data=weekday_df.to_csv(index=False),
        file_name="weekday_person_type.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download hour x weekday heatmap (CSV)",
        data=heatmap_df.to_csv(index=False),
        file_name="hour_weekday_heatmap.csv",
        mime="text/csv",
    )
    st.download_button(
        label="Download safety equipment outcomes (CSV)",
        data=safety_df.to_csv(index=False),
        file_name="safety_equipment_outcomes.csv",
        mime="text/csv",
    )

elapsed = time.time() - start_time
st.caption(f"Page loaded in {elapsed:.2f} seconds")
