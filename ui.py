from PyQt6.QtWidgets import (
    QLabel, QMainWindow, QPushButton, 
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit,QSystemTrayIcon, QStyle, 
    QCheckBox, QScrollArea
)
from PyQt6.QtCore import QTimer, QUrl, Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from datetime import datetime
from pathlib import Path
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
        self.setGeometry(0, 0, 550, 350)
        self.setWindowTitle("Digital Alarm")

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        
        self.top_container = QWidget()
        self.left_column = QVBoxLayout(self.top_container)

        self.scroll.setWidget(self.top_container)
        main_layout.addWidget(self.scroll)
        
        self.left_column.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.separator = QWidget()
        self.separator.setFixedWidth(2)
        self.separator.setStyleSheet("background-color: gray;")
        main_layout.addWidget(self.separator)
        
        right_column = QVBoxLayout()
        main_layout.addLayout(right_column)
        
        # Create label with styling
        self.time_display_label = QLabel()
        self.time_display_label.setStyleSheet("""
                                 QLabel {
                                     font-size: 80px;
                                     font-weight: bold;
                                     qproperty-alignment: AlignCenter;
                                 }
                                 """)
        right_column.addWidget(self.time_display_label)

        # Alarm name
        self.alarm_name_label = QLabel("Name:")
        right_column.addWidget(self.alarm_name_label)
        
        self.alarm_name = QLineEdit()
        self.alarm_name.setPlaceholderText("Alarm")
        right_column.addWidget(self.alarm_name)

        ## Layout and Validation for inputs
        self.alarm_time_label = QLabel("Time:")
        right_column.addWidget(self.alarm_time_label)
        input_layout = QHBoxLayout()
        right_column.addLayout(input_layout)

        validator_H = QRegularExpressionValidator(
            QRegularExpression(r"^([01]?\d|2[0-3])$")
        )

        validator_MS = QRegularExpressionValidator(
            QRegularExpression(r"^([0-5]?\d)$")
        )
        
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

        self.alarm_days_label = QLabel("Repeat:")
        right_column.addWidget(self.alarm_days_label)
        days_layout = QHBoxLayout()
        right_column.addLayout(days_layout)

        self.day_checkboxes = {}
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]      
        
        for day in days:
            checkbox = QCheckBox(day)
            self.day_checkboxes[day] = checkbox
            days_layout.addWidget(checkbox)  

        alarm_layout = QHBoxLayout()
        right_column.addLayout(alarm_layout)

        # Add a start/stop button 
        self.alarm_button = QPushButton("Turn On Alarm")
        alarm_layout.addWidget(self.alarm_button)
    
        # Add a dismiss button 
        self.dismiss_button = QPushButton("Dismiss")
        alarm_layout.addWidget(self.dismiss_button)
        self.dismiss_button.setDisabled(True)

        # Add an add/save/delete button
        action_layout = QHBoxLayout()
        right_column.addLayout(action_layout)

        self.del_button = QPushButton("Delete Alarm")
        action_layout.addWidget(self.del_button)
        
        self.add_button = QPushButton("Add Alarm")
        action_layout.addWidget(self.add_button)
        
        self.save_button = QPushButton("Save Alarm")
        action_layout.addWidget(self.save_button)
        self.action_inputs(False)

    def render_alarm_list(self):
        if len(self.alarms) > 0:
            self.scroll.show()
            self.separator.setVisible(True)
        else:
            self.scroll.hide()
            self.separator.setVisible(False)
        
        # clear layout
        for i in reversed(range(self.left_column.count())):
            widget = self.left_column.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # rebuild UI
        for i, alarm in enumerate(self.alarms):
            button_text = ' '
            if alarm.get("enabled", False):
                button_text += "➤ "
            button_text += alarm["name"]
                
            btn = QPushButton(button_text)
            btn.setStyleSheet("text-align: left;")
            btn.clicked.connect(
                lambda _, idx=i: self.select_alarm(idx)
            )

            self.left_column.addWidget(btn)          
                  
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
        self.dismiss_button.clicked.connect(self.dismiss_alarm)
        self.save_button.clicked.connect(self.save_alarm)
        self.add_button.clicked.connect(self.new_alarm)
        self.del_button.clicked.connect(self.delete_alarm)

    def setup_timer(self):
        # Init the timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # Sound Effects
        BASE_DIR = Path(__file__).resolve().parent
        sound_file = BASE_DIR / "alarm.wav"

        self.sound = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.sound.setAudioOutput(self.audio_output)
        self.sound.setSource(QUrl.fromLocalFile(str(sound_file)))
        self.sound.mediaStatusChanged.connect(self._loop_sound)

    def _loop_sound(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.sound.play()

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
            self.set_inputs_enabled(False)
        else:
            self.alarm_button.setText("Turn On Alarm")
        
        self.render_alarm_list()

    # Alarm logic
    def update_time(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        today = datetime.now().strftime("%a")
        self.time_display_label.setText(current_time)

        for alarm in self.alarms:
            if not alarm.get("enabled"):
                continue
            
            if alarm.get("days") and today not in alarm["days"]:
                continue
            
            alarm_time = f"{alarm['hour']}:{alarm['minute']}:{alarm['second']}"

            if current_time == alarm_time and not alarm.get("ringing", False):
                self.dismiss_button.setDisabled(False)
                alarm["ringing"] = True
                self.sound.play()
                self.show_notifications("Alarm", alarm["name"])
                    
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
            self.sound.stop()
            self.sound.setPosition(0)
            self.alarm.disable()
            self.alarm_button.setText("Turn On Alarm")
            self.dismiss_button.setDisabled(True)
            self.set_inputs_enabled(True)
        else:
            self.save_alarm()
            self.set_alarm()
            self.alarm_button.setText("Turn Off Alarm")
            self.set_inputs_enabled(False)
            
        if self.selected_idx is not None:
            self.alarms[self.selected_idx]["enabled"] = self.alarm.enabled
            self.storage.save(self.alarms)
            
        self.render_alarm_list()
        
    # Alarms Operations
    def select_alarm(self, idx):
        self.selected_idx = idx
        alarm = self.alarms[idx]
        self.action_inputs(True)
        
        for d, cb in self.day_checkboxes.items():
            cb.setChecked(d in alarm.get("days", []))
        
        self.alarm_name.setText(alarm["name"])
        self.alarm_input_hour.setText(alarm["hour"])
        self.alarm_input_minute.setText(alarm["minute"])
        self.alarm_input_second.setText(alarm["second"])
        self.alarm.enabled = alarm["enabled"]
        
        if alarm["enabled"]:
            self.alarm_button.setText("Turn Off Alarm")
            self.set_inputs_enabled(False)
        else:
            self.alarm_button.setText("Turn On Alarm")
            self.set_inputs_enabled(True)

    def dismiss_alarm(self):
        self.sound.stop()
        self.sound.setPosition(0)
        if self.selected_idx is not None:
            self.alarms[self.selected_idx]["ringing"] = False
        self.storage.save(self.alarms)
        self.dismiss_button.setDisabled(True)

    def new_alarm(self):
        for cb in self.day_checkboxes.values():
            cb.setChecked(False)
            
        self.selected_idx = None
        
        self.alarm.disable()
        self.alarm_button.setText("Turn On Alarm")
        self.set_inputs_enabled(True)
        
        self.alarm_name.clear()
        self.alarm_input_hour.clear()
        self.alarm_input_minute.clear()
        self.alarm_input_second.clear()
        self.action_inputs(False)

    def delete_alarm(self):
        if self.selected_idx is None: 
            return
        
        self.alarm.disable()
        self.alarm_button.setText("Turn On Alarm")
        self.set_inputs_enabled(True)
        
        del self.alarms[self.selected_idx]
        self.selected_idx = None
        
        self.storage.save(self.alarms)
        self.render_alarm_list()
        self.new_alarm()
        self.action_inputs(False)
    
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
            "enabled": self.alarm.enabled,
            "days": [d for d, cb in self.day_checkboxes.items() if cb.isChecked()]
        }
        
        if self.selected_idx is None:
            self.alarms.append(data)
            self.selected_idx = len(self.alarms) - 1
        else:
            self.alarms[self.selected_idx] = data
            
        self.storage.save(self.alarms)
        self.render_alarm_list()
        self.action_inputs(True)

    # UI helpers
    def set_inputs_enabled(self, enabled):
        widgets = [
            self.alarm_input_hour,
            self.alarm_input_minute,
            self.alarm_input_second,
            *self.day_checkboxes.values()
        ]

        for widget in widgets:
            widget.setDisabled(not enabled)
            
    def action_inputs(self, enabled):
        self.del_button.setDisabled(not enabled)