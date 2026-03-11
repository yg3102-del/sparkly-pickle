import streamlit as st

st.set_page_config(page_title="NYC Open Data App", layout="wide")

st.title("NYC Motor Vehicle Collisions")

st.subheader("🏠 Team Members")
st.write("Yiran Ge, Yizi Qu")

st.markdown("---")

st.header("Project Overview")
st.write(
    """
    This project explores traffic collision patterns in New York City using NYC Open Data.
    We use live 2026 data to build an interactive Streamlit app that helps users explore
    crash patterns and better understand public safety trends.
    """
)

st.header("Research Question")
st.write(
    """
    How can NYC motor vehicle collision data be used to reveal meaningful patterns in crash timing,
    frequency, and location through interactive visualization?
    """
)

st.header("Why This Matters")
st.write(
    """
    Traffic collisions are an important public safety issue. By analyzing open data, we can better
    understand when and where crashes occur and use visualization to make urban safety data more accessible.
    """
)

st.header("Data Sources")
st.write(
    """
    We use two NYC Open Data datasets: a person-level motor vehicle collisions dataset and a crash-level
    motor vehicle collisions dataset. We also merge the datasets to explore broader patterns.
    """
)

st.header("Method")
st.write(
    """
    Our project uses live API data collection, basic data cleaning, dataset merging, and interactive
    visualization in Streamlit. We focus on exploratory analysis to identify patterns by weekday, date,
    and borough.
    """
)

st.header("Updated Proposal / New Insights")
st.write(
    """
    After building the current version of the app, we found that the visualizations already help present
    the data clearly. We also realized that the project could be improved by using the data to explore
    more complex and more meaningful real-world questions in the future.
    """
)

st.markdown("---")
st.subheader("Navigation")
st.write("Use the sidebar to navigate:")
st.write("- **Page 2**: Person-level dataset and weekday crash visualization")
st.write("- **Page 3**: Merged dataset, daily crash trends, and borough analysis")