{{
    config(
        materialized='view'
    )
}}

with 

source as (

    select * from {{ source('staging', 'ext_n225_comp') }}

),

casted as (

    select
        cast(date as date) as date,
        open,
        high,
        low,
        close,
        adj_close,
        volume,
        cast(ticker as integer) as ticker

    from source

)

select * from casted
