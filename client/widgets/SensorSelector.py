from importlib.metadata import entry_points

from PyQt6.QtWidgets import QApplication, QCheckBox, QVBoxLayout, QWidget

from PyQt6.QtGui import QFont
from pluggy import PluginManager

from utils.setupLogger import setup_logger
from utils.BasePlugin import BasePlugin
from utils.MQTTHelper import MQTTHelper

class SensorSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.logger=setup_logger("SensorSelector")
        self.app=QApplication.instance()
        
        self.uuid=self.app.settings.value("uuid",type=str) or "Unknown"
        
        self.disabled_sensors = self.app.settings.value("disabled_sensors", type=list) or []
        self._load_available_sensors()
        
        self.initUI()
    
    def _load_available_sensors(self):
        """register sensor sensor"""
        self.app.pm=PluginManager("sensorsDesktop")
        self.app.pm.add_hookspecs(BasePlugin)
        
        publisher=MQTTHelper(self.uuid)  
        _entry_points = entry_points(group='plugins.sensors')
        self.available_sensors=dict()
        self.logger.debug(f"loaded entry_points: {(e.name for e in _entry_points)}")
    
        for sensor in _entry_points:
            sensor_name=sensor.name
            sensor_class=sensor.load()
            sensor_instance=sensor_class(publisher)
            self.available_sensors[sensor_name]=sensor_instance
            
            if sensor_name not in self.disabled_sensors:
                self.app.pm.register(sensor_instance)
                self.logger.debug(f"registered sensor: {sensor_name}")
            
            
    def _toggle_sensor(self, sensor_name):
        """Toggle a single sensor's state"""
        try:
            sensor=self.available_sensors[sensor_name]
            
            if sensor_name in self.disabled_sensors:
                self.disabled_sensors.remove(sensor_name)
                self.app.pm.register(sensor)
                self.logger.info(f"enabled sensor: {sensor_name}")
            else:
                self.disabled_sensors.append(sensor_name)
                self.app.pm.unregister(sensor)
                self.logger.info(f"disabled sensor: {sensor_name}")
        except KeyError:
            self.logger.error(f"Sensor not found: {sensor_name}")
            
        
        self.app.settings.setValue("disabled_sensors", self.disabled_sensors)
        
    def initUI(self):
        layout = QVBoxLayout()
    
        for sensor_name in self.available_sensors:
            cb = QCheckBox(sensor_name)
            cb.setChecked(sensor_name not in self.disabled_sensors)
            cb.stateChanged.connect(lambda state, name=sensor_name: self._toggle_sensor(name))
            layout.addWidget(cb)

        self.setLayout(layout)
    