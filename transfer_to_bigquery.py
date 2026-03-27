import pandas as pd
from urllib.parse import urlencode
from google.cloud import bigquery
import pandas_gbq

PROJECT_ID = "sipa-adv-c-sparkly-pickle"
DATASET_ID = "nyc_data"

PERSON_TABLE_ID = "motor_vehicle_collisions_person"
CRASH_TABLE_ID = "motor_vehicle_collisions_crash"

PERSON_API_URL = "https://data.cityofnewyork.us/resource/f55k-p6yu.json"
CRASH_API_URL = "https://data.cityofnewyork.us/resource/h9gi-nx95.json"

DAILY_TABLE_ID = "daily_crash_counts_2026"
BOROUGH_TABLE_ID = "borough_crash_counts_2026"


def create_dataset_if_needed():
    client = bigquery.Client(project=PROJECT_ID)
    dataset_full_id = f"{PROJECT_ID}.{DATASET_ID}"

    try:
        client.get_dataset(dataset_full_id)
        print("Dataset already exists.")
    except Exception:
        dataset = bigquery.Dataset(dataset_full_id)
        dataset.location = "US"
        client.create_dataset(dataset)
        print("Dataset created.")


def get_person_data():
    params = {
        "$where": "crash_date >= '2026-01-01T00:00:00'",
        "$order": "crash_date DESC",
        "$limit": 50000,
    }
    url = f"{PERSON_API_URL}?{urlencode(params)}"
    df = pd.read_json(url)

    needed_cols = [
        "unique_id",
        "collision_id",
        "crash_date",
        "person_id",
        "person_type",
        "person_injury",
        "vehicle_id",
        "person_age",
        "ejection",
        "emotional_status",
        "bodily_injury",
        "position_in_vehicle",
        "safety_equipment",
        "ped_location",
        "ped_action",
        "complaint",
        "ped_role",
        "contributing_factor_1",
        "person_sex",
    ]

    for col in needed_cols:
        if col not in df.columns:
            df[col] = None

    df = df[needed_cols]
    df["crash_date"] = pd.to_datetime(df["crash_date"], errors="coerce")
    return df


def get_crash_data():
    params = {
        "$where": "crash_date >= '2026-01-01T00:00:00'",
        "$order": "crash_date DESC",
        "$limit": 50000,
    }
    url = f"{CRASH_API_URL}?{urlencode(params)}"
    df = pd.read_json(url)

    needed_cols = [
        "collision_id",
        "crash_date",
        "borough",
        "zip_code",
        "latitude",
        "longitude",
        "location",
        "on_street_name",
        "cross_street_name",
        "off_street_name",
        "number_of_persons_injured",
        "number_of_persons_killed",
        "number_of_pedestrians_injured",
        "number_of_pedestrians_killed",
        "number_of_cyclist_injured",
        "number_of_cyclist_killed",
        "number_of_motorist_injured",
        "number_of_motorist_killed",
        "contributing_factor_vehicle_1",
        "vehicle_type_code1",
    ]

    for col in needed_cols:
        if col not in df.columns:
            df[col] = None

    df = df[needed_cols]
    df["crash_date"] = pd.to_datetime(df["crash_date"], errors="coerce")
    return df


def upload_to_bigquery(df, table_id):
    pandas_gbq.to_gbq(
        df,
        destination_table=f"{DATASET_ID}.{table_id}",
        project_id=PROJECT_ID,
        if_exists="replace",
    )
    print(f"Uploaded to {table_id}.")


def create_aggregated_tables():
    client = bigquery.Client(project=PROJECT_ID)

    daily_query = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.{DAILY_TABLE_ID}` AS
    SELECT
        DATE(p.crash_date) AS date,
        COUNT(DISTINCT p.collision_id) AS crashes
    FROM `{PROJECT_ID}.{DATASET_ID}.{PERSON_TABLE_ID}` AS p
    INNER JOIN `{PROJECT_ID}.{DATASET_ID}.{CRASH_TABLE_ID}` AS c
        ON p.collision_id = c.collision_id
    WHERE p.crash_date >= '2026-01-01'
    GROUP BY date
    ORDER BY date
    """

    borough_query = f"""
    CREATE OR REPLACE TABLE `{PROJECT_ID}.{DATASET_ID}.{BOROUGH_TABLE_ID}` AS
    SELECT
        c.borough,
        COUNT(DISTINCT p.collision_id) AS crashes
    FROM `{PROJECT_ID}.{DATASET_ID}.{PERSON_TABLE_ID}` AS p
    INNER JOIN `{PROJECT_ID}.{DATASET_ID}.{CRASH_TABLE_ID}` AS c
        ON p.collision_id = c.collision_id
    WHERE p.crash_date >= '2026-01-01'
      AND c.borough IS NOT NULL
    GROUP BY c.borough
    ORDER BY crashes DESC
    """

    client.query(daily_query).result()
    client.query(borough_query).result()

    print(f"Created {DAILY_TABLE_ID}.")
    print(f"Created {BOROUGH_TABLE_ID}.")


def main():
    create_dataset_if_needed()

    person_df = get_person_data()
    print("Person data preview:")
    print(person_df.head())
    print(person_df.shape)
    upload_to_bigquery(person_df, PERSON_TABLE_ID)

    crash_df = get_crash_data()
    print("Crash data preview:")
    print(crash_df.head())
    print(crash_df.shape)
    upload_to_bigquery(crash_df, CRASH_TABLE_ID)

    create_aggregated_tables()


if __name__ == "__main__":
    main()
