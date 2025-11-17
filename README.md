# Automated-Irrigation-GPIO-Control-Web-App-with-User-Authentication
This project is a web-based automation system for controlling GPIO pins on a FriendlyARM, primarily designed for irrigation or general-purpose actuator control. It features a secure login system, manual and automated control modes, and robust logging for monitoring operations.

# Automated GPIO & Irrigation Control Web App 

This project is a **web-based automation system** for controlling GPIO pins on a **FriendlyARM board**. It integrates **manual and automated irrigation control** with **user authentication** and **activity logging**, making it ideal for smart irrigation, home automation, or any GPIO-based control system.


## Features 

- **User Authentication**
  - Login, logout, forgot password, and password reset functionality.
- **Manual Control**
  - Toggle GPIO pins individually with real-time status feedback.
- **Automated Control**
  - Set time-based automated cycles for multiple GPIO pins.
- **Persistent Settings**
  - Saves button times, automation status, and flags in JSON files.
- **Activity Logging**
  - Logs every action with timestamps; automatically cleans old logs after 15 days.
- **FriendlyARM Compatible**
  - Designed to run on FriendlyARM boards for edge IoT applications.
- **Multi-Threaded Automation**
  - Background threads handle automated cycles and log cleanup for smooth operation.


## Tech Stack 

- **Hardware**: FriendlyARM Board, GPIO pins  
- **Software**: Python, Flask, JSON for persistent storage  
- **Concurrency**: Python `threading` for background automation and log cleanup  
- **Web Interface**: HTML templates with Flask rendering for manual and automated control  

## Prerequisites 

- FriendlyARM board with Python 3.x installed  
- Access to GPIO pins (configured for your FriendlyARM model)  

## Installation & Setup 

1. Clone this repository:
    ```bash
    git clone https://github.com/<your-username>/friendlyarm-gpio-automation.git
    cd friendlyarm-gpio-automation
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Ensure the following directories and files exist:
    - `data.json` → For storing user credentials and security answers  
    - `automation.json` → For saving automation settings  
    - `automation_log.txt` → For logging events  

4. Update the GPIO target directory if needed:
    ```python
    target_directory = "/home/pi/IrrSwitch/pin_comm/WiringNP/gpio"
    ```

5. Run the Flask application:
    ```bash
    python app.py
    ```

6. Open your web browser and navigate to:
    ```
    http://<friendlyarm-ip>:5300
    ```

---

## JSON File Structure 

**data.json**  
```json
{
  "users": {
    "admin": {
      "password": "admin123",
      "security_answers": ["answer1", "answer2", "answer3"]
    }
  }
}
