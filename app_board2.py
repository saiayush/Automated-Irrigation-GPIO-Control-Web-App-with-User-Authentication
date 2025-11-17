####perfectly working code only for login###############3

from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from threading import Thread, current_thread  
import time
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.secret_key = os.urandom(24)

target_directory = "/home/pi/IrrSwitch/pin_comm/WiringNP/gpio"

# Load user data from JSON file
def load_data():
    try:
        with open('data.json', 'r') as file:
            return json.load(file)['users']  # Access 'users' key in the JSON data
    except FileNotFoundError:
        return {}

def save_data(users):
    with open('data.json', 'w') as file:
        json.dump({'users': users}, file, indent=2)


json_file_path = 'automation.json'
log_file_path = 'automation_log.txt'
log_retention_period = 15 * 24 * 3600  # 15 days in seconds

def log_event(event):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{timestamp} {event}\n")

    # Check if log file exceeds retention period and delete old entries
    delete_old_logs()

def delete_old_logs():
    current_time = time.time()
    with open(log_file_path, 'r+') as log_file:
        lines = log_file.readlines()
        log_file.seek(0)
        for line in lines:
            log_time_str = line.split()[0][1:]  # Extract timestamp from log entry
            try:
                log_time = time.mktime(time.strptime(log_time_str, "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                # If the timestamp format doesn't match, skip this log entry
                continue
            if current_time - log_time <= log_retention_period:
                log_file.write(line)
        log_file.truncate()

# Function to periodically delete old log entries
def delete_old_logs_periodically():
    while True:
        delete_old_logs()
        time.sleep(24 * 3600)  # Check every 24 hours

# You can start this function in a separate thread to continuously delete old logs
def start_log_cleanup_thread():
    log_cleanup_thread = Thread(target=delete_old_logs_periodically, daemon=True)
    log_cleanup_thread.start()

def turn_on_button_automated(button):
    # Turn on GPIO for automated control
    pin_number = button  # Assuming button numbers correspond to GPIO pin numbers
    command_mode = f"gpio mode {pin_number} out"  # Set GPIO mode to output
    command_on = f"gpio write {pin_number} 0"

    # Set GPIO mode to output and turn on
    subprocess.run(command_mode, shell=True, cwd=target_directory)
    subprocess.run(command_on, shell=True, cwd=target_directory)

    log_event(f"[{current_thread().name}] [turn_on_button_automated] Button {button} ON")

def turn_off_button_automated(button):
     # Turn off GPIO for automated control
    pin_number = button  # Assuming button numbers correspond to GPIO pin numbers
    command_mode = f"gpio mode {pin_number} out"  # Set GPIO mode to output
    command_off = f"gpio write {pin_number} 1"

    # Set GPIO mode to output and turn off
    subprocess.run(command_mode, shell=True, cwd=target_directory)
    subprocess.run(command_off, shell=True, cwd=target_directory)
    log_event(f"[{current_thread().name}] [turn_off_button_automated] Button {button} OFF")

def check_automation_status(json_file_path='automation.json'):
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            return data.get("automation_status", False)
    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        log_event(f"[{current_thread().name}] [check_automation_status] Error checking automation status: {e}")
        return False
    
def load_button_times():
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            if isinstance(data, dict) and "button_times" in data:
                return {str(i): data["button_times"].get(str(i), 0) for i in range(1, 9)}
            else:
                raise ValueError("Invalid data format or missing 'button_times' key in JSON file")
    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        error_msg = f"[{current_thread().name}] [load_button_times] Error loading button times: {e}"
        log_event(error_msg)
        return {str(i): 0 for i in range(1, 9)}

def save_button_times(button_times):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    # If button_times value is 0, set it to 2
    button_times = {key: 2 if value == 0 else value for key, value in button_times.items()}
    
    data["button_times"] = button_times

    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def load_automation_status():
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            return data.get("automation_status", False)
    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        error_msg = f"[{current_thread().name}] [load_automation_status] Error loading automation status: {e}"
        log_event(error_msg)
        return False

def save_automation_status(status):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    data["automation_status"] = status

    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def load_button_flags():
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            return data.get("button_flags", {str(i): False for i in range(1, 9)})
    except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
        error_msg = f"[{current_thread().name}] [load_button_flags] Error loading button flags: {e}"
        log_event(error_msg)
        return {str(i): False for i in range(1, 9)}

def save_button_flags(button_flags):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    data["button_flags"] = button_flags

    with open(json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def reset_button_flags():
    global button_flags
    button_flags = {str(i): False for i in range(1, 9)}
    save_button_flags(button_flags)

automated_button_times = load_button_times()
automation_status = load_automation_status()
button_flags = load_button_flags()

manual_mode_enabled = True
manual_button_states = {i: False for i in range(1, 9)}
automated_cycle_running = False

def run_automated_cycle():
    global automated_cycle_running, button_flags
    log_event(f"[{current_thread().name}] [run_automated_cycle] Automated cycle started")

    while automated_cycle_running:
        for button, time_in_seconds in automated_button_times.items():
            if not automated_cycle_running:
                break

            if time_in_seconds == 0 or button_flags[str(button)]:
                continue

            turn_on_button_automated(button)

            log_event(f"[{current_thread().name}] [run_automated_cycle] Button {button} ON for {time_in_seconds} seconds")
            time.sleep(time_in_seconds)

            turn_off_button_automated(button)

            log_event(f"[{current_thread().name}] [run_automated_cycle] Button {button} OFF")
            
            # Set button flag to True after completion
            button_flags[str(button)] = True
            save_button_flags(button_flags)
            log_event(f"[{current_thread().name}] [run_automated_cycle] Button {button} flag set to True")
            time.sleep(1)

        # Check if all button flags are True
        if all(flag for flag in button_flags.values()):
            # Reset button flags to False
            reset_button_flags()

    automated_cycle_running = False
    log_event(f"[{current_thread().name}] [run_automated_cycle] Automated cycle stopped")

def check_and_start_automated_cycle():
    global automated_cycle_running, button_flags
    status_flag_json = check_automation_status()
    log_event(f"[{current_thread().name}] [check_and_start_automated_cycle] Checking for automated cycle flag in JSON")

    if status_flag_json and not automated_cycle_running:
        automated_cycle_running = True
        thread = Thread(target=run_automated_cycle)
        thread.start()
        log_event(f"[{current_thread().name}] [check_and_start_automated_cycle] Automated cycle started")
        print(f"[{current_thread().name}] [check_and_start_automated_cycle] Automated cycle started")
    elif not status_flag_json and automated_cycle_running:
        automated_cycle_running = False
        log_event(f"[{current_thread().name}] [check_and_start_automated_cycle] Automated cycle stopped")
        print(f"[{current_thread().name}] [check_and_start_automated_cycle] Automated cycle stopped")

def toggle_gpio(button):
    pin_number = button

    command_mode = f"gpio mode {pin_number} out"  # Set GPIO mode to output
    command_on = f"gpio write {pin_number} 0"
    command_off = f"gpio write {pin_number} 1"

    subprocess.run(command_mode, shell=True, cwd=target_directory)

    if manual_button_states[button]:
        subprocess.run(command_on, shell=True, cwd=target_directory)
        log_event(f"[{current_thread().name}] [toggle_gpio] Button {button} ON")
        print(f"[{current_thread().name}] [toggle_gpio] Button {button} ON")
    else:
        subprocess.run(command_off, shell=True, cwd=target_directory)
        log_event(f"[{current_thread().name}] [toggle_gpio] Button {button} OFF")
        print(f"[{current_thread().name}] [toggle_gpio] Button {button} OFF")

####------------------------------------------------------------------------------------------###

# Login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_data()
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html', error=None)

# Home page
@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/manual_control')
def manual_control():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    # Load automation status from JSON file
    automation_status = load_automation_status()

    # Disable manual mode if automation is running
    manual_mode_enabled = not automation_status

    return render_template('manual_control.html', button_states=manual_button_states, manual_mode_enabled=manual_mode_enabled)

@app.route('/toggle_manual/<int:button>')
def toggle_manual(button):
    global manual_mode_enabled

    if manual_mode_enabled:
        manual_button_states[button] = not manual_button_states[button]
        toggle_gpio(button)
        log_event(f"[{current_thread().name}] [toggle_manual] Button {button} {'ON' if manual_button_states[button] else 'OFF'}")

    return render_template('manual_control.html', button_states=manual_button_states, manual_mode_enabled=manual_mode_enabled)


# Page 2
@app.route('/automated_control')
def automated_control():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('automated_control.html', button_times=automated_button_times, automated_cycle_running=automated_cycle_running, automation_status=automation_status)

@app.route('/set_time/<int:button>', methods=['POST'])
def set_time(button):
    global manual_mode_enabled, automated_button_times

    if manual_mode_enabled:
        time_in_seconds = int(request.form['time'])
        automated_button_times[str(button)] = time_in_seconds
        save_button_times(automated_button_times)
        log_event(f"[{current_thread().name}] [set_time] Button {button} will be ON for {time_in_seconds} seconds")
        print(f"[{current_thread().name}] [set_time] Button {button} will be ON for {time_in_seconds} seconds")

    return render_template('automated_control.html', button_times=automated_button_times, automated_cycle_running=automated_cycle_running, automation_status=automation_status)

@app.route('/start_cycle', methods=['POST'])
def start_cycle():
    global automated_cycle_running, manual_mode_enabled, automation_status

    if not automated_cycle_running and manual_mode_enabled:
        automated_cycle_running = True
        automation_status = True
        save_automation_status(automation_status)
        thread = Thread(target=run_automated_cycle)
        thread.start()
        log_event(f"[{current_thread().name}] [start_cycle] Automated cycle started")
        print(f"[{current_thread().name}] [start_cycle] Automated cycle started")

    return render_template('automated_control.html', button_times=automated_button_times, automated_cycle_running=automated_cycle_running, automation_status=automation_status)

@app.route('/stop_cycle', methods=['POST'])
def stop_cycle():
    global automated_cycle_running, automation_status

    if automated_cycle_running:
        automated_cycle_running = False
        automation_status = False
        save_automation_status(automation_status)
        reset_button_flags()
        log_event(f"[{current_thread().name}] [stop_cycle] Automated cycle stopped")
        print(f"[{current_thread().name}] [stop_cycle] Automated cycle stopped")

    return render_template('automated_control.html', button_times=automated_button_times, automated_cycle_running=automated_cycle_running, automation_status=automation_status)

# Logout
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Forgot password
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        users = load_data()
        username = request.form['username']
        answers = [request.form[f'answer{i}'].lower() for i in range(1, 4)]

        if username in users and users[username]['security_answers'] == answers:
            session['forgot_password_user'] = username
            return render_template('update_password.html', username=username)
        else:
            flash('Invalid username or security answers. Please try again.', 'error')

    return render_template('forgot_password.html')

# Update password
@app.route('/update_password', methods=['POST'])
def update_password():
    if 'forgot_password_user' in session:
        users = load_data()
        username = session.pop('forgot_password_user')

        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password == confirm_password:
            users[username]['password'] = new_password
            save_data(users)
            flash('Password updated successfully!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('update_password'))

    else:
        flash('Session expired. Please try again.', 'error')
        return redirect(url_for('forgot_password'))

if __name__ == '__main__':
    startup = True
    if startup == True:
        startup_thread = Thread(target=check_and_start_automated_cycle, name='AutomationCheckThread')
        start_log_cleanup_thread()
        startup = False
        startup_thread.start()

    app.run(host='0.0.0.0', port=5300)