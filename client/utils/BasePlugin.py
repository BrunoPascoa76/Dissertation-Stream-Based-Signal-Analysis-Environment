from abc import ABC, abstractmethod
from pluggy import HookimplMarker, HookspecMarker
import pluggy

from utils.MQTTHelper import MQTTHelper
from utils.setupLogger import setup_logger

# Plugin hook specification for automatic discovery
hookspec = HookspecMarker("sensorsDesktop")
hookimpl=HookimplMarker("sensorsDesktop")


class BasePlugin(ABC):
    """All plugins should inherit from this class."""
    
    def __init__(self, publisher:MQTTHelper, plugin_name:str):
        self._running=False
        self._publisher=publisher
        self.logger=setup_logger(plugin_name)
        
    
    @abstractmethod
    @HookspecMarker("sensorsDesktop")
    def start(self):
        """Start the plugin/service."""
        pass

    @abstractmethod
    @HookspecMarker("sensorsDesktop")
    def stop(self):
        """Stop the plugin/service."""
        pass

    @HookspecMarker("sensorsDesktop")
    @HookimplMarker("sensorsDesktop")
    def status(self):
        if self._running:
            return "running"
        else:
            return "stopped"
