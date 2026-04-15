import json
import threading
import time
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt

from utils.setupLogger import setup_logger

from os import getenv

class MQTTHelper:
    """Helper class that sends data to Mosquitto"""
    def __init__(self,uuid:str, host: str = None,port: int = None,keepalive: int = 60,client: Optional[mqtt.Client]=None):
        """
        :param uuid: client uuid
        :type uuid: str
        :param host:
        :type host: str
        :param port:
        :type port: int
        :param keepalive:
        :type keepalive: int
        """
        self.uuid=uuid
        self.host=host or "localhost"
        self.port=port or int(getenv("MOSQUITTO_LOCAL_CONTAINER_PORT"))
        self.keepalive=keepalive
        
        self._client = client or mqtt.Client(client_id=uuid) #dependency injection for unit testing purposes (does not affect normal use)
        self._lock=threading.Lock()
        self._connected= False
        self._topic_callbacks = {}
        
        
        self._client.on_message = self._on_message
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self.logger=setup_logger("MQTTHelper")
        self.connect()
        
    def _on_message(self, _client, _userdata, msg):
        """handles the correct callback for each message"""
        self.logger.debug(f"got message from topic {msg.topic}")
        try:
            payload = json.loads(msg.payload.decode())
            
            with self._lock:
                for topic, cb in self._topic_callbacks.items():
                    if mqtt.topic_matches_sub(topic, msg.topic): #wild card support
                        callback = cb
                        break
                    
            if callback:
                callback(payload)
            else:
                self.logger.info(f"No callback registered for topic: {msg.topic}")
                
        except json.JSONDecodeError:
            self.logger.error(f"Malformed JSON received on {msg.topic}")
        except Exception as e:
            self.logger.error(f"Error executing callback for {msg.topic}: {e}")
        
    def _on_connect(self,client,userdata,flags,rc):
        if rc==0:
            self._connected=True
            self.logger.info("Connected to MQTT Broker.")
        else:
            self.logger.error(f"Failed to connect to MQTT broker. RC={rc}")
            
    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        self.logger.warning("Disconnected from MQTT broker.")

    def connect(self):
        """Connect to the MQTT broker and start network loop."""
        self._client.connect(self.host, self.port, self.keepalive)
        self._client.loop_start()

        # Optional: wait briefly for connection
        timeout = 5
        start = time.time()
        while not self._connected and time.time() - start < timeout:
            time.sleep(0.1)

        if not self._connected:
            raise ConnectionError("Unable to connect to MQTT broker.")

    def disconnect(self):
        """Disconnect cleanly from the broker."""
        if self._connected:
            self._client.loop_stop()
            self._client.disconnect()

    def publish(self,topic: str,payload: Dict[str, Any],qos: int = 1,retain: bool = True, inject_uuid=True):
        """
        Inject UUID and sends the message
        """
        if not self._connected:
            raise RuntimeError("MQTT client is not connected.")

        if inject_uuid:
            injected_payload = {"uuid": self.uuid,"measurement":topic, **payload} #the uuid is injected here to avoid all N plugins all having to know what the uuid is (especially useful with external devices)
        else:
            injected_payload=payload #for commands, where we actually don't want uuid
        message = json.dumps(injected_payload)

        with self._lock:
            result = self._client.publish(
                topic,
                message,
                qos=qos,
                retain=retain,
            )

            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                self.logger.error(f"Failed to publish message to {topic}. RC={result.rc}")
                
    def subscribe(self,topic:str,callback):
        """
        subscribe to the given topic (creating a new thread), calling the callback function for every incoming message
        """
        with self._lock:
            self._topic_callbacks[topic] = callback
            
        result, mid = self._client.subscribe(topic)
        
        if result == mqtt.MQTT_ERR_SUCCESS:
            self.logger.info(f"Subscribed to {topic}")
        else:
            self.logger.error(f"Failed to subscribe to {topic}. RC={result}")
            
    def unsubscribe(self,topic:str):
        """
        unsubscribe to a topic
        """
        with self._lock:
            self._topic_callbacks.pop(topic,None)
            
        result, mid = self._client.unsubscribe(topic)
        
        if result == mqtt.MQTT_ERR_SUCCESS:
            self.logger.info(f"Unsubscribed to {topic}")
        else:
            self.logger.error(f"Failed to unsubscribe to {topic}. RC={result}")