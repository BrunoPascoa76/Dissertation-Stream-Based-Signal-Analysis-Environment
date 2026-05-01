from os import getenv

import requests

from plugins.visualization.BaseVisualizer import BaseVisualizer


class CompositeVisualizer(BaseVisualizer):
    """Subclass of BaseVisualizer. It works almost identically to BaseVisualizer, however it visualizes data extrapolated from multiple sensors instead of just one"""
    def __init__(self, sensor_names, title, x_label=None, y_label=None, update_ms=2000, background_color="w", line_color="r"):
        super().__init__("",title, x_label=None, y_label=None, update_ms=2000, background_color="w", line_color="r")
        self.sensor_names=sensor_names
        
    def _update_loop(self):
        if not self.is_active:
            return

        params_lst = self.get_query_params() #get from child
        if params_lst is None:
            return

        host=getenv("REST_IP")
        port=getenv("REST_PORT")
        data=dict()
        
        for i, sensor_name in enumerate(self.sensor_names):
            try:
                params = params_lst[i] if i < len(params_lst) else params_lst[-1]
                
                api_url = f"http://{host}:{port}/data/{sensor_name}"
                response = requests.get(api_url, params=params, timeout=1.5)
                response.raise_for_status()

                results=response.json().get("results",None)
                if results is not None:
                    data[sensor_name]=results
                
            except requests.exceptions.RequestException as e:
                print(f"[{sensor_name}] API Error: {e}")
            except Exception as e:
                print(f"[{sensor_name}] Data Error: {e}")
                
        x, y = self.process_data(data)

        if x is not None and y is not None:
            self.curve.setData(x, y)
        
