import streamlit as st


main_page = st.Page("MVC_app.py", title="Main Page", icon="🎈")
page_2 = st.Page("page_2.py", title="Page 2", icon="❄️")
page_3 = st.Page("page_3.py", title="Page 3", icon="🎉")

pg = st.navigation([main_page, page_2, page_3])

pg.run()