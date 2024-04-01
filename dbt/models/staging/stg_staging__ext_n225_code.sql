{{
    config(
        materialized='view'
    )
}}

with 

source as (

    select * from {{ source('staging', 'ext_n225_code') }}

),

casted as (

    select
        cast(code as integer) as ticker,
        company

    from source

)

select * from casted
