import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="NYC Open Data App", layout="wide")
st.title('NYC Motor Vehicle Collisions')

st.subheader("Team Members")
st.write("Yiran Ge, Yizi Qu")

st.markdown("---")

@st.cache_data
def load_data():
    url = "https://data.cityofnewyork.us/resource/f55k-p6yu.json?$limit=5000"
    df = pd.read_json(url)
    return df

df = load_data()

st.header("Dataset Preview")
st.write("Total rows:", len(df))
st.dataframe(df.head())

st.markdown("---")

st.header("Simple Visualization")

