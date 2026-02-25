import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.nyc_open_data import load_person_2022
from src.analytics import unique_by_collision, weekday_counts

st.title("Motor Vehicle Collisions - Person")

@st.cache_data
def get_person_df_2022() -> pd.DataFrame:
    return load_person_2022()

person_df = get_person_df_2022()

st.write("Rows loaded:", person_df.shape[0])
if "crash_date" in person_df.columns:
    st.write("Date range:", person_df["crash_date"].min(), "to", person_df["crash_date"].max())

st.dataframe(person_df.head(20), use_container_width=True)

# --- analysis  ---
unique_crashes = unique_by_collision(person_df, id_col="collision_id")
weekday_df = weekday_counts(unique_crashes, date_col="crash_date")

# --- plot ---
order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
weekday_series = weekday_df.set_index("weekday").reindex(order)["crashes"].fillna(0)

fig, ax = plt.subplots()
weekday_series.plot(kind="bar", ax=ax)
ax.set_title("Crashes by Day of Week (2022)")
ax.set_ylabel("Number of Crashes")
ax.set_xlabel("Weekday")

st.pyplot(fig)