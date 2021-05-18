#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
weather.py
Data retrieval from automatic weather stations

Created on Sat Mar  6 15:42:10 2021
@author: eduardo
"""
import requests
import urllib.request, urllib.error
import pandas as pd
import numpy as np
from datetime import timedelta, datetime

class WeatherData:

    def __init__(self, station, start_date, timestep):
        self.ID_PLACES = 2
        self.NO_DATA = 999
        self.station = station
        self.start_date = start_date.date()
        self.end_date = datetime.today().date()
        assert self.end_date > self.start_date, 'Start date cannot be after end date'
        self.timestep = timestep
        
        self.station_id = '--'
        self.period = 1  # initialize with a period of 1 day
        self.years = []
        self.data = pd.DataFrame()
        
        self.locations = self.read_values('../doc/AZ_locations')
        self.weather_station_id()
        # Check whether 'daily' or 'hourly' data
        self.headerfile = '../doc/vars_daily_short'  if self.timestep == 'daily' else '../doc/vars_hourly'
        self.dtype = 'rd' if self.timestep == 'daily' else 'rh'  # rh: raw daily, rh: raw hourly
        self.headers = self.read_values(self.headerfile)
        print('Creating weather data for {0}... successful!'.format(self.station))
    
    def __str__(self):
        text = '\nWEATHER OBJECT\n'
        text += 'Station:       {0}\n'.format(self.station)
        text += 'Station ID:    {0}\n'.format(self.station_id)
        text += 'Start date:    {0}\n'.format(self.start_date)
        text += 'End date:      {0}\n'.format(self.end_date)
        text += 'Time step:     {0}\n'.format(self.timestep)
        text += 'Data type:     {0}\n'.format(self.dtype)
        text += 'Period:        {0} [days]\n'.format(self.period)
        text += 'Data cols:     {0}\n'.format(len(self.data))
        text += 'Data rows:     {0}\n'.format(len(self.data.columns))
        text += 'Data elements: {0}\n'.format(self.data.size)
        return text
    
    def set_period(self, period):
        """ Sets a period of time in days to calculate the end date """
        self.period = period
        
    def get_period(self):
        """ Gets the period of time in days between start and end dates """
        return self.period
    
    def set_end_date(self, end_date):
        """ Sets a 'datetime' object as end date"""
        self.end_date = end_date.date()
        
    def get_end_date(self):
        """ Returns the end date as 'datetime' object"""
        return self.end_date

    def read_values(self, filename):
        """ Get the values from a text file, one value per line
        
        filename: str, the text file to read
        returns: list, with one line in text file is one element of the list
        """
        values = []
        with open(filename, 'r') as f:
            # Read the values and remove any trailing hidden characters
            values = [value.strip() for value in f.readlines()]
        return values

    def weather_station_id(self):
        """ Sets a two-digit ID using the name of the weather station """
        if self.station in self.locations:
            self.station_id = str(self.locations.index(self.station) + 1).zfill(self.ID_PLACES)

    def create_url(self, station_id, year, dtype):
        """ Creates the URL of the website to retrieve weather data """
        assert len(station_id) == 2, "Incorrect weather station ID"
        assert dtype == 'rh' or dtype == 'rd', "Incorrect raw data type"
        # url: two-digit station, two-digit year, and two-char type: raw daily 'rd'
        yr = str(year)[-self.ID_PLACES:]
        self.url = 'https://cals.arizona.edu/azmet/data/' + station_id + yr + dtype + '.txt'

    def get_data_url(self):
        """ Retrieves the weather station data from online website """
        try:
            headers = {"User-Agent":"Mozilla/5.0"}
            response = requests.get(self.url, headers=headers)  # Connect to the URL
            ret_data = urllib.request.urlopen(self.url)  # Retrieve data from the URL
    
            # Print the connection status
            # for key in response.headers.keys():
            #     print("  {0}: {1}".format(key, response.headers[key]))
            print("  Response status code: {0}".format(response.status_code))
    
            # Save all the data from the website in a list
            data = []
            for line in ret_data:
                data.append(line)
    
        except urllib.error.URLError as e:
            print("  Error URL:", e.reason)
        except urllib.error.HTTPError as e:
            print("  Error HTTP:", e.code)
        return data

    def get_data_period(self):
        """ Gets the weather station data using a period after start date """
        assert self.period > 0, "Period should be at least 1 day"
        self.end_date = self.start_date + timedelta(self.period)
        self.get_data()  # Populates the Data Frame
        
    def get_data(self):
        """ Gets the weather station data using the start and end dates """
        self.years = [x for x in range(self.start_date.year, self.end_date.year + 1)]
        period = self.end_date - self.start_date
        self.period = period.days
        # Retrieve the data for every year in the range requested
        data = []  # One Data Frame per year
        for year in self.years:
            self.create_url(self.station_id, year, self.dtype)
            data.append(pd.read_csv(self.url, names=self.headers))
            print('Retrieving data for {0} ({1})... successful!'.format(year, self.url))
        # Concatenate the list of Data Frames into a single one
        self.data = pd.concat(data, ignore_index=True, sort=False)
        # Select only the data between the start date and end date
        self.trim_data()
        
    def trim_data(self):
        """ Trim the data to match period between start and end dates
        WARNING! Assumes there is a column named 'DOY' with day of the year """
        # Get day of year (DOY) for start and end dates
        start_doy = self.start_date.timetuple().tm_yday
        end_doy = self.end_date.timetuple().tm_yday
        
        # Drop data before start date
        self.data.drop(self.data[(self.data['Year'] == self.start_date.year) & (self.data['DOY'] < start_doy)].index, inplace=True)
        # Drop data after end date
        self.data.drop(self.data[(self.data['Year'] == self.end_date.year) & (self.data['DOY'] >= end_doy)].index, inplace=True)
        self.data = self.data.reset_index(drop=True)
    
    def select(self, selection):
        """ Select only the columns of the Data Frame especified in the selection list """
        assert type(selection) is list, 'Selection should be a list'
        for header in selection:
                assert header in self.headers, "Header '{0}' is not a column name in DataFrame".format(header)
        self.data = self.data[selection]
        
    def add_date(self, colname='Date'):
        """ Adds a Date column to the weather data DataFrame
        colname: str, the name of the column to add
        """
        assert type(colname) is str, 'The column name should be a string'
        self.data[colname] = [self.start_date + timedelta(i) for i in range(self.period)]
        self.headers = self.data.columns.values  # update headers
    
    def fill_missing(self):
        """ Replace all NO_DATA values with a interpolated value """
        replaced = 0
        for col in self.data.columns:
            if (self.data[col] == self.NO_DATA).any():
                self.data[col].replace(self.NO_DATA, np.nan, inplace = True)
                self.data[col].interpolate(inplace = True)
                replaced += 1
        if replaced == 0:
            print('No missing values found!')
        else:
            print('{0} missing values were filled successfully!'.format(replaced))
        
    def daily_averages(self):
        self.add_date()
        self.data.set_index('Date', inplace=True)
        annual_data = []
        for year in self.years:
            annual_data.append(self.data.loc[self.data['Year'] == year])
            # print(self.data.loc[self.data['Year'] == year])
        self.headers = self.data.columns.values
        print(self.headers)
        
        SR = []
        # dates = annual_data[0]['Date']
        dates = annual_data[0].index
        print(dates)
        
        for date in dates:
            i = 0
            for annual in annual_data:
                # print(self.years[i], len(annual))
                date_ = datetime(self.years[i], date.month, date.day).date() # date
                
                row = annual.loc[date_]
                # print(date, date_, row['SR'])
        
                i += 1
        #         # print('Before:')
        #         print(annual)
        #         # print('Columns: ', annual.columns)
        #         # annual.set_index('Date', inplace=True)
        #         # print('After:')
        #         # print(annual)
        #         row = annual.loc[date_]
        #         print(row['SR'])
        # #         SR.append(row['SR'])
        # #         i += 1
        # # print(SR)


class BlanneyCriddle:
    def __init__(self, lat, months, north=True):
        assert lat >= 0 and lat <= 90, 'Incorrect latitude value [0-90]'
        self.lat = lat
        self.north = north
        self.months = months
        # Set column name according to Northern or Southern hemisphere
        self.hemisphere = 'North' if self.north else 'South'
    
    def read_daytime_hours(self, filename='../doc/daytime_mean_hours.csv'):
        """ Mean Daily Percentage of Annual Daytime Hours, p, by month for different Latitudes """
        self.daytime_hours_table = pd.read_csv(filename)
    
    def linterpol(self, x0, y0, x1, y1, x):
        """ Linear interpolation """
        return y0 + (x - x0) * ((y1-y0) / (x1-x0))
    
    def daytime_hours(self, colname='p'):
        """ Mean Daily Percentage of Annual Daytime Hours, p, by month
        for the especified latitude
        colname: str, the name of the column to add """
        assert type(colname) is str, 'The column name should be a string'
        self.read_daytime_hours()
        # Column headers of the daytime houts table are latitudes in degrees
        latitudes = [int(x) for x in self.daytime_hours_table.columns.values[2:]]
        # Find the values between which latitude lies, x0 and x1
        x0 = latitudes[-1]
        x1 = latitudes[-1]
        for i in range(len(latitudes) - 1):
            if self.lat >= latitudes[i] and self.lat < latitudes[i+1]:
                x0 = latitudes[i]
                x1 = latitudes[i+1]

        row_months = self.daytime_hours_table[self.hemisphere]
        # Select rows for especified months, the percentage of daytime hours
        # will be the same in the whole month
        daytime_per_month = self.daytime_hours_table.loc[row_months.isin(self.months)]
        # Select the latitude columns
        if x0 == x1:
            # Any value of latitude >= 60 use the last column
            daytime_per_month = daytime_per_month[[self.hemisphere, str(x0)]]
            # Rename to 'p' the column with values corresponding to latiude
            daytime_per_month.rename(columns={str(x0):colname}, inplace=True)
        else:
            # Otherwise, interpolate between columns x0 and x1
            interp = []
            for month in self.months:
                y0 = float(daytime_per_month.loc[daytime_per_month[self.hemisphere] == month][str(x0)])
                y1 = float(daytime_per_month.loc[daytime_per_month[self.hemisphere] == month][str(x1)])
                # Interpolate for the latitude, add all the values to a list
                interp.append(self.linterpol(x0, y0, x1, y1, self.lat))
            daytime_per_month = daytime_per_month[[self.hemisphere, str(x0), str(x1)]]
            # Add a column named 'p' with the values corresponding to latiude
            daytime_per_month[colname] = interp
        
        self.daytime_per_month = daytime_per_month.reset_index(drop=True)

if __name__ == '__main__':

    station = 'Tucson'
    year = 2018
    month = 12
    day = 1
    duration = 120
    
    # # Test for a preset duration
    # ws = WeatherData(station, datetime(year,month,day), 'daily')
    # ws.set_period(duration)
    # ws.get_data_period()
    
    # print(ws)
    
    # Get annual data and compute daily averages
    start_date = datetime(2003,1,1)
    end_date = datetime(2020,12,31)
    ws = WeatherData(station, start_date, 'daily')
    ws.set_end_date(end_date)
    ws.get_data()
    
    selection =  ['Year', 'DOY', 'SR', 'TMean', 'RHMean', 'ET0', 'ET0PM']
    ws.select(selection)
    ws.fill_missing()  # fill missing data
    # ws.daily_averages()
    
    # lat = 32.735307
    # months = [11, 12, 1, 2, 3]
    # # lon = -114.530297
    # bc = BlanneyCriddle(lat, months, north=False)
    # bc.daytime_hours()
    
    