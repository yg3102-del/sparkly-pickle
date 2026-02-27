from __future__ import annotations

from urllib.parse import urlencode
from typing import Callable, Optional

import pandas as pd
from src.validation import validate_crash, validate_person


def build_url(base_url: str, where: str, limit: int, offset: int) -> str:
    """
    Build a Socrata API URL with paging params.
    """
    params = {
        "$where": where,
        "$limit": limit,
        "$offset": offset,
    }
    return f"{base_url}?{urlencode(params)}"


def load_paginated(
    base_url: str,
    where: str,
    limit: int = 50_000,
    read_json: Callable[[str], pd.DataFrame] = pd.read_json,
    max_pages: Optional[int] = None,
) -> pd.DataFrame:
    """
    Load all pages from a Socrata endpoint using limit/offset paging until empty page.

    - read_json is injected to make unit tests deterministic (no network).
    - max_pages is optional safety guard.
    """
    all_pages: list[pd.DataFrame] = []
    offset = 0
    pages = 0

    while True:
        url = build_url(base_url, where, limit, offset)
        df = read_json(url)

        if df is None or df.empty:
            break

        all_pages.append(df)
        offset += limit
        pages += 1

        if max_pages is not None and pages >= max_pages:
            break

    if not all_pages:
        return pd.DataFrame()

    return pd.concat(all_pages, ignore_index=True)


def load_person_2022(
    read_json: Callable[[str], pd.DataFrame] = pd.read_json,
    limit: int = 50_000,
) -> pd.DataFrame:
    base_url = "https://data.cityofnewyork.us/resource/f55k-p6yu.json"
    where = "crash_date between '2022-01-01T00:00:00' and '2022-12-31T23:59:59'"

    df = load_paginated(
        base_url=base_url,
        where=where,
        limit=limit,
        read_json=read_json,
    )

    df = validate_person(df)
    return df


def load_crash_2022(
    read_json: Callable[[str], pd.DataFrame] = pd.read_json,
    limit: int = 50_000,
) -> pd.DataFrame:
    base_url = "https://data.cityofnewyork.us/resource/h9gi-nx95.json"
    where = "crash_date between '2022-01-01T00:00:00' and '2022-12-31T23:59:59'"

    df = load_paginated(
        base_url=base_url,
        where=where,
        limit=limit,
        read_json=read_json,
    )

    df = validate_crash(df)
    return df
