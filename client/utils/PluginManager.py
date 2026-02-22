import importlib
import pathlib
from typing import Type

from utils.BasePlugin import BasePlugin
from utils.setupLogger import setup_logger


class PluginManager:
    """Generic plugin loader that manages all plugins"""
    
    def __init__(self, CORE_FOLDER:str="./plugins/core",SENSORS_FOLDER:str="./plugins/sensors"):
        """
        :param CORE_FOLDER: location of the folder with the core plugins (core plugins run at application start)
        :type CORE_FOLDER: str
        :param SENSORS_FOLDER: location of the folder with the sensor plugins (sensor plugins only run when gathering data)
        :type SENSORS_FOLDER: str
        """
        
        self.CORE_FOLDER=pathlib.Path(CORE_FOLDER)
        self.SENSORS_FOLDER=pathlib.Path(SENSORS_FOLDER)
        
        self.core_plugins = self._load_plugins_from_folder(self.CORE_FOLDER)
        self.sensor_plugins = self._load_plugins_from_folder(self.SENSORS_FOLDER)
        
        self.logger=setup_logger("PluginManager")
        
    def _load_plugins_from_folder(self, folder:pathlib.Path) -> list[BasePlugin]:
        """
        loads all plugins from the given folder. Ignores any classes not implementing BasePlugin
        
        :param folder: the path to the folder
        :type folder: pathlib.Path
        :return: a list of plugins
        :rtype: list[BasePlugin]
        """
        plugins = {}
        for file in folder.glob("*.py"): #get all files
            if file.name.startswith("_"): #(except private ones like __init__.py)
                continue
                
            spec = importlib.util.spec_from_file_location(file.stem, file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            #execute said files
            
            #see which ones implement BasePlugin
            plugin_class: Type[BasePlugin] = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                    plugin_class = attr
                    break
                
            #instanciate those who pass
            if plugin_class:
                instance = plugin_class()
                plugins[type(instance).__name__] = instance 
        return plugins
    
    def list_core_plugins(self) -> list[str]:
        """
        Lists all core plugins
        
        :return: a list of core plugin names
        :rtype: list[str]
        """
        return list(self.core_plugins.keys())

    def list_sensor_plugins(self) -> list[str]:
        """
        Lists all sensor plugins
        
        :return: a list of sensor plugin names
        :rtype: list[str]
        """
        return list(self.sensor_plugins.keys())
    
    def start_all_core_plugins(self):
        """
        Start all core plugins
        """
        for plugin in self.core_plugins.values():
            plugin.start()

    def start_all_sensor_plugins(self):
        """
        Start all sensor plugins
        """
        for plugin in self.sensor_plugins.values():
            plugin.start()

    # ---------- Stop ----------
    def stop_all_core_plugins(self):
        """
        Stop all core plugins
        """
        for plugin in self.core_plugins.values():
            plugin.stop()

    def stop_all_sensor_plugins(self):
        """
        Stop all sensor plugins
        """
        for plugin in self.sensor_plugins.values():
            plugin.stop()
            
    def start_sensor_plugins(self,plugin_names:list[str]):
        """
        Start all plugins in the given list of names
        :param plugin_names: the names of all plugins to be started
        :type plugin_names: list[str]
        """
        for name in plugin_names:
            self.start_sensor_plugin(name)
                
    def start_sensor_plugin(self,name:str):
        """
        Start plugin with the given name
        :param name: the name of the plugin
        :type name: str
        """
        if name in self.sensor_plugins:
            self.sensor_plugins[name].start()
            
