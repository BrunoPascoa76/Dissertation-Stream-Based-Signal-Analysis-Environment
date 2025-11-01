import json
import logging
import os
from time import time_ns
from influxdb_client import InfluxDBClient, Point, WriteApi
from kafka import KafkaConsumer

TOPIC="keyboard-events"
ORGANIZATION="dissertation"
BUCKET="sensors"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("consumer_wpm")

def connect_db():
    client=InfluxDBClient(
        url="http://influxdb:8086",
        token=os.environ["INFLUXDB_ADMIN_TOKEN"],
        org="dissertation"
    )
    write_api=client.write_api()
    return client,write_api

def process_event(event,write_api:WriteApi):
    key_class=event.get("event_type")
    timestamp_ns=event.get("timestamp_ns")
    
    if key_class=="WHITESPACE":
        point=Point("word").tag("sensor","keyboard").field("value",1).time(timestamp_ns,write_precision="ns") #create a new point (value is just because it's needed in the queries)
        logger.info(f"sent word at {timestamp_ns}")
        write_api.write(bucket=BUCKET,record=point) #record it
    elif key_class=="DELETE":
        point=Point("delete").tag("sensor","keyboard").field("value",1).time(timestamp_ns,write_precision="ns")
        logger.info(f"sent delete at {timestamp_ns}")
        write_api.write(bucket=BUCKET,record=point)

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