from pluggy import HookimplMarker
import pyqtgraph as pg
import requests
from PyQt6.QtCore import QSettings, QTimer, pyqtSlot
from abc import abstractmethod
from utils.BasePlugin import BasePlugin
from utils.setupLogger import setup_logger
from os import getenv

class BaseVisualizer(BasePlugin): 
    def __init__(self, sensor_name, title=None, x_label=None, y_label=None, update_ms=2000, background_color="w", line_color="r"):
        super().__init__(None,"") # Initialize BasePlugin logic (ID, settings, etc.)
        self.sensor_name = sensor_name
        self.is_active = False        
        
        self.widget = pg.PlotWidget()
        self.widget.setBackground(background_color)
        self.curve = self.widget.plot(pen=line_color)
        
        self.timer = QTimer()
        self.timer.setInterval(update_ms)
        self.timer.timeout.connect(self._update_loop)
        
        settings=QSettings("Dissertation", "SensorsDesktop")
        self.uuid=settings.value("uuid", defaultValue=None)
        print(self.uuid)
        
        if title:
            self.widget.setTitle(title)
        if y_label:
            self.widget.setLabel('left', title)
        if x_label:    
            self.widget.setLabel('bottom', 'Seconds Ago')
            
        self.widget.showGrid(x=True, y=True, alpha=0.3)
        
        self.logger=setup_logger(f"visualizer_{sensor_name}")
        
    @HookimplMarker("sensorsDesktop")
    def start(self):
        self.is_active = True
        if not self.timer.isActive():
            self.timer.start()
            
    @HookimplMarker("sensorsDesktop")
    def stop(self):
        self.is_active = False
        if self.timer.isActive():
            self.timer.stop()
            
    def _update_loop(self):
        if not self.is_active:
            return

        params = self.get_query_params() #get from child
        if params is None:
            return

        host=getenv("REST_IP")
        port=getenv("REST_PORT")
        
        try:
            api_url = f"http://{host}:{port}/data/{self.sensor_name}"
            response = requests.get(api_url, params=params, timeout=1.5)
            response.raise_for_status()
            
            data = response.json().get("results", [])

            x, y = self.process_data(data)

            if x is not None and y is not None:
                self.curve.setData(x, y)

        except requests.exceptions.RequestException as e:
            print(f"[{self.sensor_name}] API Error: {e}")
        except Exception as e:
            print(f"[{self.sensor_name}] Data Error: {e}")

    def get_ui_element(self):
        return self.widget

    @abstractmethod
    def get_query_params(self):
        pass

    @abstractmethod
    def process_data(self, json_results):
        pass
        
        