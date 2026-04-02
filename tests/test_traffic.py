import pandas as pd

from src.nyc_open_data import build_url, load_paginated


def test_params():
    base_url = "https://example.com/resource.json"
    where = "crash_date between '2022-01-01T00:00:00' and '2022-12-31T23:59:59'"
    url = build_url(base_url, where, limit=50000, offset=0)

    assert url.startswith(base_url + "?")
    assert "%24where=" in url or "$where=" in url  # urlencode usually encodes "$" as %24
    assert "%24limit=50000" in url or "$limit=50000" in url
    assert "%24offset=0" in url or "$offset=0" in url


def test_pages():
    calls = {"n": 0}
    pages = [
        pd.DataFrame({"a": [1, 2]}),
        pd.DataFrame({"a": [3]}),
        pd.DataFrame(),  # stop condition
    ]

    def read_json_2(url: str) -> pd.DataFrame:
        calls["n"] += 1
        return pages[calls["n"] - 1]

    df = load_paginated(
        base_url="https://example.com/resource.json",
        where="x=1",
        limit=50000,
        read_json=read_json_2,
    )

    assert df.shape[0] == 3
    assert calls["n"] == 3


def test__increment():
    seen_urls = []

    pages = [
        pd.DataFrame({"a": [1]}),
        pd.DataFrame({"a": [2]}),
        pd.DataFrame(),  # stop
    ]

    def read_json_2(url: str) -> pd.DataFrame:
        seen_urls.append(url)
        return pages[len(seen_urls) - 1]

    _ = load_paginated(
        base_url="https://example.com/resource.json",
        where="x=1",
        limit=50000,
        read_json=read_json_2,
    )

    # Expect offsets: 0, 50000, 100000
    assert ("%24offset=0" in seen_urls[0]) or ("$offset=0" in seen_urls[0])
    assert ("%24offset=50000" in seen_urls[1]) or ("$offset=50000" in seen_urls[1])
    assert ("%24offset=100000" in seen_urls[2]) or ("$offset=100000" in seen_urls[2])
