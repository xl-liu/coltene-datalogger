from flask import Flask, render_template, request, send_file, send_from_directory, jsonify
import time
import csv
import os
import threading
import smbus
from rtd_lib import tempADC
from pijuice import PiJuice

# ... (previous code)

app = Flask(__name__)
recording = False  # Flag to control recording

# I2C setup
bus = smbus.SMBus(1)
temp_adc = tempADC(bus)
pijuice = PiJuice(bus)

# CSV file setup
downloads_directory = "logdata"

def get_pi_status():
    pi_temp = os.popen("vcgencmd measure_temp").readline()
    pi_temp = pi_temp.replace("temp=", "").strip()
    pi_time = time.strftime("%Y-%m-%d %H:%M:%S")
    return pi_temp, pi_time

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
    else:
        battery_faults = 'N/A'

    return battery_temp, battery_power, battery_faults

@app.route("/")
def index():
    # List all files in the downloads directory
    global recording
    files = os.listdir(downloads_directory)
    return render_template("index.html", files=files, recording=recording)

@app.route("/status")
def status():
    temperature, timestamp = get_pi_status()
    battery_temp, battery_power, battery_faults = get_battery_status()
    return jsonify({ 
        "temperature": temperature,
        "timestamp": timestamp,
        "recording": recording,  # Pass recording status to the client
        "battery_temp": battery_temp,
        "battery_power": battery_power,
        "battery_faults": battery_faults
        })

@app.route("/download/<filename>")
def download_file(filename):
    # Serve files from the downloads directory
    return send_from_directory(downloads_directory, filename)

@app.route("/start_stop_recording", methods=["POST"])
def start_stop_recording():
    global recording
    if recording:
        recording = False
        csv_filename = time.strftime("%Y-%m-%d_%H-%M-%S") + '.csv'
        filename = downloads_directory + '/' + csv_filename
        with open(filename, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Time", "Data"])  # Add appropriate headers
            # Read data from I2C here
            # data = bus.read_byte_data(address, register)  # Replace with your I2C read code
            data = 1
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            csv_writer.writerow([timestamp, data])
    else:
        recording = True
    return jsonify({"recording": recording})

if __name__ == "__main__":
    
    app.debug = True
    app.run(host="0.0.0.0", port=70)

