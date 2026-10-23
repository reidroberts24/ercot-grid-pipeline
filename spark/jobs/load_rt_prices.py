"""Load one day of raw real-time settlement point prices (ERCOT NP6-905-CD)
from the landed API responses into the raw Iceberg table iceberg.raw.rt_prices.

    docker compose exec spark spark-submit /home/iceberg/spark/jobs/load_rt_prices.py --date 2026-10-15

Reads data/raw/ercot/np6-905-cd/delivery_date=<date>/*.json (written by
ingestion/fetch_rt_prices.py). Values stay as ERCOT sent them; only column names
become snake_case and each column gets its type. Reruns replace the day in a
single atomic commit, so they never duplicate rows.
"""

import argparse
import logging
from datetime import date

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

log = logging.getLogger(__name__)

RAW_ROOT = "/home/iceberg/data/raw/ercot/np6-905-cd"
TABLE = "iceberg.raw.rt_prices"

# (ERCOT field name, column name, Spark type), in the order ERCOT sends them.
FIELDS = [
    ("deliveryDate", "delivery_date", "date"),
    ("deliveryHour", "delivery_hour", "int"),
    ("deliveryInterval", "delivery_interval", "int"),
    ("settlementPoint", "settlement_point", "string"),
    ("settlementPointType", "settlement_point_type", "string"),
    ("settlementPointPrice", "settlement_point_price", "double"),
    ("DSTFlag", "dst_flag", "boolean"),
]

# Not partitioned yet: week 5 benchmarks partitioning, so it needs a "before".
CREATE_TABLE = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
    delivery_date          DATE      COMMENT 'Operating day, Central prevailing time',
    delivery_hour          INT       COMMENT 'Hour ending, 1-24 (Central prevailing time)',
    delivery_interval      INT       COMMENT '15-minute interval within the hour, 1-4',
    settlement_point       STRING,
    settlement_point_type  STRING    COMMENT 'HU hub, AH hub average, LZ load zone, LZEW energy-weighted load zone, ...',
    settlement_point_price DOUBLE    COMMENT 'USD/MWh; can be negative or spike far above normal',
    dst_flag               BOOLEAN   COMMENT 'True for the repeated hour on the fall DST day',
    _source_file           STRING    COMMENT 'Landed API response this row came from',
    _fetched_at_utc        TIMESTAMP COMMENT 'When the response was fetched from ERCOT',
    _loaded_at_utc         TIMESTAMP COMMENT 'When this job wrote the row'
)
USING iceberg
COMMENT 'Raw ERCOT NP6-905-CD real-time settlement point prices. Grain: one row per settlement point, settlement point type, and 15-minute delivery interval, as published.'
"""


def read_day(spark, day):
    responses = (
        spark.read.option("multiLine", True)
        .json(f"{RAW_ROOT}/delivery_date={day.isoformat()}/*.json")
        .withColumn("_source_file", F.col("_metadata.file_path"))
    )
    pages = responses.select(
        "_source_file",
        F.col("fetched_at_utc"),
        F.explode("pages").alias("page"),
    )

    # Rows are positional arrays, so fail loudly if ERCOT ever reorders or
    # renames a field instead of loading prices into the wrong column.
    expected = [ercot_name for ercot_name, _, _ in FIELDS]
    for (names,) in pages.select(F.col("page.fields.name")).distinct().collect():
        if names != expected:
            raise ValueError(f"Unexpected NP6-905-CD fields: {names}, expected {expected}")

    # JSON rows mix strings, numbers, and booleans, so Spark reads every value
    # as a string; cast each column to its real type.
    rows = pages.select("_source_file", "fetched_at_utc", F.explode("page.data").alias("row"))
    return rows.select(
        *[F.col("row")[i].cast(spark_type).alias(name) for i, (_, name, spark_type) in enumerate(FIELDS)],
        "_source_file",
        F.to_timestamp("fetched_at_utc").alias("_fetched_at_utc"),
        F.current_timestamp().alias("_loaded_at_utc"),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--date", required=True, type=date.fromisoformat, help="delivery date, YYYY-MM-DD")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    spark = (
        SparkSession.builder.appName("load_rt_prices")
        # Timestamps are interpreted and written in UTC, whatever the container's clock says.
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    spark.sql("CREATE NAMESPACE IF NOT EXISTS iceberg.raw")
    spark.sql(CREATE_TABLE)

    df = read_day(spark, args.date)
    row_count = df.count()
    if row_count == 0:
        raise ValueError(f"No rows found for {args.date}; was it fetched?")

    # Delete the day's existing rows and add the new ones in one commit. Iceberg
    # can do this because each load writes files containing only that day.
    df.writeTo(TABLE).overwrite(F.col("delivery_date") == F.lit(args.date))
    log.info("Loaded %d rows for %s into %s", row_count, args.date, TABLE)


if __name__ == "__main__":
    main()
