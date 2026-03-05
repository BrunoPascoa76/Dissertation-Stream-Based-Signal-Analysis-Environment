from importlib.metadata import entry_points
import sys
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from pluggy import PluginManager

from utils.BasePlugin import BasePlugin
from utils.MQTTHelper import MQTTHelper
from plugins.core.MosquittoManager import MosquittoManager

class SensorsDesktopApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        # Set window properties
        self.setWindowTitle('Hello World App')
        self.setGeometry(100, 100, 300, 200)  # x, y, width, height
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create label with hello world text
        label = QLabel('Hello World!')
        label.setStyleSheet('font-size: 24px; font-weight: bold;')
        layout.addWidget(label)
        
        # Set the layout on the application's window
        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    #register plugin Manager
    app.pm=PluginManager("sensorsDesktop")
    app.pm.add_hookspecs(BasePlugin)
    
    app.mosquitto=MosquittoManager()
    app.mosquitto.start()
    
    #register sensor plugins
    publisher=MQTTHelper()  
    sensors = entry_points(group='plugins.sensors')
    
    for entry_point in sensors:
        plugin_class = entry_point.load()
        plugin_instance = plugin_class(publisher)
        app.pm.register(plugin_instance)
    
    
    # Create and show the application's window
    ex = SensorsDesktopApp()
    ex.show()
    
    app.aboutToQuit.connect(app.mosquitto.stop)
    sys.exit(app.exec())