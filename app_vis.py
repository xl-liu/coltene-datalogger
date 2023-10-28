from flask import Flask, render_template, request, send_file, send_from_directory, jsonify
from dash import Dash, dcc, html, Input, Output
import time
import csv
import os
from threading import Thread
import smbus
from rtd_lib import tempADC
from pijuice_lib import PiJuice
from datetime import datetime 
import plotly.graph_objects as go
import matplotlib.pyplot as plt

app = Flask(__name__)
recording = False  # Flag to control recording

# dash wrapper
app = Flask(__name__)
dash_app = Dash(__name__, server=app, url_base_pathname='/dash/')
dash_app.layout = html.Div([
    dcc.Graph(id='temp-plot'),
    dcc.Interval(
            id='interval-component',
            interval=1*1000,  # in milliseconds
            n_intervals=0
    )
])

# I2C setup
bus = smbus.SMBus(1)
temp_adc = tempADC(bus, n_channels=5)
pijuice = PiJuice(bus)

# data buffer for visualization 
DATA_RATE = 2   # Hz
WLEN = int(DATA_RATE * 25)  # 25 seconds of data
time_buffer = [0] * WLEN
temp_buffer0 = [0] * WLEN
temp_buffer1 = [0] * WLEN
temp_buffer2 = [0] * WLEN
temp_buffer3 = [0] * WLEN
temp_buffer4 = [0] * WLEN
pressure_buffer = [0] * WLEN

# CSV file setup
downloads_directory = "logdata"

# Dash callback to update graph
@dash_app.callback(
    Output('temp-plot', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n_intervals):
    # Use the global lists to plot
    global time_buffer, temp_buffer
    
    # Create Plotly figure without Pandas
    fig = {
        'data': [
            go.Scatter(
                x=time_buffer,
                y=temp_buffer0,
                mode='lines',
                name='Temperature Ch 1'
            ),
            go.Scatter(
                x=time_buffer,
                y=temp_buffer1,
                mode='lines',
                name='Temperature Ch 2'
            ),
            go.Scatter(
                x=time_buffer,
                y=temp_buffer2,
                mode='lines',
                name='Temperature Ch 3'
            ),            
            go.Scatter(
                x=time_buffer,
                y=temp_buffer3,
                mode='lines',
                name='Temperature Ch 4'
            ),            
            go.Scatter(
                x=time_buffer,
                y=temp_buffer4,
                mode='lines',
                name='Temperature Ch 5'
            ),            
            # go.Scatter(
            #     x=time_buffer,
            #     y=pressure_buffer,
            #     mode='lines',
            #     name='Pressure'
            # )
        ],
        'layout': go.Layout(
            title='Temperature Over Time',
            xaxis=dict(title='Time (s)'),
            yaxis=dict(title='Temperature (°C)'),
            legend=dict(x=0, y=1, traceorder='normal'),
            font=dict(family='Helvetica, sans-serif', size=14)
        )
    }
    return fig

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
    return jsonify(dic)

@app.route("/download/<filename>")
def download_file(filename):
    # Serve files from the downloads directory
    return send_from_directory(downloads_directory, filename)

def record_data():
    global recording
    tt = 0
    while True:
        now = datetime.now()
        timestamp = now.strftime('%H:%M:%S.%f')[:-3]
        temps = temp_adc.read_all_channels()
        temp_buffer0.append(temps[0])
        time_buffer.append(tt)
        tt += 1. /  DATA_RATE
        temp_buffer0.pop(0)
        time_buffer.pop(0)
        temp_buffer1.append(temps[1])
        temp_buffer1.pop(0)
        temp_buffer2.append(temps[2])
        temp_buffer2.pop(0)        
        temp_buffer3.append(temps[3])
        temp_buffer3.pop(0)       
        temp_buffer4.append(temps[4])
        temp_buffer4.pop(0)
        if recording:
            with open(csv_filename, "a", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([timestamp] + temps)
        time.sleep(1. / DATA_RATE)  # Sleep 

@app.route("/start_stop_recording", methods=["POST"])
def start_stop_recording():
    global recording
    global csv_filename
    if recording:
        recording = False
        plot_recorded_data()
    else:
        recording = True
        csv_filename = f"{downloads_directory}/{time.strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        with open(csv_filename, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Time", "Temperature Ch0","Temperature Ch1","Temperature Ch2",
                                 "Temperature Ch3","Temperature Ch4","Pressure Data"])  # Add appropriate headers
    return jsonify({"recording": recording})

def plot_recorded_data():
    # read the csv file
    tt = []
    temp_data0 = []
    temp_data1 = []
    temp_data2 = []
    temp_data3 = []
    temp_data4 = []
    pressure_data = []

    with open(csv_filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)    # skip header 
        for row in reader:
            tt.append(float(row[0])) 
            temp_data0.append(float(row[1])) 
            temp_data1.append(float(row[2])) 
            temp_data2.append(float(row[3])) 
            temp_data3.append(float(row[4])) 
            temp_data4.append(float(row[5])) 
            pressure_data.append(float(row[6])) 

    fig, ax1 = plt.subplots()
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('Temperature ()')
    ax1.plot(tt, temp_data0, label='Channel 1')
    ax1.plot(tt, temp_data1, label='Channel 2')
    ax1.plot(tt, temp_data2, label='Channel 3')
    ax1.plot(tt, temp_data3, label='Channel 4')
    ax1.plot(tt, temp_data4, label='Channel 5')
    ax1.legend()
    # ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    ax2.set_ylabel('Pressure (unit)') 
    ax2.plot(tt, pressure_data, label='Pressure')
    # ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout() 
    fig.savefig(csv_filename[:-4])

if __name__ == "__main__":
    record_thread = Thread(target=record_data)
    record_thread.start()

    app.debug = False
    app.run(host="0.0.0.0", port=70)
