select
    cast(session_id as integer) as session_id,
    cast(user_id as integer) as user_id,
    cast(session_started_at as timestamp) as session_started_at,
    cast(session_started_at as date) as session_date,
    cast(device_type as varchar) as device_type,
    cast(traffic_source as varchar) as traffic_source
from {{ source('raw', 'raw_sessions') }}

