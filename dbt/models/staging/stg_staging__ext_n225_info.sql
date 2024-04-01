{{
    config(
        materialized='view'
    )
}}

with 

source as (

    select * from {{ source('staging', 'ext_n225_info') }}

),

renamed as (

    select
        cast(ticker as integer) as ticker,
        shares

    from source

)

select * from renamed
