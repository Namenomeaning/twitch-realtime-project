# Grafana Custom Dockerfile
FROM grafana/grafana:latest

# Install ClickHouse plugin
RUN grafana-cli plugins install grafana-clickhouse-datasource

# Copy provisioning configurations
COPY provisioning /etc/grafana/provisioning/

# Set proper ownership
USER root
RUN chown -R grafana:root /etc/grafana/provisioning/
USER grafana

# Expose port
EXPOSE 3000

# Use the default entrypoint from base image
