from __future__ import annotations

import pandas as pd


WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def unique_by_collision(df: pd.DataFrame, id_col: str = "collision_id") -> pd.DataFrame:
    """
    Deduplicate by collision_id (or another id column).
    """
    if id_col not in df.columns:
        raise KeyError(f"Missing required column: {id_col}")
    return df.drop_duplicates(subset=id_col).copy()


def _coerce_datetime_and_dropna(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    if date_col not in df.columns:
        raise KeyError(f"Missing required column: {date_col}")
    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col], errors="coerce")
    out = out.dropna(subset=[date_col])
    return out


def weekday_counts(df: pd.DataFrame, date_col: str, id_col: str | None = None) -> pd.DataFrame:
    work = df.copy()

    if id_col is not None:
        work = work.drop_duplicates(subset=id_col).copy()

    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work = work.dropna(subset=[date_col])

    if work.empty:
        return pd.DataFrame(columns=["weekday", "crashes"])

    weekdays = work[date_col].dt.day_name()
    counts = weekdays.value_counts()

   
    counts = counts.reindex(WEEKDAY_ORDER).dropna().astype(int)

    out = counts.reset_index()
    out.columns = ["weekday", "crashes"]  
    return out


def monthly_counts(df: pd.DataFrame, date_col: str, id_col: str | None = None) -> pd.DataFrame:
    work = df.copy()

    if id_col is not None:
        work = work.drop_duplicates(subset=id_col).copy()

    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")
    work = work.dropna(subset=[date_col])

    if work.empty:
        return pd.DataFrame(columns=["month", "crashes"])

    months = work[date_col].dt.month
    counts = months.value_counts().sort_index().astype(int)

    out = counts.reset_index()
    out.columns = ["month", "crashes"]   
    return out


def value_counts_df(df: pd.DataFrame, col: str, dropna: bool = True) -> pd.DataFrame:
    """
    Generic value counts to DataFrame: value, count
    """
    if col not in df.columns:
        raise KeyError(f"Missing required column: {col}")

    series = df[col]
    counts = series.value_counts(dropna=dropna).astype(int)
    out = counts.reset_index()
    out.columns = [col, "count"]
    return out