select
    u.user_id,
    u.signup_date,
    u.acquisition_channel,
    u.country,
    u.is_active,
    count(s.session_id) as total_sessions,
    min(s.session_started_at) as first_session_at,
    max(s.session_started_at) as most_recent_session_at,
    count(distinct s.device_type) as device_type_count,
    count(distinct s.traffic_source) as traffic_source_count
from {{ ref('stg_users') }} as u
left join {{ ref('stg_sessions') }} as s
    on u.user_id = s.user_id
group by 1, 2, 3, 4, 5

