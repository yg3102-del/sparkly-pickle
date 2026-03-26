# NYC Motor Vehicle Collisions App

## Project Overview

This project is a Streamlit app that explores motor vehicle collision patterns in New York City using NYC Open Data. The goal is to make collision data easier to understand through summary statistics, raw data previews, and visualizations.

The project focuses on identifying basic patterns in crash frequency, timing, and distribution. By using interactive charts and cleaned datasets, the app helps users better understand how collisions vary across time.

## Research Goal

The main goal of this project is to explore whether NYC motor vehicle collisions show meaningful patterns across time and other dimensions in the dataset.

More specifically, the project asks:

- Are collisions evenly distributed across the week?
- Do some days show consistently higher crash frequency?
- What can raw person-level collision data tell us about broader crash patterns?

## Data Sources

This project uses NYC Open Data.

### Main dataset
- **Motor Vehicle Collisions - Person**
- API endpoint: `https://data.cityofnewyork.us/resource/f55k-p6yu.json`

This dataset contains person-level records related to motor vehicle collisions, including information such as crash date, collision ID, person type, injury status, and related factors.

### Additional dataset
An additional NYC Open Data dataset is also used in later analysis and merging work in other pages of the app.

## Data Processing

The project pulls data from the NYC Open Data API and transfers it into BigQuery for easier querying and app integration.

The workflow is:

1. Pull data from the API
2. Clean and select the needed columns
3. Upload the dataset to BigQuery
4. Read the BigQuery table in the Streamlit app
5. Use pandas and Altair to summarize and visualize the results

## App Structure

The app is organized into multiple pages though streamlit app:
https://sparkly-pickle-vluncnqsyee7xht3my7b7m.streamlit.app/

### `main_page.py`
This page introduces the project and provides a starting point for users.

### `page_2.py`
This page focuses on the person-level motor vehicle collision dataset stored in BigQuery.

It includes:
- a short explanation of the page goal
- a dataset summary
- a raw data preview
- a bar chart showing crashes by day of the week
- a short written interpretation of the chart

This page is designed to give users a first look at temporal collision patterns.

### `page_3.py`
This page includes additional analysis based on merged or expanded data sources.

### `transfer_to_bigquery.py`
This script pulls data from the NYC Open Data API and uploads it to BigQuery. It is used to populate the database before running the app.

## Main Visualization

One of the main visualizations in this project is the **Crashes by Day of Week** bar chart.

### What this chart shows
This chart counts unique collisions by weekday. It helps show whether crashes are spread evenly across the week or whether some days experience more collisions than others.

### Why this chart matters
This is an important first step in understanding temporal patterns in traffic safety. If collisions are more concentrated on certain days, that may reflect commuting behavior, traffic volume, or other recurring patterns.

### Key takeaway
The chart suggests that collisions are not distributed evenly across the week. Crash counts tend to rise toward the end of the work week, with Friday showing especially high counts, while Sunday tends to be lower. This suggests that traffic intensity and weekly travel behavior may shape collision risk.

## Tools Used

- **Python**
- **Streamlit**
- **pandas**
- **Altair**
- **BigQuery**
- **Google Cloud**
- **NYC Open Data API**

## How to Run the Project

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd sparkly-pickle-1
