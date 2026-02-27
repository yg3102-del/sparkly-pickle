from __future__ import annotations

import pandera as pa
from pandera import Column, DataFrameSchema, Check


# -------- Crash Data --------
_crash_schema = DataFrameSchema(
    {
        "collision_id": Column(
            object,
            nullable=False,
            checks=Check.str_matches(r"^\d+$"),
        ),
        "crash_date": Column(
            "datetime64[ns]",
            nullable=False,
            coerce=True,
        ),
        "borough": Column(
            object,
            nullable=True,
            checks=Check.isin(
                ["BRONX", "BROOKLYN", "MANHATTAN", "QUEENS", "STATEN ISLAND"]
            ),
        ),
        "number_of_persons_injured": Column(
            float,
            nullable=True,
            checks=Check.ge(0),
            coerce=True,
        ),
        "number_of_persons_killed": Column(
            float,
            nullable=True,
            checks=Check.ge(0),
            coerce=True,
        ),
    },
    strict=False,  
)


def validate_crash(df):
    return _crash_schema.validate(df)


# -------- Person Data --------
_person_schema = DataFrameSchema(
    {
        "collision_id": Column(
            object,
            nullable=False,
            checks=Check.str_matches(r"^\d+$"),
        ),
        "crash_date": Column(
            "datetime64[ns]",
            nullable=False,
            coerce=True,
        ),
        "person_type": Column(
            object,
            nullable=True,
        ),
    },
    strict=False,
)


def validate_person(df):
    return _person_schema.validate(df)