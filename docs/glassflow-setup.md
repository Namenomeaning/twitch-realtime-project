# GlassFlow Pipeline Setup Guide

This guide walks you through setting up the ETL pipeline using GlassFlow to join Kafka topics and write enriched data to ClickHouse.

## Overview

The pipeline will:
1. Read from two Kafka topics: `game_streams` and `twitch_users`
2. Join the data on `user_id` field
3. Write the enriched result to ClickHouse table `game_streams_enriched`

## Prerequisites

- Docker environment is running
- Kafka topics `game_streams` and `twitch_users` are created and receiving data
- ClickHouse table `game_streams_enriched` exists

## Step-by-Step Setup

### 1. Access GlassFlow UI

Navigate to http://localhost:8080 in your browser.

### 2. Create Data Sources

#### Source 1: Game Streams
- **Name**: `game_streams_source`
- **Type**: Kafka
- **Configuration**:
  ```yaml
  bootstrap_servers: kafka1:19092
  topic: game_streams
  group_id: glassflow_game_streams
  auto_offset_reset: earliest
  ```

#### Source 2: Twitch Users
- **Name**: `twitch_users_source` 
- **Type**: Kafka
- **Configuration**:
  ```yaml
  bootstrap_servers: kafka1:19092
  topic: twitch_users
  group_id: glassflow_twitch_users
  auto_offset_reset: earliest
  ```

### 3. Configure Transformation

Create a join transformation:
- **Type**: Left Join
- **Left Source**: `game_streams_source`
- **Right Source**: `twitch_users_source`
- **Join Key**: `user_id`
- **Join Type**: LEFT JOIN

#### Transformation Logic
```sql
SELECT 
    gs.stream_id,
    gs.user_id,
    tu.user_login,
    tu.user_name,
    gs.game_id,
    gs.game_name,
    gs.stream_type,
    gs.title,
    gs.viewer_count,
    gs.started_at,
    gs.language,
    gs.is_mature,
    gs.tags,
    tu.broadcaster_type,
    tu.user_description,
    tu.user_created_at,
    gs.data_retrieved_at
FROM game_streams_source gs
LEFT JOIN twitch_users_source tu ON gs.user_id = tu.user_id
```

### 4. Configure Destination

#### ClickHouse Destination
- **Type**: ClickHouse
- **Configuration**:
  ```yaml
  host: clickhouse
  port: 9000
  database: default
  table: game_streams_enriched
  username: default
  password: ""
  ```

### 5. Pipeline Configuration Example

Complete pipeline configuration:

```yaml
version: "1.0"

sources:
  game_streams_source:
    type: kafka
    config:
      bootstrap_servers: "kafka1:19092"
      topic: "game_streams"
      group_id: "glassflow_game_streams"
      auto_offset_reset: "earliest"
      
  twitch_users_source:
    type: kafka
    config:
      bootstrap_servers: "kafka1:19092"
      topic: "twitch_users"
      group_id: "glassflow_twitch_users"
      auto_offset_reset: "earliest"

transformations:
  - name: enrich_streams
    type: join
    config:
      left: game_streams_source
      right: twitch_users_source
      join_key: user_id
      join_type: left
      select:
        - "gs.stream_id"
        - "gs.user_id"
        - "tu.user_login"
        - "tu.user_name"
        - "gs.game_id"
        - "gs.game_name"
        - "gs.stream_type"
        - "gs.title"
        - "gs.viewer_count"
        - "gs.started_at"
        - "gs.language"
        - "gs.is_mature"
        - "gs.tags"
        - "tu.broadcaster_type"
        - "tu.user_description"
        - "tu.user_created_at"
        - "gs.data_retrieved_at"

destinations:
  clickhouse_sink:
    type: clickhouse
    config:
      host: "clickhouse"
      port: 9000
      database: "default"
      table: "game_streams_enriched"
      username: "default"
      password: ""
      batch_size: 1000
      flush_interval: 30s
```

## Testing the Pipeline

### 1. Verify Data Sources
Check that both Kafka topics are receiving data:
```bash
# Check game_streams topic
docker exec -it kafka1 kafka-console-consumer --bootstrap-server localhost:19092 --topic game_streams --max-messages 1

# Check twitch_users topic  
docker exec -it kafka1 kafka-console-consumer --bootstrap-server localhost:19092 --topic twitch_users --max-messages 1
```

### 2. Monitor Pipeline Status
- Check GlassFlow UI for pipeline status
- Monitor processing metrics and error logs
- Verify data is flowing through transformations

### 3. Validate Output Data
Query ClickHouse to verify enriched data:
```sql
-- Check record count
SELECT COUNT(*) FROM default.game_streams_enriched;

-- Verify join worked correctly
SELECT 
    stream_id,
    user_login,
    user_name,
    game_name,
    viewer_count
FROM default.game_streams_enriched 
WHERE user_login IS NOT NULL
LIMIT 10;

-- Check data freshness
SELECT 
    MAX(data_retrieved_at) as latest_data,
    COUNT(*) as total_records
FROM default.game_streams_enriched;
```

## Troubleshooting

### Common Issues

1. **Pipeline not starting**
   - Check Kafka connectivity
   - Verify topic names and bootstrap servers
   - Ensure ClickHouse table exists

2. **No data in destination**
   - Check source data availability
   - Verify join keys match between sources
   - Check transformation logic

3. **Join not working**
   - Ensure `user_id` field exists in both topics
   - Check data types match
   - Verify join key formatting

4. **ClickHouse write errors**
   - Verify table schema matches transformation output
   - Check ClickHouse connectivity and credentials
   - Monitor ClickHouse logs

### Useful Commands

```bash
# Check GlassFlow container logs
docker-compose logs -f app

# Restart GlassFlow service
docker-compose restart app

# Check Kafka topics
docker exec -it kafka1 kafka-topics --bootstrap-server localhost:19092 --list

# Access ClickHouse client
docker exec -it clickhouse clickhouse-client
```

## Performance Tuning

- **Batch Size**: Increase for higher throughput
- **Flush Interval**: Adjust based on latency requirements  
- **Parallelism**: Configure consumer groups for scaling
- **Memory**: Monitor and adjust container memory limits

## Additional Resources

- [GlassFlow Documentation](https://github.com/glassflow/clickhouse-etl)
- [ClickHouse Documentation](https://clickhouse.com/docs)
- [Kafka Documentation](https://kafka.apache.org/documentation/)
