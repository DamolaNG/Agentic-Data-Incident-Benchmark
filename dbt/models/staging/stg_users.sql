select
    cast(user_id as integer) as user_id,
    cast(signup_date as date) as signup_date,
    cast(acquisition_channel as varchar) as acquisition_channel,
    cast(country as varchar) as country,
    cast(is_active as boolean) as is_active
from {{ source('raw', 'raw_users') }}

