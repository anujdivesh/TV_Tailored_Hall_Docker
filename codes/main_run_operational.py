# -*- coding: utf-8 -*-
"""
Created on Sat Jun 12 18:16:18 2021

@author: moritzw
This is the main script to run the forecast
"""

import datetime as dt
from datetime import timedelta
import os
import shutil
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import sys
import step1_download_NCEP as step1
import step2_download_CMEMS as step2
import step3_gen_tide_TPOX8 as step3
import step4_make_wave_forcing as step4
import step5_make_wind_forcing as step5
import step6_parallelize_run as step6
import step10_download_all_regional_data as step_10
import step11_read_and_plot_all_regional_data as step_11
import step12_forecast_pts as step_12
#####################################
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

ROOT_DIR = '/Tailored'

def list_available_runs(url):
    session = requests.Session()
    retry = Retry(connect=5, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount(url, adapter)

    try:
        req = session.get(url).text
        session.close() 
        soup = BeautifulSoup(req, 'html.parser')     
        x = (soup.find_all('a'))
        runs = []
        for i in x:
            file_name = i.extract().get_text()
            runs.append(int(file_name))
    except:
        
        runs = []
        print('Keep working on making the dowinloading process more robust')
        
      
    return(runs)



def delete_ndaysbefore(now,ndays):
    folder_name=ROOT_DIR+'/runs/'
    flist = os.listdir(folder_name)
    for d in flist:
        rundate=dt.datetime.strptime(d+'0000',"%Y%m%d%H%M%S")
        if rundate<now-timedelta(ndays):
            shutil.rmtree(ROOT_DIR+'/runs/'+ d)
    return()

###############################################################################


if __name__ == "__main__":
    #- Find the latest available run in nomads.ncep.noaa.gov
    now = dt.datetime.utcnow()
    url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfswave.pl?dir=%2Fgfs.' + now.strftime("%Y") + now.strftime("%m") + now.strftime("%d")
    runs = list_available_runs(url)
    if len(runs)==0:
        now = dt.datetime.utcnow()-timedelta(1)
        url = 'https://nomads.ncep.noaa.gov/cgi-bin/filter_gfswave.pl?dir=%2Fgfs.' + now.strftime("%Y") + now.strftime("%m") + now.strftime("%d")
        runs = list_available_runs(url)
    
    #- Define the run to be used
    runs=sorted(runs)
    now = now.replace(hour=runs[-1],minute=0,second=0,microsecond=0)
    #now = dt.datetime(2024,4,28,18)
    
    
    # delete previous runs older than 14 days
    try:
        delete_ndaysbefore(now,5)
    except Exception as e:
        print(e)

    #now = dt.datetime(2024,4,28,18) 
    
    step1.download_NCEP(now)
    step2.download_CNEMS(now)
    step3.gen_tide(now,"tailored_report_config.json")
    step4.make_waves(now)
    step5.make_winds(now)
    step6.par_run(now)
    step_10.download_NCEP(now)
    step_11.plot_winds_and_MSLP(now)
    step_12.hallsTailoredForecast(now,"tailored_report_config.json")
    
