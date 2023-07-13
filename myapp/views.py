from django.shortcuts import render
from django.http import HttpResponse
from . import main

def index(request):
    # Initialize lists
    temp_avg_list = []
    humi_avg_list = []
    temp = []
    humi = []
    
    # Get data from FTP
    filefromftp = main.getfileFTP()
    (temp_list, humi_list, time_list, lat_list, lon_list, date_list, Batt_Lev_list, MAC_list) = main.getdata(filefromftp)
    
    # Calculate average temperature and humidity for each data set
    for i in range(len(temp_list)):
        temp_avg, humi_avg = main.findavg(temp_list[i], humi_list[i])
        temp_avg_list.append(temp_avg)
        humi_avg_list.append(humi_avg)
        
        # Get the last temperature and humidity data for each data set
        temp.append(temp_list[i][-1])
        humi.append(humi_list[i][-1])

    # Get latest battery level and update time
    Batt = Batt_Lev_list[-1]
    lastupdate = f"{date_list[-1]} {time_list[-1]}"
    
    # Get center coordinates of all locations
    center = main.getcenter(lat_list, lon_list)
    length = len(temp_list)
    
    # Generate a list of strings for each data set to display on the map
    strlist = main.getstrlist(lat_list, MAC_list, temp_list, humi_list,time_list)
    
    # Set context variables to be passed to the template
    context = {
        "temp": temp,
        "humi": humi,
        "tempavg": temp_avg_list,
        "humiavg": humi_avg_list,
        "Batt_Lev": Batt,
        "Time": lastupdate,
        "templist": temp_list,
        "timelist": time_list,
        "humilist": humi_list,
        "latlist": lat_list,
        "lonlist": lon_list,
        "center": center,
        "strlist": strlist,
        'range': range(length)
    }
    
    # Render the index template with the context variables
    return render(request, 'index.html', context)

def BER(request):
    # Render the BER template
    return render(request, 'BER.html')
