from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """All plugins should inherit from this class."""
    
    @abstractmethod
    def start(self):
        """Start the plugin/service."""
        pass

    @abstractmethod
    def stop(self):
        """Stop the plugin/service."""
        pass

    @abstractmethod
    def status(self) -> str:
        """Return status string, e.g., 'running' or 'stopped'."""
        pass