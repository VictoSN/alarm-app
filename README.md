# alarm-app
## A desktop alarm application built with PyQt6
A very basic Python desktop application for setting and managing multiple alarms.

## Features
1. Add / Delete Alarms
2. Named Alarms
3. Persistent Storage in JSON
4. System Tray Notifications
4. Light/Dark Mode Based on System's Preferences

## How it works
- Alarms are stored in `alarm.json` and loaded on startup
- A QTimer ticks every second and checks all enabled alarms
- Sound plays when an alarm triggers using QSoundEffect
- System tray notification is shown on trigger

## Screenshots
### Default Interface
![Default](/images/Default.png)

### Multiple Alarms
![Multiple Alarms](/images/Multiple.png)

### Dark Mode
![Dark Mode](/images/Dark.png)

## How to Run

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd alarm-app
```

---

# Windows (PowerShell)

### 2. Create a virtual environment
```powershell
python -m venv venv
```

### 3. Activate the virtual environment
```powershell
.\venv\Scripts\Activate
```

### 4. Install dependencies
```powershell
pip install PyQt6
```

### 5. Run the application
```powershell
python main.py
```

---

# Linux / macOS

### 2. Create a virtual environment
```bash
python3 -m venv venv
```

### 3. Activate the virtual environment
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install PyQt6
```

### 5. Run the application
```bash
python main.py
```

## License
This project is licensed under the [MIT License](LICENSE)