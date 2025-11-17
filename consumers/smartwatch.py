import json
import logging
import os
from time import time_ns
from influxdb_client import InfluxDBClient, Point, WriteApi
from kafka import KafkaConsumer

TOPIC="smartwatch_data"
ORGANIZATION="dissertation"
BUCKET="sensors"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("consumer_smartwatch")

def connect_db():
    client=InfluxDBClient(
        url="http://influxdb:8086",
        token=os.environ["INFLUXDB_ADMIN_TOKEN"],
        org="dissertation"
    )
    write_api=client.write_api()
    return client,write_api

def process_event(event,write_api:WriteApi):
    reading_type=event.get("reading_type")
    value=event.get("value")
    timestamp_ns=event.get("timestamp_ns")
    
    point=Point(reading_type).tag("sensor","smartwatch").field("value",value).time(timestamp_ns,write_precision="ns") #create a new point (value is just because it's needed in the queries)
    logger.info(f"sent {reading_type} with value {value} at {timestamp_ns}")
    write_api.write(bucket=BUCKET,record=point) #record it

if __name__=="__main__":
    consumer=KafkaConsumer(
        TOPIC,
        bootstrap_servers=['kafka:29092'],  
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True
    )
    
    influx_client,write_api=connect_db()
    
    try:
        for message in consumer: #for each message...
            event=message.value #get the event
            logger.info(f"got new message: {event}")
            process_event(event,write_api) #and process it into the database
    except KeyboardInterrupt:
        print("Shutting down...")
    finally: #close everything nicely
        influx_client.close()
        consumer.close()