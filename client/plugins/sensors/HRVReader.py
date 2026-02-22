from utils.BasePlugin import BasePlugin
from utils.MQTTHelper import MQTTHelper


class HRVReader(BasePlugin):
    def __init__(self,publisher:MQTTHelper):
        super().__init__(publisher,"HRV Reader")
    
    def start(self):
        if self.running:
            return
        
        
        self._publisher.publish("commands/hrv","start")
        self.running=True
    
    def stop(self):
        if not self.running:
            return
        
        self._publisher.publish("commands/hrv","stop")
        self.running=False