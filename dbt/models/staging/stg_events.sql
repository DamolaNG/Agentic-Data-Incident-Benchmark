select
    cast(event_id as integer) as event_id,
    cast(session_id as integer) as session_id,
    cast(user_id as integer) as user_id,
    cast(event_timestamp as timestamp) as event_timestamp,
    cast(event_name as varchar) as event_name,
    cast(page_url as varchar) as page_url
from {{ source('raw', 'raw_events') }}

