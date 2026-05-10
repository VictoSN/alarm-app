import json
import os

class Storage:
    def __init__(self, path="alarm.json"):
        self.path = path
            
    def save(self, data, ):
        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)
    
    def load(self):
        if not os.path.exists(self.path):
            return {}
        try:
            with open(self.path, "r") as f:
                return json.load(f)
        except:
            return {}