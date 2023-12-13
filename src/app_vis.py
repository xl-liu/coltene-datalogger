from flask import Flask, render_template, request, send_file, send_from_directory, jsonify
from dash import Dash, dcc, html, Input, Output
import time
import csv
import os
from threading import Thread
from smbus import SMBus
from i2c_lib.rtd_lib import tempADC
from i2c_lib.pijuice_lib import PiJuice
from datetime import datetime 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# import plotly.express as px
import sys
sys.path.insert(0, 'adafruit_ads1x15')
import i2c_lib.adafruit_ads1x15.ads1115 as ADS
from i2c_lib.adafruit_ads1x15.analog_in import AnalogIn
from i2c_lib.adafruit_ads1x15.ads1x15 import Mode

app = Flask(__name__)
recording = False  # Flag to control recording

# I2C setup
bus = SMBus(1)  # I2C bus
temp_adc = tempADC(bus, n_channels=5)   # temperature ADC hat 
pijuice = PiJuice(bus)  # pijuice board
pres_ads = ADS.ADS1115(bus, gain=2/3)   # adc for pressure sensor
pres_ads.mode = Mode.CONTINUOUS
pres_chan = AnalogIn(pres_ads, ADS.P0)
global io2_status
io2_status = 1

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

# data buffer for visualization 
DATA_RATE = 2   # Hz
WLEN = int(DATA_RATE * 25)  # 25 seconds of data
time_buffer = [0] * WLEN
temp_buffer0 = [0] * WLEN
temp_buffer1 = [0] * WLEN
temp_buffer2 = [0] * WLEN
temp_buffer3 = [0] * WLEN
temp_buffer4 = [0] * WLEN
pres_buffer = [0] * WLEN

# offset for temp sensors
TEMP_OFFSET = [0.64,  0.138,  0.17, -0.853, -1.188]

# CSV file setup
downloads_directory = "../logdata"

# Dash callback to plot live data 
@dash_app.callback(
    Output('temp-plot', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n_intervals):
    # Use the global lists to plot
    global time_buffer, temp_buffer0, temp_buffer1, temp_buffer2
    global temp_buffer3, temp_buffer4, pres_buffer
    
    # Create Plotly figure without Pandas
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_buffer,
                            y=temp_buffer0,
                            mode='lines',
                            name='Temperature Ch 1'))
    fig.add_trace(go.Scatter(x=time_buffer,
                            y=temp_buffer1,
                            mode='lines',
                            name='Temperature Ch 2'))
    fig.add_trace(go.Scatter(x=time_buffer,
                            y=temp_buffer2,
                            mode='lines',
                            name='Temperature Ch 3'))
    fig.add_trace(go.Scatter(x=time_buffer,
                            y=temp_buffer3,
                            mode='lines',
                            name='Temperature Ch 4'))
    fig.add_trace(go.Scatter(x=time_buffer,
                            y=temp_buffer4,
                            mode='lines',
                            name='Temperature Ch 5'))
    fig.update_layout(yaxis=dict(title='Temperature (°C)'))

    # plot the pressure
    fig.add_trace(go.Scatter(x=time_buffer, 
                             y=pres_buffer, 
                             mode='lines', 
                             name='Pressure', 
                             yaxis='y2'))
    fig.update_layout(yaxis2=dict(title='Pressure (mbar)', 
                                  overlaying='y', 
                                  side='right', 
                                  range=[0,4]))
    fig.update_layout(
        title='Live Data',
        xaxis=dict(title='Time (s)'),
        legend=dict(x=0, y=1, traceorder='normal'),
        font=dict(family='Helvetica, sans-serif', size=12)
    )

    return fig

def get_pi_status():
    pi_temp = os.popen("vcgencmd measure_temp").readline()
    # pi_temp = pi_temp.replace("temp=", "").strip()
    pi_temp = pi_temp[5:-3]
    pi_time = time.strftime("%Y-%m-%d %H:%M:%S")
    pi_space = get_available_space()
    return pi_temp, pi_time, pi_space

