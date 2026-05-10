# alarm-app
## A desktop alarm application built with PyQt6
A very basic Python desktop application for setting and managing multiple alarms.

## Features
1. Add / Delete Alarms
2. Named Alarms
3. Persistent Storage in JSON
4. System Tray Notifications

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

## How to run
1. Clone the repo
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```
3. Install dependencies:
```bash
pip install PyQt6
```
4. Add an `alarm.wav` file to the project root
5. Run:
```bash
python main.py
```

## License
This project is licensed under the [MIT License](LICENSE)