# -*- coding: utf-8 -*-
"""
Created on Fri May 28 15:41:44 2021

@author: antonioh
"""
import os
import datetime
import numpy as np
import numpy.matlib
import matplotlib
matplotlib.use('TkAgg',force=True)
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import matplotlib.dates as mdates
import netCDF4 as nc
from scipy.interpolate import interp1d

# import pyTMD.time
import pyTMD.io
import pyTMD.time
import pyTMD.predict
import pyTMD.tools
import pyTMD.utilities
import json


def read_tpo_csv(fpath):
    df = pd.read_csv(fpath)
    atoll = df['atoll'].tolist()
    tpo_lon = df['lon'].tolist()
    tpo_lat = df['lat'].tolist()
    return(atoll,tpo_lon,tpo_lat)


###############################################################################
def gen_tide(now,configfile):
    
    print('Generating tide from TPOX8 Global Tidal Model https://www.tpxo.net/global')
        
    f = open(configfile)
    data = json.load(f)
    location_pts_csv = data[0]['Tailored_Forecast']['forecast_locations_path']

    
    folder_tmp ='../tmp/' 
    tide_dir = '../extras/'
    # grid_file = os.path.join(tide_dir,'TPXO9.1','DATA','grid_tpxo9.nc')
    # model_file = os.path.join(tide_dir,'TPXO9.1','DATA','h_tpxo9.v1.nc')
    grid_file = os.path.join(tide_dir,'TPXO8','DATA','grid_tpxo8atlas_30')## check if we can go for a newer version, others models can be used:'GOT4.8','FES2014',...
    model_file = os.path.join(tide_dir,'TPXO8','DATA','hf.tpxo8_atlas_30')
    OTIS_version = 'TPXO8-atlas'
    OTIS_path = '../extras/TPXO8/DATA'
    
    model_format = 'OTIS'
    EPSG = '4326'
    TYPE = 'z'
    
    tpo_fpath = location_pts_csv
    atoll_list, tpo_lon_list, tpo_lat_list = read_tpo_csv(tpo_fpath)

    for atoll,tpo_lon,tpo_lat in zip(atoll_list, tpo_lon_list, tpo_lat_list):
        print("\n",atoll,tpo_lon,tpo_lat)
        
        ##LON,LAT
        LON = tpo_lon
        LAT = tpo_lat
        

        now1 = now - dt.timedelta(2)# NCEP needs at least 3 hours to upload their forecast from UTC00
        then = now1 + dt.timedelta(days=9.5,minutes=1)
        time_tide = mdates.drange(now1,then,dt.timedelta(minutes=1))
        time_tide_hourly = mdates.drange(now1,then,dt.timedelta(hours=1))
        date_time = pd.to_datetime(mdates.num2date(time_tide))
        date_time_hourly = pd.to_datetime(mdates.num2date(time_tide_hourly))

        #-- convert time from MJD to days relative to Jan 1, 1992 (48622 MJD)
        time_tmd=time_tide-mdates.date2num(np.datetime64('1992-01-01T00:00:00')) 
        # time_tmd_hourly=time_tide_hourly-mdates.date2num(np.datetime64('1992-01-01T00:00:00')) 
        # tide_time_TMD = pyTMD.time.convert_calendar_dates(date_time.year, date_time.month,
        #     date_time.day, date_time.hour, date_time.minute) # this function  produces exactly same values than the line begore
        model = pyTMD.io.model(OTIS_path).elevation(OTIS_version)
        #model = pyTMD.io.model(grid_file).elevation('TPXO8-atlas')
        DELTAT = np.zeros_like(time_tmd)

        amp,ph,D,c = pyTMD.io.OTIS.extract_constants(np.atleast_1d([LON]), np.atleast_1d([LAT]),model.grid_file, model.model_file,
            model.projection, type=model.type, method='spline', grid='OTIS')

        #amp,ph,D,c = extract_tidal_constants(np.array([LON]), np.array([LAT]),
        #    grid_file,model_file,EPSG,TYPE=TYPE,METHOD='spline',GRID=model_format)

        ####### Amlitude and phase can be stored to save a few seconds

        #deltat = np.zeros_like(time_tide)
        # deltat_hourly = np.zeros_like(time_tide_hourly)
        #-- calculate complex phase in radians for Euler's
        cph = -1j*ph*np.pi/180.0
        #-- calculate constituent oscillation
        hc = amp*np.exp(cph)

        #-- predict tidal elevations at time 1 and infer minor corrections
        #-- convert to centimeters
        #TIDE = predict_tidal_ts(time_tmd, hc, c,
        #    DELTAT=deltat, CORRECTIONS=model_format)*100.0
        #MINOR = infer_minor_corrections(time_tmd, hc, c,
        #    DELTAT=deltat, CORRECTIONS=model_format)
        #TIDE.data[:] += MINOR.data
#
        #f = interp1d(time_tide,TIDE)
        #TIDE_hourly = f(time_tide_hourly)

        TIDE = pyTMD.predict.time_series(time_tmd, hc, c,
        deltat=DELTAT, corrections=model.format)
        MINOR = pyTMD.predict.infer_minor(time_tmd, hc, c,
        deltat=DELTAT, corrections=model.format)
        TIDE.data[:] += MINOR.data[:]
        # convert to centimeters
        TIDE.data[:] *= 100.0
        f = interp1d(time_tide,TIDE)
        TIDE_hourly = f(time_tide_hourly)

        #print(len(TIDE.data))


        #-- Save netcdf with the 10 days tide forecast hourly 
        fn = folder_tmp  + ('tide_hourly_%s.nc' % atoll)
        try:
            os.remove(fn)
        except:
            print('The system cannot find the file specified, creating netcdf file')
        ds = nc.Dataset(fn, 'w', format='NETCDF4')
        time = ds.createDimension('time', None)
        times = ds.createVariable('time', 'f8', ('time',))
        times.units='hours since 1950-01-01 00:00:00'
        times.calendar='gregorian'
        # times_min = ds.createVariable('time_min', 'f4', ('time',))
        # times_min.units='hours since 1950-01-01 00:00:00'
        # times_min.calendar='gregorian'
        tide= ds.createVariable('tide', 'f4', ('time',))
        tide.units = 'cm'
        # tide_min= ds.createVariable('tide_min', 'f4', ('time',))
        # tide_min.units = 'cm'
        times[:]=[nc.date2num(x,units=times.units,calendar=times.calendar) for x in date_time_hourly]
        # time_or = nc.num2date(times,units=times.units,calendar=times.calendar)
        tide[:]=TIDE_hourly
        # times_min[:]=[nc.date2num(x,units=times.units,calendar=times.calendar) for x in date_time]
        # tide_min[:]=TIDE.data
        ds.close()
        print('1 hour tides stored as ' + fn)

        #-- Save  tide forecast in netcdf in 1 minute and one hour resolution 
        fn = folder_tmp  + ('tide_minute_%s.nc' % atoll)
        try:
            os.remove(fn)
        except:
            print('The system cannot find the file specified, creating netcdf file')
        ds = nc.Dataset(fn, 'w', format='NETCDF4')
        time = ds.createDimension('time', None)
        times = ds.createVariable('time', 'f8', ('time',))
        times.units='hours since 1950-01-01 00:00:00'
        times.calendar='gregorian'
        tide= ds.createVariable('tide', 'f4', ('time',))
        tide.units = 'cm'
        times[:]=[nc.date2num(x,units=times.units,calendar=times.calendar) for x in date_time]
        tide[:]=TIDE.data
        ds.close()

        print('1 minute tides stored as ' + fn)