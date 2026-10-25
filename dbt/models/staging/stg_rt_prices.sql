with source as (
    select * from {{ source('ercot', 'rt_prices') }}
)
select
    settlement_point,
    settlement_point_type,
    -- ERCOT times are Central, hour-ending 1-24, interval 1-4.
    -- Start of interval in local time, then converted to UTC.
    -- Not correct on the fall DST day yet; that's week 5.
    cast(
        with_timezone(
            date_add(
                'minute',
                (delivery_hour - 1) * 60 + (delivery_interval - 1) * 15,
                cast(delivery_date as timestamp(6))
            ),
            'America/Chicago'
        ) at time zone 'UTC'
        as timestamp(6)
    ) as interval_start_utc,
    settlement_point_price as price_usd_per_mwh,
    delivery_date,
    dst_flag,
    _loaded_at_utc
from source