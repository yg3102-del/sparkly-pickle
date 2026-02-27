import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.nyc_open_data import load_person_2022, load_crash_2022
from src.analytics import unique_by_collision, monthly_counts, value_counts_df

st.title("Motor Vehicle Collisions - Merged Dataset")


@st.cache_data
def get_person_df_2022() -> pd.DataFrame:
    return load_person_2022()


@st.cache_data
def get_crash_df_2022() -> pd.DataFrame:
    return load_crash_2022()


person_df = get_person_df_2022()
crash_df = get_crash_df_2022()

st.write("Person rows:", person_df.shape[0])
st.write("Crash rows:", crash_df.shape[0])

merged_df = pd.merge(person_df, crash_df, on="collision_id", how="inner")
st.write("Merged rows:", merged_df.shape[0])
st.write("Merged columns:", merged_df.shape[1])

st.dataframe(merged_df.head(20), use_container_width=True)

# --- dedupe ---
unique_crashes = unique_by_collision(merged_df, id_col="collision_id")

# crash_date column in merged data might differ
# your original code used crash_date_y
date_col = "crash_date_y" if "crash_date_y" in unique_crashes.columns else "crash_date"

# --- monthly counts ---
monthly_df = monthly_counts(unique_crashes, date_col=date_col)
monthly_series = monthly_df.set_index("month")["crashes"]

fig1, ax1 = plt.subplots()
monthly_series.plot(kind="line", marker="o", ax=ax1)
ax1.set_title("Crashes by Month (2022)")
ax1.set_xlabel("Month")
ax1.set_ylabel("Number of Crashes")
st.pyplot(fig1)

# --- borough counts ---
if "borough" in unique_crashes.columns:
    borough_df = value_counts_df(unique_crashes, "borough")
    borough_series = borough_df.set_index("borough")["count"]

    fig2, ax2 = plt.subplots()
    borough_series.plot(kind="bar", ax=ax2)
    ax2.set_title("Crashes by Borough (2022)")
    ax2.set_xlabel("Borough")
    ax2.set_ylabel("Number of Crashes")
    plt.xticks(rotation=45)
    st.pyplot(fig2)
else:
    st.warning("Column 'borough' not found in merged dataset.")
