from pluggy import HookimplMarker

from utils.BasePlugin import BasePlugin
from utils.MQTTHelper import MQTTHelper

class HRVReader(BasePlugin):
    def __init__(self,publisher:MQTTHelper):
        super().__init__(publisher,"HRV Reader")
    
    @HookimplMarker("sensorsDesktop")
    def start(self):
        if self._running:
            return
        
        payload={
            "command":"start"
        }
        
        self._publisher.publish("commands/hrv",payload,inject_uuid=True) #this way the watch receives the uuid as well
        self._running=True
    
    @HookimplMarker("sensorsDesktop")
    def stop(self):
        if not self._running:
            return
        
        payload={
            "command":"stop"
        }
        
        self._publisher.publish("commands/hrv",payload,inject_uuid=False)
        self.running=False