select
    cast(transaction_id as integer) as transaction_id,
    cast(session_id as integer) as session_id,
    cast(user_id as integer) as user_id,
    cast(transaction_timestamp as timestamp) as transaction_timestamp,
    cast(transaction_timestamp as date) as transaction_date,
    cast(amount as double) as amount,
    cast(currency as varchar) as currency,
    cast(payment_method as varchar) as payment_method,
    cast(transaction_status as varchar) as transaction_status
from {{ source('raw', 'raw_transactions') }}

