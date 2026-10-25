select
    settlement_point,
    date_trunc('hour', interval_start_utc) as hour_start_utc,
    avg(price_usd_per_mwh) as avg_price_usd_per_mwh,
    count(*) as intervals
from {{ ref('stg_rt_prices') }}
where settlement_point_type = 'HU'
    and delivery_date = date '2026-10-15'
group by 1, 2
order by 1, 2