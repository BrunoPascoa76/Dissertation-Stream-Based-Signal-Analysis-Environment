from pynput import keyboard
from kafka import KafkaProducer
import json,time

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],  # change to your broker
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
topic = 'keyboard-events'

def on_press(key):
    t=time.time_ns()
    
    if key in (keyboard.Key.backspace,keyboard.Key.delete):
        event_type="delete"
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

    try:
        record_metadata = future.get(timeout=10)  # blocks until ack from broker
        print(f"Message sent to topic {record_metadata.topic}, partition {record_metadata.partition}, offset {record_metadata.offset}")
    except Exception as e:
        print(f"Failed to send message: {e}")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
