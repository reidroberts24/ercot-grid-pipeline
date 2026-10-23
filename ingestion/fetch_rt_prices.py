"""Fetch one day of real-time settlement point prices (ERCOT report NP6-905-CD)
for hubs and load zones, and save the raw API responses unchanged.

    python -m ingestion.fetch_rt_prices --date 2026-10-15

Writes data/raw/ercot/np6-905-cd/delivery_date=<date>/<type>.json, one file per
settlement point type. Rerunning a day overwrites its files, so reruns never
duplicate data.
"""

import argparse
import json
import logging
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

from ingestion.ercot_client import ErcotClient

log = logging.getLogger(__name__)

ENDPOINT = "np6-905-cd/spp_node_zone_hub"
OUT_ROOT = Path(__file__).resolve().parents[1] / "data" / "raw" / "ercot" / "np6-905-cd"

# HU = trading hubs, AH = hub average, LZ = load zones, LZEW = load zones with
# energy-weighted prices. LZ and LZEW share settlement point names, so the
# settlement point type is part of a row's natural key.
DEFAULT_TYPES = ("HU", "AH", "LZ", "LZEW")


def fetch_day(client, day, types=DEFAULT_TYPES):
    out_dir = OUT_ROOT / f"delivery_date={day.isoformat()}"
    out_dir.mkdir(parents=True, exist_ok=True)

    for point_type in types:
        params = {
            "deliveryDateFrom": day.isoformat(),
            "deliveryDateTo": day.isoformat(),
            "settlementPointType": point_type,
        }
        pages = client.get_all_pages(ENDPOINT, params)
        record = {
            "endpoint": ENDPOINT,
            "params": params,
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
            "pages": pages,
        }

        # Write to a temp file and rename, so a crash never leaves a
        # half-written file where a complete one is expected.
        path = out_dir / f"{point_type}.json"
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(record))
        tmp.replace(path)

        log.info("%s: %s", point_type, summarize(pages))


def summarize(pages):
    """Rows, settlement points, and intervals per point, for a quick sanity check.

    A normal day has 96 intervals per point (92 or 100 on DST transition days).
    """
    field_names = [f["name"] for f in pages[0]["fields"]]
    point_col = field_names.index("settlementPoint")
    rows = [row for page in pages for row in page["data"]]
    per_point = Counter(row[point_col] for row in rows)
    interval_counts = sorted(set(per_point.values()))
    return f"{len(rows)} rows, {len(per_point)} points, intervals per point: {interval_counts}"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", required=True, type=date.fromisoformat, help="delivery date, YYYY-MM-DD")
    parser.add_argument("--types", nargs="+", default=DEFAULT_TYPES, help="settlement point types to fetch")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    fetch_day(ErcotClient.from_env(), args.date, args.types)


if __name__ == "__main__":
    main()
