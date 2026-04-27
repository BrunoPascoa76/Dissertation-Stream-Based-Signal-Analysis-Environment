from plugins.visualization.BaseVisualizer import BaseVisualizer


class HRVVisualization(BaseVisualizer):
    def __init__(self):
        super().__init__("HRV",title="Heart Rate Variability",x_label="Seconds ago",y_label="HRV")