def get_battery_status():
    global io2_status

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

    # check the IO2 pin 
    io2_info = pijuice.status.GetIoDigitalInput(2)
    if io2_info['error'] == 'NO_ERROR':
        io2_status = io2_info['data']
    return battery_temp, battery_power, battery_faults, io2_status

def get_available_space():
    try:
        # stat = os.statvfs('/')  # Replace with the mount point of /dev/root if different
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
    battery_temp, battery_power, battery_faults, io2 = get_battery_status()
    dic = { 
        "temperature": temperature,
        "timestamp": timestamp,
        "available_space": avail_space,
        "recording": recording,  # Pass recording status to the client
        "battery_temp": battery_temp,
        "battery_power": battery_power,
        "battery_faults": battery_faults,
        "system_switch": io2_status
        }
    
    # turn off the pi if the system switch is off
    if not io2_status:
        pijuice.power.SetSystemPowerSwitch(0)
        pijuice.power.SetPowerOff(10)
        os.system("sudo shutdown -h now")
    return jsonify(dic)

@app.route("/download/<filename>")
def download_file(filename):
    # Serve files from the downloads directory
    return send_from_directory(downloads_directory, filename)

def record_data():
    global recording
    tt = 0
    while True:
        # timestamp used for logging
        now = datetime.now()
        timestamp = now.strftime('%H:%M:%S.%f')[:-3]

        # timestamp used for plotting
        time_buffer.append(tt)
        tt += 1. /  DATA_RATE
        time_buffer.pop(0)

        # read the temperature sensor
        temps = temp_adc.read_all_channels()
        temp_buffer0.append(temps[0] + TEMP_OFFSET[0])
        temp_buffer0.pop(0)
        temp_buffer1.append(temps[1] + TEMP_OFFSET[1])
        temp_buffer1.pop(0)
        temp_buffer2.append(temps[2] + TEMP_OFFSET[2])
        temp_buffer2.pop(0)        
        temp_buffer3.append(temps[3] + TEMP_OFFSET[3])
        temp_buffer3.pop(0)       
        temp_buffer4.append(temps[4] + TEMP_OFFSET[4])
        temp_buffer4.pop(0)

        # read the pressure sensor
        pressure = pres_chan.pressure
        pres_buffer.append(pressure)
        pres_buffer.pop(0)

        # save the data to csv file
        if recording:
            with open(csv_filename, "a", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([timestamp] + temps + [pressure])  # 0 for pressure sensor for now
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
    tt = []
    temp_data0 = []
    temp_data1 = []
    temp_data2 = []
    temp_data3 = []
    temp_data4 = []
    pressure_data = []

    # read the csv file
    with open(csv_filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)    # skip header 
        for row in reader:
            tt.append(row[0])
            temp_data0.append(float(row[1])) 
            temp_data1.append(float(row[2])) 
            temp_data2.append(float(row[3])) 
            temp_data3.append(float(row[4])) 
            temp_data4.append(float(row[5])) 
            # pressure_data.append(float(row[6])) 
            pressure_data.append(0) 

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=tt, y=temp_data0, name="Channel 1"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=tt, y=temp_data1, name="Channel 2"),
        secondary_y=False,
    )    
    fig.add_trace(
        go.Scatter(x=tt, y=temp_data2, name="Channel 3"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=tt, y=temp_data3, name="Channel 4"),
        secondary_y=False,
    )    
    fig.add_trace(
        go.Scatter(x=tt, y=temp_data4, name="Channel 5"),
        secondary_y=False,
    )   
    fig.add_trace(
        go.Scatter(x=tt, y=pressure_data, name="Pressure"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="Logdata"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Time (s)")
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=tt[::4]
        )
    )
    # Set y-axes titles
    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
    fig.update_yaxes(title_text="Pressure (mbar)", secondary_y=True)

    # save the figure
    fig.write_html(csv_filename[:-4] + ".html")

if __name__ == "__main__":
    record_thread = Thread(target=record_data)
    record_thread.start()

    app.debug = False
    app.run(host="0.0.0.0", port=70)
