import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import csv 
import os
import glob

def plot_logdata(filename):
    tt = []
    temp_data0 = []
    temp_data1 = []
    temp_data2 = []
    temp_data3 = []
    temp_data4 = []
    pressure_data = []

    # read the csv file
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)    # skip header 
        for row in reader:
            tt.append(row[0])
            temp_data0.append(float(row[1])) 
            temp_data1.append(float(row[2])) 
            temp_data2.append(float(row[3])) 
            temp_data3.append(float(row[4])) 
            temp_data4.append(float(row[5])) 
            pressure_data.append(float(row[6])) 
            # pressure_data.append(0) 

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
    step_size = int(len(tt) / 20)
    fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=tt[::step_size]
        )
    )
    # Set y-axes titles
    fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
    fig.update_yaxes(title_text="Pressure (mbar)", secondary_y=True)
    # fig.update_yaxes(title_text="<b>secondary</b> yaxis title", secondary_y=True)

    # save the figure
    fig.write_html(filename[:-4] + ".html")

if __name__ == "__main__":
    list_of_files = glob.glob('logdata/*.csv') 
    latest_file = max(list_of_files, key=os.path.getctime)
    # print(latest_file)
    latest_file = 'logdata/2023-11-03_01-47-09.csv'
    plot_logdata(latest_file)
    