import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIntValidator
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtCore import QUrl
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
        
        # Alarm name
        self.alarm_name = QLineEdit()
        self.alarm_name.setPlaceholderText("Alarm")
        main_layout.addWidget(self.alarm_name)
        
        ## Layout and Validation for inputs
        input_layout = QHBoxLayout()
        validator_H = QIntValidator(0, 23)
        validator_MS = QIntValidator(0, 59)

        # Alarm inputs
        self.alarm_input_hour = QLineEdit()
        self.alarm_input_hour.setValidator(validator_H)
        self.alarm_input_hour.setMaxLength(2)
        self.alarm_input_hour.setPlaceholderText("HH")
        input_layout.addWidget(self.alarm_input_hour)
        
        self.alarm_input_minute = QLineEdit()
        self.alarm_input_minute.setValidator(validator_MS)
        self.alarm_input_minute.setMaxLength(2)
        self.alarm_input_minute.setPlaceholderText("MM")
        input_layout.addWidget(self.alarm_input_minute)

        self.alarm_input_second = QLineEdit()
        self.alarm_input_second.setValidator(validator_MS)
        self.alarm_input_second.setMaxLength(2)
        self.alarm_input_second.setPlaceholderText("SS")
        input_layout.addWidget(self.alarm_input_second)
        
        main_layout.addLayout(input_layout)
        
        # Add a start/stop button & save button
        action_layout = QHBoxLayout()
        
        self.alarm_button = QPushButton("Turn On Alarm")
        action_layout.addWidget(self.alarm_button)
        
        self.save_button = QPushButton("Save Alarm")
        action_layout.addWidget(self.save_button)
        
        main_layout.addLayout(action_layout)
        
        
    def setup_connections(self):
        # Connect signals to slots
        self.alarm_button.clicked.connect(self.toggle_alarm)
        self.save_button.clicked.connect(self.save_alarm)
        
        # Auto Save
        self.alarm_name.textChanged.connect(self.schedule_save)
        self.alarm_input_hour.textChanged.connect(self.schedule_save)
        self.alarm_input_minute.textChanged.connect(self.schedule_save)
        self.alarm_input_second.textChanged.connect(self.schedule_save)
        
    def schedule_save(self):
        self.save_timer.start(800)
    
    def setup_timer(self):            
        # Init the timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.timeout.connect(self.save_alarm)
        
        # Init Alarm
        self.alarm_time = ""
        self.alarm_enabled = False
        self.alarm_ringing = False
        
        # Sound Effects
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile("alarm.wav"))
        
        # Load previous alarm
        try:
            data = self.load_data()
            if data:
                self.alarm_name.setText(data["name"])
                self.alarm_input_hour.setText(data["hour"])
                self.alarm_input_minute.setText(data["minute"])
                self.alarm_input_second.setText(data["second"])
                self.alarm_enabled = data["enabled"]
                
                if data["enabled"]:
                    self.set_alarm()
                    self.alarm_button.setText("Turn Off Alarm")
                    
                    # Block the user from changing mid alarm
                    self.alarm_input_hour.setDisabled(True)
                    self.alarm_input_minute.setDisabled(True)
                    self.alarm_input_second.setDisabled(True)
                else:
                    self.alarm_button.setText("Turn On Alarm")
                    
        except json.JSONDecodeError:
            print("No Alarms Saved")

        
    def update_time(self):
        # Update the display
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_display_label.setText(current_time)
        
        # Run infinitely until user turn it off
        if self.alarm_enabled and (current_time == self.alarm_time or self.alarm_ringing):
            self.alarm_ringing = True
            self.sound.play()
            self.alarm_button.setText("Turn Off Alarm")
        
    def set_alarm(self):
        self.alarm_time = (
            f"{self.alarm_input_hour.text():0>2}:"
            f"{self.alarm_input_minute.text():0>2}:"
            f"{self.alarm_input_second.text():0>2}"
        )
           
    def toggle_alarm(self):
        self.alarm_enabled = not self.alarm_enabled

        if self.alarm_enabled:
            self.set_alarm()
            self.alarm_button.setText("Turn Off Alarm")
            
            # Block the user from changing mid alarm
            self.alarm_input_hour.setDisabled(True)
            self.alarm_input_minute.setDisabled(True)
            self.alarm_input_second.setDisabled(True)
        else:
            self.alarm_ringing = False
            self.alarm_button.setText("Turn On Alarm")
            
            self.alarm_input_hour.setDisabled(False)
            self.alarm_input_minute.setDisabled(False)
            self.alarm_input_second.setDisabled(False)


        self.save_alarm()

    def save_alarm(self):
        # Save alarm time into JSON
        data = ({
            "name": self.alarm_name.text(),
            "hour": self.alarm_input_hour.text(),
            "minute": self.alarm_input_minute.text(),
            "second": self.alarm_input_second.text(),
            "enabled": self.alarm_enabled
        })
        self.save_data(data)
            
    def save_data(self, data, ):
        with open("alarm.json", "w") as f:
            json.dump(data, f, indent=4)
    
    def load_data(self):
        try:
            if not os.path.exists("alarm.json"):
                return {}
            with open("alarm.json", "r") as f:
                return json.load(f)
        except:
            return {}
                        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())