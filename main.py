import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIntValidator
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
        
        ## Layout and Validation for inputs
        input_layout = QHBoxLayout()
        validator_H = QIntValidator(0, 23)
        validator_MS = QIntValidator(0, 59)
        
        # Alarm Input
        self.alarm_input_hour = QLineEdit()
        self.alarm_input_hour.setValidator(validator_H)
        self.alarm_input_hour.setMaxLength(2)
        self.alarm_input_hour.setPlaceholderText("HH")
        input_layout.addWidget(self.alarm_input_hour)
        
        self.alarm_input_minute = QLineEdit()
        self.alarm_input_minute.setValidator(validator_MS)
        self.alarm_input_hour.setMaxLength(2)
        self.alarm_input_minute.setPlaceholderText("MM")
        input_layout.addWidget(self.alarm_input_minute)

        self.alarm_input_second = QLineEdit()
        self.alarm_input_second.setValidator(validator_MS)
        self.alarm_input_hour.setMaxLength(2)
        self.alarm_input_second.setPlaceholderText("SS")
        input_layout.addWidget(self.alarm_input_second)
        
        main_layout.addLayout(input_layout)
        
        # Add a start/stop button
        self.alarm_button = QPushButton("Set Alarm")
        main_layout.addWidget(self.alarm_button)
        
    def setup_connections(self):
        # Connect signals to slots
        self.alarm_button.clicked.connect(self.toggle_alarm)
        
    def setup_timer(self):
        # Init the timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.alarm_time = ""
        self.alarm_enabled = False
        
    def update_time(self):
        # Update the display
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_display_label.setText(current_time)
        if self.alarm_enabled and current_time == self.alarm_time:
            print("Ring Ring Ring!")
        
    def set_alarm(self):
        self.alarm_time =  (
            f"{self.alarm_input_hour.text():0>2}:"
            f"{self.alarm_input_minute.text():0>2}:"
            f"{self.alarm_input_second.text():0>2}"
        )
        self.alarm_enabled = True
        
    def toggle_alarm(self):
        # Turn on or off the alarm
        if self.alarm_enabled:
            self.alarm_enabled = False
            self.alarm_button.setText("Set Alarm")
        else:
            self.set_alarm()
            self.alarm_enabled = True
            self.alarm_button.setText("Disable Alarm")
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())