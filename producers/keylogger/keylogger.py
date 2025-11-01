import logging
from pynput import keyboard
from kafka import KafkaProducer
import json,time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("producer")

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],  
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
TOPIC = 'keyboard-events'
BUCKET= "sensors"

def on_press(key):
    t=time.time_ns()
    
    if key in (keyboard.Key.backspace,keyboard.Key.delete):
        event_type="DELETE"
    elif key in (keyboard.Key.enter,keyboard.Key.space):
        event_type="WHITESPACE"
    elif hasattr(key,'char') and key.char is not None:
        event_type="ALPHANUMERIC"
    else:
        return
    
    event={
        "timestamp_ns": t,
        "event_type": event_type
    }
    
    future=producer.send(TOPIC,event)

    try:
        record_metadata = future.get(timeout=10)  # blocks until ack from broker
        logger.info(f"Message sent to topic {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}")
    except Exception as e:
        logger.exception(f"Failed to send message: {e}")

with keyboard.Listener(on_press=on_press) as listener:
    try:
        listener.join()
    except KeyboardInterrupt as e:
        logger.info("shutting down...")
