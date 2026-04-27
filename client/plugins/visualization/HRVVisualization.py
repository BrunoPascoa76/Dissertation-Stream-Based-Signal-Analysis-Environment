import time

from plugins.visualization.BaseVisualizer import BaseVisualizer


class HRVVisualization(BaseVisualizer):
    def __init__(self):
        super().__init__("hrv",title="Heart Rate Variability",x_label="Seconds ago",y_label="HRV")
    
    def get_query_params(self):
        now_ms = int(time.time() * 1000)
        start_ms = now_ms - 60000 #for this one we just need 60s

        return {
            "uuid": self.uuid,      # Identifies the participant
            "agg": None,           # we just want the values          
            "field": "value",      # The field we are counting
            "start": start_ms,        # Start timestamp
            "end": now_ms             # End timestamp
        }
        
    def process_data(self, json_results):
        if not json_results:
            return None, None

        y = [d.get('value') for d in json_results]
        
        x = list(range(len(y))) 
        
        return x, y
    