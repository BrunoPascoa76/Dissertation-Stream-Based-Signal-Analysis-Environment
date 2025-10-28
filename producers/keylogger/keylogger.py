from pynput import keyboard
from kafka import KafkaProducer
import json,time

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # change to your broker
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
topic = 'keyboard-events'

def on_press(key):
    t=time.time_ns()
    
    if key in (keyboard.Key.backspace,keyboard.Key.delete):
        event_type="delete"
    elif key in (keyboard.Key.delete,keyboard.Key.return,keyboard.Key.space):
        event_type="WHITESPACE"
    elif hasattr(key,'char') and key.char is not None:
        event_type="ALPHANUMERIC"
    else:
        return
    
    event={
        "timestamp_ns": t,
        "event_type": event_type
    }
    
    print(event)
    
    producer.send(topic,event)
    

