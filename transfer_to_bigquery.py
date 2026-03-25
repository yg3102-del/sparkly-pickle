import pandas as pd
from urllib.parse import urlencode
from google.cloud import bigquery
import pandas_gbq

PROJECT_ID = "sipa-adv-c-sparkly-pickle"
DATASET_ID = "nyc_data"
TABLE_ID = "motor_vehicle_collisions_person"

API_URL = "https://data.cityofnewyork.us/resource/f55k-p6yu.json"


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


def get_data():
    params = {
        "$limit": 50000
    }

    url = f"{API_URL}?{urlencode(params)}"
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


def upload_to_bigquery(df):
    pandas_gbq.to_gbq(
        df,
        destination_table=f"{DATASET_ID}.{TABLE_ID}",
        project_id=PROJECT_ID,
        if_exists="replace",
    )
    print("Upload finished.")


def main():
    create_dataset_if_needed()
    df = get_data()
    print(df.head())
    print(df.shape)
    upload_to_bigquery(df)


if __name__ == "__main__":
    main()