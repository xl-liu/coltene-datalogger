from flask import Flask, render_template, request, send_file, send_from_directory, jsonify
import time
import csv
import os
from threading import Thread
import smbus
from rtd_lib import tempADC
from pijuice_lib import PiJuice
from datetime import datetime 

# ... (previous code)

app = Flask(__name__)
recording = False  # Flag to control recording

# I2C setup
bus = smbus.SMBus(1)
temp_adc = tempADC(bus, n_channels=5)
pijuice = PiJuice(bus)

# CSV file setup
downloads_directory = "logdata"

def get_pi_status():
    pi_temp = os.popen("vcgencmd measure_temp").readline()
    # pi_temp = pi_temp.replace("temp=", "").strip()
    pi_temp = pi_temp[5:-3]
    pi_time = time.strftime("%Y-%m-%d %H:%M:%S")
    pi_space = get_available_space()
    return pi_temp, pi_time, pi_space

def get_battery_status():

    temp_info = pijuice.status.GetBatteryTemperature()
    if temp_info['error'] == 'NO_ERROR':
        battery_temp = temp_info['data']
    else:
        battery_temp = 'N/A'

    charge_info = pijuice.status.GetChargeLevel()
    if charge_info['error'] == 'NO_ERROR':
        battery_power = charge_info['data']
    else:
        battery_power = 'N/A'    
    
    faults_info = pijuice.status.GetFaultStatus()
    if faults_info['error'] == 'NO_ERROR':
        battery_faults = []
        for fault, flag in faults_info['data'].items():
            if flag: battery_faults.append(fault)
        if not battery_faults:
            battery_faults = 'None'
    else:
        battery_faults = 'N/A'

    return battery_temp, battery_power, battery_faults

def get_available_space():
    try:
        stat = os.statvfs('/')  # Replace with the mount point of /dev/root if different
        # Calculate available space
        available_space = stat.f_frsize * stat.f_bavail
        # Convert to human-readable format (bytes to GB)
        available_space_gb = available_space / (1024 ** 3)
        return round(available_space_gb, 2)
    except Exception as e:
        print(f'Error getting disk space: {e}')
        return 'N/A'
    
@app.route("/")
def index():
    # List all files in the downloads directory
    global recording
    files = os.listdir(downloads_directory)
    return render_template("index.html", files=files, recording=recording)

@app.route("/status")
def status():
    temperature, timestamp, avail_space = get_pi_status()
    battery_temp, battery_power, battery_faults = get_battery_status()
    dic = { 
        "temperature": temperature,
        "timestamp": timestamp,
        "available_space": avail_space,
        "recording": recording,  # Pass recording status to the client
        "battery_temp": battery_temp,
        "battery_power": battery_power,
        "battery_faults": battery_faults
        }
    # print(dic)
    return jsonify(dic)

@app.route("/download/<filename>")
def download_file(filename):
    # Serve files from the downloads directory
    return send_from_directory(downloads_directory, filename)

def record_data():
    global recording
    while True:
        if recording:
            now = datetime.now()
            timestamp = now.strftime('%H:%M:%S.%f')[:-3]
            # Replace the following line with your I2C reading function
            temps = temp_adc.read_all_channels()
            
            with open(csv_filename, "a", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([timestamp] + temps)
        time.sleep(0.2)  # Sleep for 200ms to achieve ~5Hz

@app.route("/start_stop_recording", methods=["POST"])
def start_stop_recording():
    global recording
    global csv_filename
    if recording:
        recording = False
    else:
        recording = True
        csv_filename = f"{downloads_directory}/{time.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        with open(csv_filename, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Time", "Temperature Ch0","Temperature Ch1","Temperature Ch2","Temperature Ch3","Temperature Ch4", "Pressure Data"])  # Add appropriate headers
    return jsonify({"recording": recording})

if __name__ == "__main__":
    record_thread = Thread(target=record_data)
    record_thread.start()

    app.debug = True
    app.run(host="0.0.0.0", port=70)

