from datetime import datetime

class Alarm:
    def __init__(self):
        self.alarm_time = None
        self.enabled = False    # Alarm active or not
        self.ringing = False    # Ringing on or not
        
    def set_time(self, hour, minute, second):
        self.alarm_time = f"{hour:02}:{minute:02}:{second:02}"
        self.enabled = True
        self.ringing = False
        
    def disable(self):
        self.enabled = False
        self.ringing = False
        
    def check(self, current_time):
        if not self.enabled:
            return False

        if current_time == self.alarm_time:
            self.ringing = True

        return self.ringing