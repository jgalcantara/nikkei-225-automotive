{{
    config(
        materialized='table'
    )
}}

with 
n225_added_prev_close as (
    select *
    from {{ ref('n225_added_prev_close') }}
),
n225_code as (
    select *
    from {{ ref('stg_staging__ext_n225_code') }}
),
n225_info as (
    select * 
    from {{ ref('stg_staging__ext_n225_info')}}
),
n225_max as (
    select ticker, 
        min(low) as year_low,
        max(high) as year_high,
    from {{ ref('n225_added_prev_close') }}
    group by ticker 
),
n225_summary as (
    select
        n225_added_prev_close.date,
        n225_added_prev_close.ticker,
        n225_code_only.company,
        n225_added_prev_close.open,
        n225_added_prev_close.close,
        n225_added_prev_close.high,
        n225_added_prev_close.low,
        n225_yoy_vol.year_high,
        n225_yoy_vol.year_low,
        n225_added_prev_close.volume,
        n225_added_prev_close.avg_vol_30d,
        n225_added_prev_close.prev_close,
        n225_added_prev_close.close_change,
        (n225_added_prev_close.close_change / n225_added_prev_close.prev_close) * 100 as pct_change,
        n225_add_info.shares * n225_added_prev_close.close as mkt_cap
    from n225_added_prev_close 
    inner join n225_code as n225_code_only 
    on n225_added_prev_close.ticker = n225_code_only.ticker
    inner join n225_max as n225_yoy_vol
    on n225_added_prev_close.ticker = n225_yoy_vol.ticker
    inner join n225_info as n225_add_info 
    on n225_added_prev_close.ticker = n225_add_info.ticker
    where n225_added_prev_close.date = (select max(date) from n225_added_prev_close)
    order by n225_added_prev_close.ticker
)
select * from n225_summary
