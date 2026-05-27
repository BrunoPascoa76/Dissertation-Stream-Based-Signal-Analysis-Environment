import time

from plugins.visualization.BaseVisualizer import BaseVisualizer


class HRVVisualization(BaseVisualizer):
    def __init__(self):
        super().__init__("hrv",title="Heart Rate",x_label="Seconds ago",y_label="BPM")
    
    def get_query_params(self):
        now_ms = int(time.time() * 1000)
        start_ms = now_ms - 60000 #for this one we just need 60s

        return {
            "uuid": self.uuid,      # Identifies the participant
            "agg": None,                   
            "field": "bpm,timestamp",      # The field we are counting
            "start": start_ms,        # Start timestamp
            "end": now_ms,             # End timestamp
        }
        
    def process_data(self, json_results):
        now_ms = int(time.time() * 1000)
        
        if not json_results:
            return None, None

        y = [d.get('bpm',0.0) for d in json_results]
        
        x = list(range(-len(y) + 1, 1))
        
        
        return x,y
    