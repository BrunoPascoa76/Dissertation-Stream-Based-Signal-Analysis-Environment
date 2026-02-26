#!/bin/sh
# Install MQTT connector if missing
if [ ! -d /usr/share/java/kafka-connect-mqtt ]; then
  confluent-hub install --no-prompt confluentinc/kafka-connect-mqtt:latest
fi

# Start Kafka Connect
/etc/confluent/docker/run