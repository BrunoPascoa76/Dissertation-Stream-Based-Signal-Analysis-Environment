import json
import threading
import time
from typing import Any, Dict, Optional

import paho.mqtt.client as mqtt

from utils.setupLogger import setup_logger

class MQTTHelper:
    """Helper class that sends data to Mosquitto"""
    def __init__(self,host: str = "localhost",port: int = 1883,client_id: Optional[str] = None,keepalive: int = 60,client: Optional[mqtt.Client]=None):
        """
        :param host:
        :type host: str
        :param port:
        :type port: int
        :param client_id:
        :type client_id: Optional[str]
        :param keepalive:
        :type keepalive: int
        """
        self.host=host
        self.port=port
        self.keepalive=keepalive
        
        self._client = client or mqtt.Client(client_id=client_id) #dependency injection for unit testing purposes (does not affect normal use)
        self._lock=threading.Lock()
        self._connected= False
        
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self.logger=setup_logger("MQTTHelper")
        
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

    def publish(self,topic: str,payload: Dict[str, Any],qos: int = 0,retain: bool = False):
        """
        Publish a JSON payload to a topic.
        """
        if not self._connected:
            raise RuntimeError("MQTT client is not connected.")

        message = json.dumps(payload)

        with self._lock:
            result = self._client.publish(
                topic,
                message,
                qos=qos,
                retain=retain,
            )

            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                self.logger.error(f"Failed to publish message to {topic}. RC={result.rc}")