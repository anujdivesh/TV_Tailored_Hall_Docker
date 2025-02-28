import os
from pathlib import Path
import shutil
import pandas as pd
import datetime
import xarray as xr
import numpy as np
import glob

def ingest2GUI(now):
# function to ingest results into GUI
    #Paths
    webSrvPath = 'C:/apache-tomcat-9.0.55/webapps/ROOT/ds_tv/'
    dirpath='D:/CREWS_TV/operational_TV_v1/runs/'
    realTimePath = 'C:/Users/test/Documents/Latest/'
    ingesterPath = 'C:/ingest/'
    baseUrl = 'http://192.168.0.207:8080/ds_kiri/inundation/'
    
    #Move nc files
    run_path = dirpath + now.strftime("%Y") + now.strftime("%m") + now.strftime("%d") + now.strftime("%H")
    dirname = Path(run_path)
    file_list = ['P1_Nanumea.nc', 'P2_Nanumanga.nc', 'P3_Niutao.nc','P4_Nui.nc', 'P5_Vaitupu.nc', 'P6_Nukufetau.nc','P7_Fongafale.nc', 'P8_Nukulaelae.nc', 'P9_Niulakita.nc','Tuvalu.nc']

    for x in file_list:
        print('copying '+x)
        shutil.copy(str(dirname)+'/results/'+x, 'C:/Users/test/Documents/Latest/'+x)
    
    #MOVE Inundation pngs
    dest = "C:/apache-tomcat-9.0.55/webapps/ROOT/ds_tv/Figures"
    source = "D:/CREWS_TV/operational_TV_v1/inundation/Figures"
    for file in glob.glob(os.path.join(source,"*.png")):
        shutil.copy2(file,dest)

    #CALC Inundation
    #CONFIG
    
    path_risk = "D:/CREWS_TV/operational_TV_v1/inundation/Flood_risk/"
    out_path = "C:/apache-tomcat-9.0.55/webapps/ROOT/ds_tv/"
    ipaddr = "192.168.0.207"
    locations = ["Nanumaga", "Niulakita", "Niutao", "Nanumea", "Nukufetau", "Funafuti", "Nui","Nukulaelae", "Vaitupu", "Funafutilagoon"]
    
    #INIT
    columnsTitles = ['lon','lat','Coastal Inundation Hazard Levels','Primary image']
    extension = 'csv'
    count = 0

    ##REMOVE OLD FILES
    try:
        os.remove(out_path+"temp.csv")
        os.remove(out_path+"final.csv")
    except:
        print("Cannot remove files")

    #START CALC
    for locate in locations:
        all_files = [i for i in glob.glob(path_risk+''+locate+'*.{}'.format(extension))]
        cols = ['lon', 'lat', 'Coastal Inundation Hazard Levels']

        result = pd.DataFrame()
        df = pd.DataFrame(columns=cols)
        for x in all_files:
            x_str = x.split("_")
            #m2 = x.split("/")
            vap = x_str[4]
            m2 = vap.split("\\")
            stati = m2[1]
            statsion_id = x_str[6]
            f1 = pd.read_csv(x, index_col=False,names=cols)
            f1["index"] = pd.NaT
            f1["sid"] = pd.NaT
            f1.at[0, 'index'] = count
            f1.at[0, 'sid'] = statsion_id
            f1["station"] = pd.NaT
            f1.at[0, 'station'] = stati
            frames = [result, f1]
            result = pd.concat(frames)
            count +=1
        
        
        result['Primary image'] = np.nan
        result.set_index("index", inplace = True)
        
        for idx, row in result.iterrows():
            x = int(row['sid'])
            result.loc[idx,'Primary image'] = 'http://'+ipaddr+':8080/ds_tv/Figures/'+str(row['station'])+'_t_'+str(row['sid'])+'_forecast.png'
            y = int(row['Coastal Inundation Hazard Levels'])
            riskVal = ""
            if y == 0:
                riskVal= "Low Risk"
            elif y ==1:
                riskVal= "Moderate Risk"
            elif y==2:
                riskVal="High Risk"
            result.loc[idx,'Coastal Inundation Hazard Levels'] = riskVal
        result = result.reindex(columns=columnsTitles)
        result.to_csv(out_path+'temp.csv', index=True, mode='a')
    #print(result)    

    #SAVING
    f2 = pd.read_csv(out_path+'temp.csv', index_col=False)
    
    final_df = f2[f2["index"].str.contains("index")==False]
    final_df.to_csv(out_path+'final.csv', index=False, mode='a')
    
    ##NEWWWW
    #
    
    df = pd.read_csv('C:/apache-tomcat-9.0.55/webapps/ROOT/ds_tv/final.csv')
    for index, row in df.iterrows():
        url= row['Primary image']
        split = url.split('/')
        url = split[2]
        new_add = '192.168.0.207'
        new_url = "http://"+new_add+":8080/ds_tv/Figures/"+split[5]   
        df.at[index, 'Primary image'] = new_url

    os.remove(out_path+"final.csv")
    df.to_csv(out_path+'final.csv', index=False, mode='a')
    
    print("Ingestion Successful")    
    return()    
#import datetime as dt
#now = dt.datetime(2024,3,25,18)
#ingest2GUI(now)