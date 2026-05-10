from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QPushButton,
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QSystemTrayIcon, QStyle
)
from PyQt6.QtCore import QTimer, QUrl, Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtMultimedia import QSoundEffect
from datetime import datetime

from alarm import Alarm
from storage import Storage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.alarms = []
        self.selected_idx = None
        
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray.show()

        self.alarm = Alarm()
        self.storage = Storage()

        self.setup_ui()
        self.setup_connections()
        self.setup_timer()
        self.alarms = self.storage.load()
        self.render_alarm_list()
        
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
        
        self.right_column = QVBoxLayout()
        main_layout.addLayout(self.right_column)
        self.right_column.setSpacing(8)
        self.right_column.setContentsMargins(5, 5, 5, 5)
        self.right_column.setAlignment(Qt.AlignmentFlag.AlignTop)
        
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

        # Add a start/stop button 
        self.alarm_button = QPushButton("Turn On Alarm")
        left_column.addWidget(self.alarm_button)
        
        # Add an add/save/delete button
        action_layout = QHBoxLayout()
        left_column.addLayout(action_layout)

        self.del_button = QPushButton("Delete Alarm")
        action_layout.addWidget(self.del_button)
        
        self.add_button = QPushButton("Add Alarm")
        action_layout.addWidget(self.add_button)
        
        self.save_button = QPushButton("Save Alarm")
        action_layout.addWidget(self.save_button)

    def render_alarm_list(self):
        # clear layout
        for i in reversed(range(self.right_column.count())):
            widget = self.right_column.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # rebuild UI
        for i, alarm in enumerate(self.alarms):
            btn = QPushButton(alarm["name"])

            btn.clicked.connect(
                lambda _, idx=i: self.select_alarm(idx)
            )

            self.right_column.addWidget(btn)
                    
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
        self.add_button.clicked.connect(self.new_alarm)
        self.del_button.clicked.connect(self.delete_alarm)

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
        
        self.render_alarm_list()

    # Alarm logic
    def update_time(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_display_label.setText(current_time)

        for alarm in self.alarms:
            if not alarm.get("enabled"):
                continue

            alarm_time = f"{alarm['hour']}:{alarm['minute']}:{alarm['second']}"

            if current_time == alarm_time:
                self.sound.play()

                if not alarm.get("notified", False):
                    self.show_notifications("Alarm", alarm["name"])
                    alarm["notified"] = True
                    
        self.storage.save(self.alarms)
                    
    def set_alarm(self):
        h = self.alarm_input_hour.text().strip()
        m = self.alarm_input_minute.text().strip()
        s = self.alarm_input_second.text().strip()

        if not h or not m or not s:
            print("Incomplete time")
            return

        self.alarm.set_time(int(h), int(m), int(s))
    
    def toggle_alarm(self):
        if not self.alarm.enabled:
            h = self.alarm_input_hour.text().strip()
            m = self.alarm_input_minute.text().strip()
            s = self.alarm_input_second.text().strip()
            if not h or not m or not s:
                print("Incomplete time")
                return
        
        if self.alarm.enabled:
            self.alarm.disable()
            self.alarm.notified = False
            self.alarm_button.setText("Turn On Alarm")
            self.unlock_inputs()
        else:
            self.set_alarm()
            self.alarm_button.setText("Turn Off Alarm")
            self.lock_inputs()
            
        if self.selected_idx is not None:
            self.alarms[self.selected_idx]["enabled"] = self.alarm.enabled
            self.storage.save(self.alarms)
        
    # Alarms Operations
    def select_alarm(self, idx):
        self.selected_idx = idx
        alarm = self.alarms[idx]
        
        self.alarm_name.setText(alarm["name"])
        self.alarm_input_hour.setText(alarm["hour"])
        self.alarm_input_minute.setText(alarm["minute"])
        self.alarm_input_second.setText(alarm["second"])
        self.alarm.enabled = alarm["enabled"]
        
        if alarm["enabled"]:
            self.alarm_button.setText("Turn Off Alarm")
            self.lock_inputs()
        else:
            self.alarm_button.setText("Turn On Alarm")

    def new_alarm(self):
        self.selected_idx = None
        self.alarm_name.clear()
        self.alarm_input_hour.clear()
        self.alarm_input_minute.clear()
        self.alarm_input_second.clear()

    def delete_alarm(self):
        if self.selected_idx is None: return
        
        del self.alarms[self.selected_idx]
        self.selected_idx = None
        
        self.storage.save(self.alarms)
        self.render_alarm_list()
        self.new_alarm()
    
    def save_alarm(self):
        if not self.alarm_name.text().strip():
            return
        h = self.alarm_input_hour.text().strip()
        m = self.alarm_input_minute.text().strip()
        s = self.alarm_input_second.text().strip()
        if not h or not m or not s:
            return
        
        # Save alarm time into JSON
        data = {
            "name": self.alarm_name.text(),
            "hour": self.alarm_input_hour.text(),
            "minute": self.alarm_input_minute.text(),
            "second": self.alarm_input_second.text(),
            "enabled": self.alarm.enabled
        }
        
        if self.selected_idx is None:
            self.alarms.append(data)
            self.selected_idx = len(self.alarms) - 1
        else:
            self.alarms[self.selected_idx] = data
            
        self.storage.save(self.alarms)
        self.render_alarm_list()

    # UI helpers
    def lock_inputs(self):
        self.alarm_input_hour.setDisabled(True)
        self.alarm_input_minute.setDisabled(True)
        self.alarm_input_second.setDisabled(True)

    def unlock_inputs(self):
        self.alarm_input_hour.setDisabled(False)
        self.alarm_input_minute.setDisabled(False)
        self.alarm_input_second.setDisabled(False)