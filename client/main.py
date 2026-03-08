from importlib.metadata import entry_points
import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from pluggy import PluginManager

from utils.BasePlugin import BasePlugin
from utils.MQTTHelper import MQTTHelper
from plugins.core.MosquittoManager import MosquittoManager
from widgets.SensorControlScreen import SensorControlScreen


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    #add mosquitto docker manager
    app.mosquitto=MosquittoManager()
    app.mosquitto.start()
    
    
    
    
    # Create and show the application's window
    ex = SensorControlScreen()
    ex.show()
    
    app.aboutToQuit.connect(app.mosquitto.stop)
    sys.exit(app.exec())