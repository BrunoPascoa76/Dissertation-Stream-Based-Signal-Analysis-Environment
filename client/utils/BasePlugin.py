from abc import ABC, abstractmethod

from utils.MQTTHelper import MQTTHelper
from utils.setupLogger import setup_logger

class BasePlugin(ABC):
    """All plugins should inherit from this class."""
    
    def __init__(self, publisher:MQTTHelper, plugin_name:str):
        self.running=False
        self._publisher=publisher
        self.logger=setup_logger(plugin_name)
        

    
    @abstractmethod
    def start(self):
        """Start the plugin/service."""
        pass

    @abstractmethod
    def stop(self):
        """Stop the plugin/service."""
        pass

    def status(self):
        if self.running:
            return "running"
        else:
            return "stopped"