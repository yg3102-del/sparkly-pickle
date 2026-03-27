## Data Loading Strategy

For all datasets in this project, we use a **full refresh loading strategy**.

Each time the transfer script runs, it pulls the latest available data from the NYC Open Data API and replaces the corresponding table in BigQuery. We use this approach for both the person-level dataset and the crash-level dataset.

### Why we chose full refresh loading

We chose full refresh loading for three reasons:

1. **Simplicity**  
   This approach is straightforward to implement and easy to maintain in a course project setting.

2. **Data consistency**  
   Replacing the full table helps avoid duplicate records and ensures that the BigQuery table reflects one consistent version of the dataset after each run.

3. **Easy verification**  
   Full refresh loading makes it easier to validate whether the data transfer worked correctly, since the output table is fully regenerated each time.

### Datasets covered

- **Motor Vehicle Collisions - Person**  
  Loaded from the NYC Open Data API into the BigQuery table  
  `nyc_data.motor_vehicle_collisions_person`

- **Motor Vehicle Collisions - Crash**  
  Loaded from the NYC Open Data API into the BigQuery table  
  `nyc_data.motor_vehicle_collisions_crash`

In addition, we create pre-aggregated BigQuery tables for performance optimization:

- `nyc_data.daily_crash_counts_2026`
- `nyc_data.borough_crash_counts_2026`

These aggregated tables are also recreated during each run, following the same full refresh logic.