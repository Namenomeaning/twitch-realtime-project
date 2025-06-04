# Twitch Real-time Data Engineering Pipeline

A comprehensive real-time data engineering project that analyzes streaming data from Twitch to discover insights about gaming trends, viewer patterns, and broadcaster metrics through interactive dashboards.

![Architecture](./images/architecture.png)

## 🎯 Project Overview

This project implements a modern data engineering pipeline that:
- **Collects** real-time streaming data from Twitch API
- **Processes** data through Apache Kafka for stream processing
- **Stores** processed data in ClickHouse for analytical queries
- **Visualizes** insights through interactive Grafana dashboards
- **Monitors** data pipeline health and performance

## 🏗️ Architecture

The pipeline follows a modern streaming architecture pattern:

1. **Data Ingestion**: Python producer fetches data from Twitch API
2. **Stream Processing**: Apache Kafka handles real-time data streams
3. **Data Storage**: ClickHouse serves as the analytical database
4. **Data Transformation**: ETL processes enrich and clean the data
5. **Visualization**: Grafana provides real-time dashboards
6. **Infrastructure**: Docker containers orchestrate the entire stack

### Components

- **🎮 Twitch API Producer**: Fetches top games and streaming data
- **📨 Apache Kafka**: Message broker for stream processing
- **🗄️ ClickHouse**: Columnar database for analytics
- **📊 Grafana**: Dashboard and visualization platform
- **🔄 ETL Pipeline**: Data transformation and enrichment
- **🌐 Nginx**: Reverse proxy and load balancer
- **💾 NATS**: Message queuing system

## 📈 Dashboard Insights

![Dashboard](./images/grafana.png)

The Grafana dashboard provides real-time insights into:
- **Top Games by Viewer Count**: Most popular games currently being streamed
- **Streaming Trends**: Viewer count patterns over time
- **Broadcaster Analytics**: Stream duration, language distribution, mature content ratio
- **Platform Metrics**: Data pipeline performance and health monitoring

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Twitch Developer Account (for API credentials)

### Environment Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd twitch-realtime-project
   ```

2. **Configure Twitch API credentials**:
   ```bash
   # Edit src/.env with your Twitch API credentials
   cp src/.env.example src/.env
   ```
   
   Update the following variables:
   ```
   APP_ID=your_twitch_app_id
   APP_SECRET=your_twitch_app_secret
   ```

3. **Start the infrastructure**:
   ```bash
   docker-compose up -d
   ```

4. **Install Python dependencies**:
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

### Running the Pipeline

1. **Start data ingestion**:
   ```bash
   cd src/producer
   python streams_producer.py
   ```

2. **Access the services**:
   - **Grafana Dashboard**: http://localhost:3000 (admin/admin)
   - **Kafka UI**: http://localhost:8088
   - **ClickHouse**: http://localhost:8123
   - **Glassflow UI**: http://localhost:8080

## 📊 Data Schema

### Streams Data
```sql
CREATE TABLE game_streams_enriched (
    stream_id String,
    user_id String,
    user_login Nullable(String),
    user_name Nullable(String),
    game_id String,
    game_name Nullable(String),
    stream_type Nullable(String),
    title Nullable(String),
    viewer_count Nullable(UInt32),
    started_at DateTime,
    language Nullable(String),
    is_mature Nullable(Bool),
    tags Nullable(String),
    broadcaster_type Nullable(String),
    user_description Nullable(String),
    user_created_at Nullable(DateTime),
    data_retrieved_at DateTime
) ENGINE = MergeTree
PARTITION BY (data_retrieved_at, game_id)
ORDER BY (stream_id, data_retrieved_at)
TTL toDateTime(started_at) + toIntervalDay(14)
```

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Data Ingestion** | Python, TwitchAPI | Real-time data collection |
| **Message Broker** | Apache Kafka | Stream processing |
| **Database** | ClickHouse | Analytical data storage |
| **Visualization** | Grafana | Dashboard and monitoring |
| **ETL** | GlassFlow | Data transformation |
| **Infrastructure** | Docker, Nginx | Container orchestration |
| **Schema Registry** | Confluent Schema Registry | Data schema management |

## 🔧 Configuration

### Kafka Topics
- `game_streams`: Raw streaming data
- `twitch_users`: User profile information

### ClickHouse Tables
- `game_streams_enriched`: Main analytical table with enriched stream data

### Grafana Dashboards
- **Twitch Realtime Dashboard**: Main analytics dashboard

## 📁 Project Structure

```
├── docker-compose.yml          # Infrastructure orchestration
├── pyproject.toml             # Python dependencies
├── src/
│   ├── producer/              # Data ingestion
│   │   ├── streams_producer.py
│   │   └── twitch_api.py
│   ├── database/              # Database schemas
│   │   └── game_streams_enriched.sql
│   └── dashboard/             # Grafana dashboards
│       └── twitch_realtime_dashboard.json
├── docker/                    # Docker configurations
│   ├── clickhouse/
│   ├── grafana/
│   └── nginx/
├── data/                      # Persistent data storage
└── images/                    # Documentation images
```

## 🔍 Monitoring and Observability

- **Pipeline Health**: Monitor data ingestion rates and processing latency
- **Data Quality**: Track data completeness and accuracy metrics
- **System Performance**: Monitor resource usage and response times
- **Business Metrics**: Track gaming trends and viewer engagement

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Twitch API](https://dev.twitch.tv/docs/api/) for providing streaming data
- [ClickHouse](https://clickhouse.com/) for fast analytical queries
- [Apache Kafka](https://kafka.apache.org/) for stream processing
- [Grafana](https://grafana.com/) for beautiful visualizations

## 📞 Support

For questions and support, please open an issue on GitHub or contact the maintainers.

---

**Built with ❤️ for the gaming and data engineering community**