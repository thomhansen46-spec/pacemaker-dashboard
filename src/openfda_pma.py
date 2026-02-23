import time
import requests
import pandas as pd
from datetime import date

OPENFDA_PMA_ENDPOINT = "https://api.fda.gov/device/pma.json"


def build_search_query(date_from: str, date_to: str, brand_terms: list[str], product_codes: list[str] | None = None) -> str:
    parts = [
        "decision_code:APPR",
        f"decision_date:[{date_from}+TO+{date_to}]",
    ]

    if brand_terms:
        terms = []
        for t in brand_terms:
            t = t.replace('"', "").strip()
            if t:
                terms.append(f'trade_name:"{t}"')
        if terms:
            parts.append("(" + " OR ".join(terms) + ")")

    if product_codes:
        codes = [c.strip().upper() for c in product_codes if c.strip()]
        if codes:
            parts.append("(" + " OR ".join([f"product_code:{c}" for c in codes]) + ")")

    return " AND ".join(parts)


def fetch_openfda_pma(search_query: str, api_key: str = "", max_records: int = 5000, page_size: int = 500) -> pd.DataFrame:
    rows = []
    skip = 0

    while True:
        params = {
            "search": search_query,
            "limit": page_size,
            "skip": skip,
        }

        if api_key:
            params["api_key"] = api_key

        r = requests.get(OPENFDA_PMA_ENDPOINT, params=params, timeout=30)

        if r.status_code != 200:
            raise RuntimeError(f"openFDA error: HTTP {r.status_code} | {r.text[:300]}")

        payload = r.json()
        results = payload.get("results", [])

        if not results:
            break

        rows.extend(results)
        skip += page_size

        if len(rows) >= max_records:
            break

        time.sleep(0.2)

    df = pd.json_normalize(rows)
    return df


def year_chunks(d_from: date, d_to: date) -> list[tuple[str, str]]:
    chunks = []
    for y in range(d_from.year, d_to.year + 1):
        start = date(y, 1, 1)
        end = date(y, 12, 31)

        if y == d_from.year:
            start = d_from
        if y == d_to.year:
            end = d_to

        chunks.append((start.isoformat(), end.isoformat()))

    return chunks
