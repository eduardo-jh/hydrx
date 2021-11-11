# -*- coding: utf-8 -*-
"""
Plot of the daily precipitation for Tucson AZ, during 2021
ATMO555 Assigment 9 - Nov 6, 2021

Created on Wed Nov 10 17:26:48 2021
@author: eduardo
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
sys.path.insert(0, '../src/')
from weather import WeatherData

def plot_max_precip(x, y, **kwargs):
    """ Plot of the precipitation over the year and identify maximum value """
    _title = kwargs.get('title', 'This is the title')
    _xlabel = kwargs.get('xlabel', 'x')
    _ylabel = kwargs.get('ylabel', 'y')
    _filename = kwargs.get('filename', '')
    
    # Create a figure and the scatter plot
    plt.figure(figsize=(12,8))
    # plt.scatter(x, y, marker='+', color='black')
    plt.plot(y, 'b-')
    plt.xlim((0, len(y)))
    plt.ylim((0, np.ceil(y.max())))
    
    # Mark on the max value
    max_idx = np.where(y == y.max())  # Index of the maximum value
    xy = x[max_idx[0]], y[max_idx[0]]
    label = '({0}, {1})'.format(xy[0].values[0], xy[1].values[0])
    
    # Substract 1 to DOY, due to 0-indexing
    plt.plot(xy[0]-1, xy[1], 'go')
    xy_text = (x[max_idx[0]]-110, y[max_idx[0]]-2)
    plt.annotate(label, xy=xy, c='b', arrowprops=dict(arrowstyle="->",
                 connectionstyle="angle3"), xytext=xy_text)
    
    # Set titles
    plt.xlabel(_xlabel)
    plt.ylabel(_ylabel)
    plt.title(_title)
    plt.grid()
    
    # Save a image with the same name to the corresponding data
    if _filename != '':
        plt.savefig(_filename, dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()

# Retrieve data from Tucson weather station from Jan 1 to Nov 5, 2021
station = 'Tucson'
start_date = datetime(2021,1,1)
end_date = datetime(2021,11,5)
ws = WeatherData(station, start_date, 'daily')
ws.set_end_date(end_date)
ws.get_data()

# Select only precipitation
selection =  ['Year', 'DOY', 'Precipitation']
ws.select(selection)

# Plot daily precipitation and identify the maximum value
plot_max_precip(ws.data['DOY'][:], ws.data['Precipitation'][:], xlabel='DOY',
                ylabel='Precipitation [mm]',
                title='Daily precipitation for year 2021 in Tucson, Arizona',
                filename='daily_precip.png')

# Show max precipitation
max_idx = np.where(ws.data['Precipitation'] == ws.data['Precipitation'].max())
print('Max precip:', ws.data['Precipitation'][max_idx[0]].values[0], 'DOY: ', ws.data['DOY'][max_idx[0]].values[0])
