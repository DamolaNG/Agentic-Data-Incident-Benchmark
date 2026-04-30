with source as (
    select * from {{ source('raw', 'orders') }}
),

renamed as (
    select
        cast(order_id as integer) as order_id,
        cast(customer_id as integer) as customer_id,
        cast(order_timestamp as timestamp) as order_timestamp,
        cast(order_status as varchar) as order_status,
        cast(order_total as double) as order_total
    from source
)

select * from renamed

