from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QPushButton,
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QSystemTrayIcon, QStyle
)
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtGui import QIntValidator
from PyQt6.QtMultimedia import QSoundEffect
from datetime import datetime

from alarm import Alarm
from storage import Storage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray.show()

        self.alarm = Alarm()
        self.storage = Storage()

        self.setup_ui()
        self.setup_connections()
        self.setup_timer()
        self.load_alarm()
        
    def setup_ui(self):
        # Create and arrange the widgets
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle("Digital Clock")

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        left_column = QVBoxLayout()
        main_layout.addLayout(left_column)

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
        left_column.addWidget(self.time_display_label)

        # Alarm name
        self.alarm_name = QLineEdit()
        self.alarm_name.setPlaceholderText("Alarm")
        left_column.addWidget(self.alarm_name)

        ## Layout and Validation for inputs
        input_layout = QHBoxLayout()
        left_column.addLayout(input_layout)

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

        # Add a start/stop button & save button
        action_layout = QHBoxLayout()
        left_column.addLayout(action_layout)

        self.alarm_button = QPushButton("Turn On Alarm")
        action_layout.addWidget(self.alarm_button)

        self.save_button = QPushButton("Save Alarm")
        action_layout.addWidget(self.save_button)

    def show_notifications(self, title, message):
        self.tray.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information,
            5000
        )

    def setup_connections(self):
        # Connect signals to slots
        self.alarm_button.clicked.connect(self.toggle_alarm)
        self.save_button.clicked.connect(self.save_alarm)

    def setup_timer(self):
        # Init the timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # Sound Effects
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile("alarm.wav"))

    def load_alarm(self):
        data = self.storage.load()
        if not data:
            return

        self.alarm_name.setText(data.get("name", ""))
        self.alarm_input_hour.setText(data.get("hour", ""))
        self.alarm_input_minute.setText(data.get("minute", ""))
        self.alarm_input_second.setText(data.get("second", ""))

        if data.get("enabled"):
            self.alarm.set_time(
                int(data["hour"]),
                int(data["minute"]),
                int(data["second"])
            )
            self.alarm_button.setText("Turn Off Alarm")
            self.lock_inputs()
        else:
            self.alarm_button.setText("Turn On Alarm")

    # Alarm logic
    def update_time(self):
        # Update the display
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_display_label.setText(current_time)

        # Run infinitely until user turn it off
        if self.alarm.check(current_time):
            self.sound.play()
            
            if not self.alarm.notified:
                print("ringing inside here")
                self.show_notifications(
                    "Alarm",
                    f"{self.alarm_name.text()} is ringing!"
                )
                self.alarm.notified = True

    def set_alarm(self):
        self.alarm.set_time(
            int(self.alarm_input_hour.text()),
            int(self.alarm_input_minute.text()),
            int(self.alarm_input_second.text())
        )

    def toggle_alarm(self):
        if self.alarm.enabled:
            self.alarm.disable()
            self.alarm.notified = False
            self.alarm_button.setText("Turn On Alarm")
            self.unlock_inputs()
        else:
            self.set_alarm()
            self.alarm_button.setText("Turn Off Alarm")
            self.lock_inputs()

        self.save_alarm()

    # Saving alarms
    def save_alarm(self):
        # Save alarm time into JSON
        data = {
            "name": self.alarm_name.text(),
            "hour": self.alarm_input_hour.text(),
            "minute": self.alarm_input_minute.text(),
            "second": self.alarm_input_second.text(),
            "enabled": self.alarm.enabled
        }
        self.storage.save(data)

    # UI helpers
    def lock_inputs(self):
        self.alarm_input_hour.setDisabled(True)
        self.alarm_input_minute.setDisabled(True)
        self.alarm_input_second.setDisabled(True)

    def unlock_inputs(self):
        self.alarm_input_hour.setDisabled(False)
        self.alarm_input_minute.setDisabled(False)
        self.alarm_input_second.setDisabled(False)