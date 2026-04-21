import time

from plugins.visualization import BaseVisualizer


class KeysPerMinuteVisualization(BaseVisualizer):
    def __init__(self):
        super().__init__("keyboard")
        
    def get_query_params(self):
        now_ms = int(time.time() * 1000)
        start_ms = now_ms - 120000 #120s to guarantee each minute has a 60s before it

        return {
            "uid": self.user_id,      # Identifies the participant
            "agg": "COUNT",           # We want to count keypresses
            "field": "key_code",      # The field we are counting
            "interval": "1s",         # The 'Group By' bucket size
            "start": start_ms,        # Start timestamp
            "end": now_ms             # End timestamp
        }
        
    def process_data(self, json_results):
        raw_counts = [d.get('count_key_code', 0) for d in json_results]
        
        if len(raw_counts) < 60:
            #we have less than a minute available, so we have to multiply the per-second numbers by 60
            y = [val * 60 for val in raw_counts]
            x = list(range(-len(y) + 1, 1))
            return x, y
        
        cpm_values = []
        
        #for each element in the last minute
        for i in range(60, len(raw_counts) + 1):
            current_minute_sum = sum(raw_counts[i-60 : i]) # Sum the values of the 60s before it to get "characters per minute"
            cpm_values.append(current_minute_sum)
        
        x_values = list(range(-len(cpm_values) + 1, 1)) #the "0" (now) is on the far right
        
        return x_values, cpm_values