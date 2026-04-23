from importlib.metadata import entry_points

from PyQt6.QtWidgets import QHBoxLayout, QListWidget, QStackedWidget, QWidget

class VisualizationParent(QWidget):
    def __init__(self):
        super().__init__()
        self._load_visualizations()
        
        if self.available_visualizations is not None and len(self.available_visualizations)>0:
            self.active_visualization=self.available_visualizations[0]
            self.active_visualization.start()
            
        self.initUI()
        
        
    def _load_visualizations(self):
        _entry_points = entry_points(group='plugins.visualizations')
        self.available_visualizations=list()
        print(_entry_points)
    
        for viz in _entry_points:
            viz_class=viz.load()
            viz_instance=viz_class()
            self.available_visualizations.append(viz_instance)

    def initUI(self):
        self.main_layout = QHBoxLayout(self)
        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        
        self.stack = QStackedWidget()
        
        for viz_plugin in self.available_visualizations:
            self.sidebar.addItem(viz_plugin.title)
            
            ui_widget = viz_plugin.get_ui_element()
            self.stack.addWidget(ui_widget)

        self.sidebar.currentRowChanged.connect(self.handle_selection_change)

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stack)
        
        if self.available_visualizations:
            self.sidebar.setCurrentRow(0)

    def handle_selection_change(self, index):
        """Logic to switch sensors using list indices"""
        if hasattr(self, 'active_visualization') and self.active_visualization:
            self.active_visualization.stop()

        self.active_visualization = self.available_visualizations[index]
        
        self.stack.setCurrentIndex(index)
        
        self.active_visualization.start()
            
    