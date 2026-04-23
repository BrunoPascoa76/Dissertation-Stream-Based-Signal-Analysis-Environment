from importlib.metadata import entry_points
import sys
import uuid
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import QSettings
from pluggy import PluginManager

from utils.BasePlugin import BasePlugin
from utils.MQTTHelper import MQTTHelper
from plugins.core.MosquittoManager import MosquittoManager
from widgets.SensorControlScreen import SensorControlScreen

from dotenv import load_dotenv

if __name__ == '__main__':
    app = QApplication(sys.argv)
    load_dotenv() #load configurations into app
    
    #add mosquitto docker manager
    app.mosquitto=MosquittoManager()
    app.mosquitto.start()
    
    app.settings=QSettings("Dissertation", "SensorsDesktop")
    
    if not app.settings.contains("uuid"):
        app.settings.setValue("uuid",str(uuid.uuid4()))
        
    
    # Create and show the application's window
    ex = SensorControlScreen()
    ex.setWindowTitle("Sensor data gathering")
    ex.show()
    
    app.aboutToQuit.connect(app.mosquitto.stop)
    sys.exit(app.exec())