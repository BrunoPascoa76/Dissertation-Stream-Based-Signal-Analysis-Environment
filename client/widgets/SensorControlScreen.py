from importlib.metadata import entry_points
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from pluggy import PluginManager

from utils.crockford_encode import address_encode
from utils.setupLogger import setup_logger
from widgets.SensorSelector import SensorSelector

class SensorControlScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app = QApplication.instance()
        self.sensor_selector = SensorSelector()
        self.logger=setup_logger("SensorControlScreen")
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout()
        
        """pairing code"""
        pairing_label = QLabel(f"Pairing Code: {address_encode(self.app.mosquitto.port)}")
        pairing_label.setStyleSheet("""QLabel {
            font-size: 14px;
            font-weight: bold;
        }""")
        
        layout.addWidget(pairing_label)
        info_label = QLabel(
            "Use the following code to pair with external sensors"
        )
        info_label.setStyleSheet(
            """QLabel {
                font-size: 10pt;
                font-weight: normal;
                color: #555555;
            }"""
        )
        layout.addWidget(info_label)
        
        
        layout.addWidget(self.sensor_selector)
        
        # Part 3: Start/Stop Button
        self.button = QPushButton("Start")
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
        """)
        
        self.button.clicked.connect(self.toggle_action)
        layout.addWidget(self.button)
        
        self.setLayout(layout)
    
    def toggle_action(self):
        """Toggle between start and stop states"""
        if self.button.text() == "Start":
            # Start the plugin hooks
            self.app.pm.hook.start()
            self.button.setText("Stop")
        else:
            # Stop the plugin hooks
            self.app.pm.hook.stop()
            self.button.setText("Start")
