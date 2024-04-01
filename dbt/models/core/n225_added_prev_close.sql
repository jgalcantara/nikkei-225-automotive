{{
    config(
        materialized='table'
    )
}}

with 
n225_comp as (
    select *
    from {{ ref('stg_staging__ext_n225_comp') }}
),
added_prev_close as (
    select *,
    lag(close, 1) over (partition by ticker order by date asc) as prev_close,
    close - lag(close, 1) over (partition by ticker order by date asc) as close_change,
    avg(volume) over (partition by ticker order by date rows between 29 preceding and current row ) as avg_vol_30d,
    
    from n225_comp

)
select * from added_prev_close