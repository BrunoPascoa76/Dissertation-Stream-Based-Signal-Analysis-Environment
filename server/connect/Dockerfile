FROM confluentinc/cp-kafka-connect:latest

USER root

#install mqtt plugin
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-mqtt:latest

#install influxdb plugin
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-influxdb:latest

USER appuser