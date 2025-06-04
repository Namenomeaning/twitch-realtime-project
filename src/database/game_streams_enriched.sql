CREATE TABLE default.game_streams_enriched (
    `stream_id` String,
    `user_id` String,
    `user_login` Nullable (String),
    `user_name` Nullable (String),
    `game_id` String,
    `game_name` Nullable (String),
    `stream_type` Nullable (String),
    `title` Nullable (String),
    `viewer_count` Nullable (UInt32),
    `started_at` DateTime,
    `language` Nullable (String),
    `is_mature` Nullable (Bool),
    `tags` Nullable (String),
    `broadcaster_type` Nullable (String),
    `user_description` Nullable (String),
    `user_created_at` Nullable (DateTime),
    `data_retrieved_at` DateTime
) ENGINE = MergeTree
PARTITION BY (data_retrieved_at, game_id)
ORDER BY (stream_id, data_retrieved_at) TTL toDateTime (started_at) + toIntervalDay (14) SETTINGS index_granularity = 8192