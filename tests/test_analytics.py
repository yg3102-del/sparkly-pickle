import pandas as pd
import pytest
from src.analytics import monthly_counts, unique_by_collision, value_counts_df, weekday_counts


def test_dedupes():
    df = pd.DataFrame({"collision_id": [1, 1, 2], "x": [10, 11, 20]})
    out = unique_by_collision(df)
    expected_n = 2
    assert out.shape[0] == expected_n
    assert set(out["collision_id"]) == {1, 2}


def test_basic():
    df = pd.DataFrame(
        {
            "collision_id": [1, 2, 3],
            "crash_date": ["2022-01-03", "2022-01-03", "2022-01-04"],  # Mon, Mon, Tue
        }
    )
    out = weekday_counts(df, date_col="crash_date", id_col=None)
    # convert to dict for easy asserts
    d = dict(zip(out["weekday"], out["crashes"], strict=True))
    expected_monday = 2
    expected_tuesday = 1
    assert d["Monday"] == expected_monday
    assert d["Tuesday"] == expected_tuesday


def test_dates():
    df = pd.DataFrame({"collision_id": [1, 2, 3], "crash_date": ["2022-01-03", None, "not-a-date"]})
    out = weekday_counts(df, date_col="crash_date")
    d = dict(zip(out["weekday"], out["crashes"], strict=True))
    assert d["Monday"] == 1
    assert "Tuesday" not in d  # nothing else valid


def test_weekday_counts_empty_d_empty():
    df = pd.DataFrame({"crash_date": []})
    out = weekday_counts(df, date_col="crash_date")
    assert list(out.columns) == ["weekday", "crashes"]
    assert out.shape[0] == 0


def test_monthly_counts():
    df = pd.DataFrame(
        {
            "collision_id": [1, 2, 3],
            "crash_date": ["2022-01-15", "2022-01-20", "2022-02-01"],
        }
    )
    out = monthly_counts(df, date_col="crash_date")
    d = dict(zip(out["month"], out["crashes"], strict=True))
    expected_jan = 2
    expected_feb = 1
    assert d[1] == expected_jan
    assert d[2] == expected_feb


def test_value_counts():
    df = pd.DataFrame({"borough": ["MANHATTAN", "MANHATTAN", "QUEENS"]})
    out = value_counts_df(df, "borough")
    d = dict(zip(out["borough"], out["count"], strict=True))
    expected_manhattan = 2
    expected_queens = 1
    assert d["MANHATTAN"] == expected_manhattan
    assert d["QUEENS"] == expected_queens


def test_missing_column():
    df = pd.DataFrame({"x": [1]})
    with pytest.raises(KeyError):
        _ = unique_by_collision(df)
