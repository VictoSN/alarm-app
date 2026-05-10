import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_connections()
        self.setup_timer()
        
    def setup_ui(self):
        # Create and arrange the widgets
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle("Digital Clock")
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create label with styling
        self.time_display_label = QLabel()
        self.time_display_label.setStyleSheet("""
                                 QLabel {
                                     font-size: 48px;
                                     font-weight: bold;
                                     color: black;
                                     qproperty-alignment: AlignCenter;
                                 }
                                 """)
        main_layout.addWidget(self.time_display_label)
        
        # Add a start/stop button
        self.toggle_button = QPushButton("Stop Clock")
        main_layout.addWidget(self.toggle_button)
        
    def setup_connections(self):
        # Connect signals to slots
        self.toggle_button.clicked.connect(self.toggle_clock)
        
    def setup_timer(self):
        # Init the timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.is_running = True
        
    def update_time(self):
        # Update the display
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_display_label.setText(current_time)
        
    def toggle_clock(self):
        # Start or stop the clock
        if self.is_running:
            self.timer.stop()
            self.toggle_button.setText("Start Clock")
            self.is_running = False
        else:
            self.timer.start(1000)
            self.toggle_button.setText("Stop Clock")
            self.is_running = True
            self.update_time()
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())