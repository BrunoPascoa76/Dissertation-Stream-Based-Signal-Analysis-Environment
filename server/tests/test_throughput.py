import time
import os
import threading
from influxdb import InfluxDBClient
import json
import paho.mqtt.client as mqtt

TOPIC = 'sensors/test'
MQTT_HOST="mosquitto-central"
MQTT_PORT=int(os.getenv("MQTT_PORT",1883))
INFLUX_HOST = 'influxdb'
INFLUX_PORT = int(os.getenv("INFLUXDB_PORT",8086))
DB_NAME = os.getenv("INFLUXDB_DB","mqtt")
TEST_TIME=10
THROUGHPUT_RATE=10 #messages/second

def sender():
    client = mqtt.Client()
    client.connect(MQTT_HOST, MQTT_PORT, 60)
    
    client.loop_start()
    
    print(f"[*] Sending 10 messages...")
    for i in range(THROUGHPUT_RATE*TEST_TIME):
        data = {
            "uuid": "abcdef",
            "measurement":TOPIC,
            "timestamp": int(time.time() * 1000),
            "value": i
        }
        client.publish(TOPIC, json.dumps(data))
        time.sleep(1/THROUGHPUT_RATE)
    client.loop_stop()
    client.disconnect()
    print("Sending complete")

def monitor():
    client = InfluxDBClient(host=INFLUX_HOST,port=INFLUX_PORT, database=DB_NAME)
    
    last_value=0
    failed_checks=0
    for i in range(TEST_TIME):
        try:
            # Query InfluxQL (versão 1.8) - contamos o valor em qualquer measurement
            # onde o uuid seja o do nosso teste.
            query = f'SELECT count(value) FROM "{TOPIC}" WHERE "uuid"=\'abcdef\''
            result = client.query(query)
            
            points = list(result.get_points())
            total = points[0]['count'] if points else 0
            count=total-last_value
            last_value=total
            
            if i==0: #first reading
                print(f"T+{i}s: Messages found: {total}.")
            else:
                print(f"T+{i}s: Messages found: {total}. Mensagens since last check: {count}")
                if count<THROUGHPUT_RATE:
                    failed_checks=failed_checks+1
                    
                
        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(1) #1 check per second
    print("Monitoring Complete")#
    print(f"Failed checks: {failed_checks}")
    

def test_throughput():
    t1 = threading.Thread(target=sender)
    t2 = threading.Thread(target=monitor)

    t1.start()
    t2.start()

    t1.join()
    t2.join()