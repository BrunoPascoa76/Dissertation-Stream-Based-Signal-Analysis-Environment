from utils.BasePlugin import BasePlugin
from utils.MQTTHelper import MQTTHelper


class HRVReader(BasePlugin):
    def __init__(self):
        self.mqtt=MQTTHelper()
        self.running=False
    
    def start(self):
        if self.running:
            return
        
        
        self.mqtt.connect()
        self.mqtt.publish("commands/hrv","start")
        self.running=True
    
    def stop(self):
        if not self.running:
            return
        
        self.mqtt.publish("commands/hrv","stop")
        self.mqtt.disconnect()
        self.running=False
    
    def status(self):
        if self.running:
            return "running"
        else:
            return "stopped"