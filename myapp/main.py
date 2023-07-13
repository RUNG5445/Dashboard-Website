import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import numpy as np
import socket
from ftplib import FTP_TLS
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import datetime
import folium
import webbrowser
import os

def getfileFTP():
    # Set up connection details
    host = '188.166.217.51'
    port = 7021
    usr = 'tung'
    pwd = 'anundaJJ795'

    # Connect to FTP server
    ftp = FTP_TLS()
    ftp.connect(host, port)
    ftp.login(usr, pwd)

    # Navigate to the desired directory
    ftp.cwd("/BER/")

    # Get a list of all files in the directory
    files = ftp.nlst()

    # Sort the list by modification time (oldest to newest)
    files.sort(key=lambda x: ftp.sendcmd("MDTM " + x)[4:])

    # Print the list of files (for debugging purposes)
    print(files)

    # Download the most recently modified file
    latest_file = files[-1]
    with open(latest_file, "wb") as f:
        ftp.retrbinary(f"RETR {latest_file}", f.write)

    # Print the name of the downloaded file
    print(latest_file)

    # Close the FTP connection
    ftp.quit()
    return latest_file


def getdata(latest_file):
    # Open the file and read the data
    with open(latest_file, 'r') as file:
        data = file.read()

    # Split the data into individual JSON objects
    data_list = data.strip().split('\n')
    data_list = list(filter(lambda x: x != '\n' and x != '', data_list))
    print(data_list)
    # Initialize lists
    temp_list = []
    humi_list = []
    time_list = []
    lat_list = []
    lon_list = []
    date_list = []
    Batt_Lev_list = []
    MAC_list=[]
    
    # Define offset for timezone conversion
    offset = timedelta(hours=7)

    # Process each JSON object in the data list
    for item in data_list:
        # Load JSON data
        json_data = json.loads(item)

        # Extract data from the JSON object
    temp_list = []
    humi_list=[]
    mac_to_row = {}
    for item in data_list:
        # Load JSON data
        json_data = json.loads(item)

        # Loop through the keys in the dictionary and extract temperature data for MAC addresses
        for key in json_data.keys():
            if ":" in key:  # If the key contains a colon (":") character, it's a MAC address
                mac_address = key
                temp = json_data[key]["Temp"]
                humi = json_data[key]["Humi"]
                # If this is the first time we've seen this MAC address, add it to the temp_array
                if mac_address not in mac_to_row:
                    mac_to_row[mac_address] = len(temp_list)
                    MAC_list.append(mac_address)
                    temp_list.append([])
                    humi_list.append([])
                # Add the temperature to the appropriate row in temp_array
                row = mac_to_row[mac_address]
                temp_list[row].append(temp)
                humi_list[row].append(humi)

        # Print the temp_array
        lat_list.append(json_data['Lat'])
        lon_list.append(json_data['Lon'])
        Batt_Lev_list.append(json_data['Batt_Lev'])

        # Convert date and time to GMT+7 timezone
        date_str = json_data['Date']
        time_str = json_data['Time']
        if date_str.startswith("2023"):
            full_time = datetime.strptime(date_str + ' ' + time_str, '%Y/%m/%d %H:%M:%S')
        else:
            full_time = datetime.strptime(date_str + ' ' + time_str, '%y/%m/%d %H:%M:%S')
        full_time = full_time 
        date_str = (full_time.date()).strftime('%Y/%m/%d')
        time_str = (full_time.time()).strftime('%H:%M:%S')
        date_list.append(date_str)
        time_list.append(time_str)

        # Handle missing latitude/longitude values
        if lon_list[-1] is None:
            lon_list[-1] = lon_list[-2]
        if lat_list[-1] is None:
            lat_list[-1] = lat_list[-2]

    # Limit the data to the most recent 20 entries
    if len(date_list) > 20:
        start_index = len(date_list) - 20
        lat_list = lat_list[start_index:]
        lon_list = lon_list[start_index:]
        date_list = date_list[start_index:]
        Batt_Lev_list = Batt_Lev_list[start_index:]
        time_list = time_list[start_index:]
        for i in range(len(temp_list)):
            temp_list[i] = temp_list[i][-20:]
            humi_list[i] = humi_list[i][-20:]


    print("Date:  ", date_list)
    print("Time:  ", time_list)
    print("Temp:  ", temp_list)
    print("Humi:  ", humi_list)
    print("Lat:   ", lat_list)
    print("Lon:   ", lon_list)
    print("Batt:  ", Batt_Lev_list[0])

    return temp_list,humi_list,time_list,lat_list,lon_list,date_list,Batt_Lev_list,MAC_list

def getcenter(lat_list, lon_list):
    # Calculate the average temperature
    lat_sum = 0.0
    lat_count = 0
    for x in lat_list:
        try:
            lat_sum += float(x)
            lat_count += 1
        except ValueError:
            pass  # Skip over invalid values
    lat_avg = lat_sum / lat_count if lat_count > 0 else float('nan')
    lat_avg = "{:.4f}".format(lat_avg)  # Format the average temperature as a string with two decimal places

    # Calculate the average humidity
    lon_sum = 0.0
    lon_count = 0
    for x in lon_list:
        try:
            lon_sum += float(x)
            lon_count += 1
        except ValueError:
            pass  # Skip over invalid values
    lon_avg = lon_sum / lon_count if lon_count > 0 else float('nan')
    lon_avg = "{:.4f}".format(lon_avg)  # Format the average humidity as a string with two decimal places

    # Create a list with the latitude and longitude of the center point
    center = [lat_avg, lon_avg]

    # Print the center point for debugging
    print("Center = ",center)

    # Return the center point
    return center


    

def findavg(temp_list, humi_list):
    # Calculate the average temperature
    temp_sum = 0.0
    temp_count = 0
    for x in temp_list:
        try:
            temp_sum += float(x)
            temp_count += 1
        except ValueError:
            pass  # Skip over invalid values
    temp_avg = temp_sum / temp_count if temp_count > 0 else float('nan')
    temp_avg = "{:.2f}".format(temp_avg)  # Format the average temperature as a string with two decimal places

    # Calculate the average humidity
    humi_sum = 0.0
    humi_count = 0
    for x in humi_list:
        try:
            humi_sum += float(x)
            humi_count += 1
        except ValueError:
            pass  # Skip over invalid values
    humi_avg = humi_sum / humi_count if humi_count > 0 else float('nan')
    humi_avg = "{:.2f}".format(humi_avg)  # Format the average humidity as a string with two decimal places

    # Return the average temperature and humidity as a tuple
    return temp_avg, humi_avg

def getstrlist(lat_list,MAC_list,temp_list,humi_list,time_list):
    str_list=[]
    for i in range(len(lat_list)):
        str_log=""
        str_log+=f"Time {time_list[i]} (GMT +7) \n"
        for j in range(len(humi_list)):
            str_log+=f"Sensor {j+1} ({MAC_list[j]})\n"
            if temp_list[j][i] is None or temp_list[j][i] == '' or humi_list[j][i] is None or humi_list[j][i] == '':
                str_log+=f"Temp = N/A\nHumi = N/A\n"
            else:
                str_log+=f"Temp = {temp_list[j][i]} °C\n"
                str_log+=f"Humi = {humi_list[j][i]} %\n"
        str_list.append(str_log)
    return str_list