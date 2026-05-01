import time
import numpy as np
from plugins.visualization.CompositeVisualizer import CompositeVisualizer


class AttentionVisualization(CompositeVisualizer):
    def __init__(self):
        super().__init__(["keyboard","hrv","face"],title="Attention",x_label="Seconds ago",y_label="HRV")
        self.attention_weights={"face":0.5,"hrv":0.2,"keyboard":0.3} #these sensors may be finetuned for better results
        
    def get_query_params(self):
        now_ms = int(time.time() * 1000)
        start_ms = now_ms - 60000
        
        params=[]
        
        #keyboard
        params.append(
            {
            "uuid": self.uuid,      
            "agg": "COUNT",           
            "field": "value",      
            "interval": "1s",         
            "start": start_ms,        
            "end": now_ms
            }
        )
        
        params.append(
            {
            "uuid": self.uuid,
            "agg": "MEAN",
            "field": "value",
            "interval": "1s",
            "start": start_ms,
            "end": now_ms
            }
        )
        
        params.append(
            {
            "uuid": self.uuid,
            "agg": "MEAN",
            "field": "ear,yaw,pitch",
            "interval": "1s",
            "start": start_ms,
            "end": now_ms
            }
        )
        return params
    
    def process_data(self, json_results):
        print(json_results)
        total_weight=0 #by dividing by total weight, unused sensors will not contribute to the results
        attention_scores=[] #each element is an array of scores, 1 per second
        active_sensors=[]

        #get attention "scores" from each sensor
        if "hrv" in json_results:
            attention_scores.append(self._get_hrv_score(json_results["hrv"]))
            total_weight+=self.attention_weights["hrv"]
            active_sensors.append("hrv")
        if "face" in json_results:
            attention_scores.append(self._get_face_score(json_results["face"]))
            total_weight+=self.attention_weights["face"]
            active_sensors.append("face")
        if "keyboard" in json_results:
            attention_scores.append(self._get_keyboard_score(json_results["keyboard"]))
            total_weight+=self.attention_weights["keyboard"]
            active_sensors.append("keyboard")
        
        #calculate final attention
        if not attention_scores or total_weight == 0:
            return None, None
        
        min_len = min(len(score_arr) for score_arr in attention_scores)
        
        final_sum = np.zeros(min_len)
        
        for i in range(len(attention_scores)):
            # Convert to numpy array, clip to min_len, and multiply by its weight
            final_sum += np.array(attention_scores[i][:min_len]) * self.attention_weights[active_sensors[i]]
            
        final_y = (final_sum / total_weight).tolist()
        
        x = list(range(-len(final_y) + 1, 1))

        return x, final_y
    
    def _get_keyboard_score(self, kb_data):
        if not kb_data:
            return []
        
        MAX_KPS = 6.0 #6 keys per second should be around 70~80 wpm, which is a good standard for "100% focused"
    
        raw_scores = []
        for d in kb_data:
            count = d.get('count',0)
            score = min(100.0, (count / MAX_KPS) * 100.0)
            raw_scores.append(score)
            
        # use a moving average to "smoothen out" the scores to not be as affected by natural pauses
        smoothed_scores = []
        for i in range(len(raw_scores)):
            window = raw_scores[max(0, i-2) : i+1]
            smoothed_scores.append(sum(window) / len(window))

        return smoothed_scores
    
    def _get_hrv_score(self, hrv_data):
        if not hrv_data:
            return []
    
        MIN_HRV = 30.0  # Stress/Distraction floor
        MAX_HRV = 90.0  # Focus/Flow ceiling
        
        scores = []
        for d in hrv_data:
            val = d.get('mean', d.get('value', 60)) # Default to 60 if missing
            
            # Linear normalization to 0-100
            score = (val - MIN_HRV) / (MAX_HRV - MIN_HRV) * 100
            
            # Clamp between 0 and 100
            scores.append(max(0, min(100, score)))
            
        return scores
    
    def _get_face_score(self, face_data):
        if not face_data:
            return []

        scores = []
        OFFSET = 1.8
        YAW_THRESHOLD = 5.0    # Degrees allowed before penalty
        PITCH_THRESHOLD = 2.0  # Degrees allowed before penalty
        EAR_THRESHOLD = 0.22   # Below this = eyes closed/blinking

        for d in face_data:
            ear = d.get('mean_ear', 0)
            yaw = abs(d.get('mean_yaw', 0) + OFFSET)
            pitch = abs(d.get('mean_pitch', 0) + OFFSET)

            if ear < EAR_THRESHOLD:
                scores.append(0)
                continue

           
            yaw_penalty = max(0, (yaw - YAW_THRESHOLD) * 8)    # -8 points per degree off
            pitch_penalty = max(0, (pitch - PITCH_THRESHOLD) * 15) # -15 points per degree (stricter)

            face_attention = max(0, 100 - yaw_penalty - pitch_penalty)
            scores.append(face_attention)

        return scores