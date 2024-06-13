# -*- coding: utf-8 -*-
"""
Created on Thu May 20 17:51:04 2021

@author: antonioh
"""
import datetime as dt
from matplotlib import path
import os, shutil
from adcircpy import AdcircMesh
import matplotlib.pyplot as plt
# from AdcircPy import read_mesh
import numpy as np
from subprocess import Popen, PIPE

def execute(cmd):
    popen = Popen(cmd, stdout=PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return()

def startenddate(start_str,end_str):
    fmt = '%Y%m%d%H'
    dt1 = dt.datetime.strptime(start_str, fmt)
    dt2 = dt.datetime.strptime(end_str, fmt)
    dt1f = dt1.strftime('%Y%m%d.%H%M%S')
    dt2f = dt2.strftime('%Y%m%d.%H%M%S')
    return(dt1f,dt2f)


def main_fort26(folder_name,t1,t2,pointlist):
    # directory = os.getcwd()
    # fpath = os.path.join(directory,folder_name)
    # flist = os.listdir(folder_name)

    pmesh = AdcircMesh.open(folder_name+"/fort.14",crs=4326)
    #pmesh = read_mesh(folder_name+"/fort.14")
    # px = pmesh.x
    # py = pmesh.y
    pbnd = pmesh.ocean_boundaries
    pbnd_val = pbnd.indexes[0]
    pbnd_val = np.array(pbnd_val)+1
    # pbnd_x = px[pbnd_val]
    # pbnd_y = py[pbnd_val]
	
    bnd_txt = []
    for pf14id in range(1,len(pbnd_val)-1):
        s = ("BOUN SEGMENT IJ %s VAR FILE 0 'Pto_%s.sp2' 1, &\n" % (pbnd_val[pf14id] ,pbnd_val[pf14id]))
        bnd_txt.append(s)

    bnd_txt[-1] = bnd_txt[-1][:-4].strip()
    bnd_str = ''.join(bnd_txt)

    # Read in the file
    with open(folder_name+"/fort.26", 'r') as f:
        filedata = f.read()

    # Replace the target string
    filedata = filedata.replace('$%%BOUND_COMMAND%%', bnd_str)
    filedata = filedata.replace('%%BOUND_STARTDATE%%', t1)
    filedata = filedata.replace('%%BOUND_ENDDATE%%', t2)
	
    points_txt = []
    table_txt = []
    spect_txt = []

    for npp in range(len(pointlist[:,1])):

                   
        po = ("POINTS 'Pto_%s' %s %s \n" % (npp+1,pointlist[npp,0],pointlist[npp,1]))
        points_txt.append(po)
        
        tb=("TABLE  'Pto_%s' HEAD   '../Pto_%s.tab' TIME DEP HS HSWELL RTP PER DIR WIND OUT %s 1 HR \n" % (npp+1,npp+1,t1))
        table_txt.append(tb)
        
        sp=("SPECOUT 'Pto_%s' SPEC2D ABS '../Pto_%s.spec' OUT %s 1 HR \n" % (npp+1,npp+1,t1))
        spect_txt.append(sp)


    # Replace the target string
    filedata = filedata.replace('$%%POINTS%%', ''.join(points_txt))
    filedata = filedata.replace('$%%TABLE%%', ''.join(table_txt))
    filedata = filedata.replace('$%%SPECT%%', ''.join(spect_txt))

    
    # Write the file out again
    with open(folder_name+"/swanconf.swn", 'w') as fout:
        fout.write(filedata)

############################################################################################################################################

def par_run(now):
    out_name='../runs/' + now.strftime("%Y") + now.strftime("%m") + now.strftime("%d") + now.strftime("%H")  +'/'
    # cygfolder = '/cygdrive/d/Projects_SPC/Kiribati/CREWS-KI-Forecast-System-main/operational_v1/runs/' + now.strftime("%Y") + now.strftime("%m") + now.strftime("%d") +  now.strftime("%H")  +'/'
    ini = now - dt.timedelta(days=2)
    start_str = ini.strftime("%Y") + ini.strftime("%m") + ini.strftime("%d") + ini.strftime("%H")
    end = ini + dt.timedelta(days=9.5)
    end_str = end.strftime("%Y") + end.strftime("%m") + end.strftime("%d") + end.strftime("%H")

    t1,t2 = startenddate(start_str,end_str)

    source_dir ='../common'
    file_names = os.listdir(source_dir)
    for file_name in file_names:
        shutil.copy(os.path.join(source_dir, file_name), out_name)

   
    pointlist=np.array([[179.2139623911262, -8.522669489113921],[179.0812094845414, -8.652164074276669],[179.0000481854969, -8.513060353962492],[179.1357025559911, -8.411012345526808]])

    main_fort26(out_name,t1,t2,pointlist)


    print(out_name)

    os.system('rm %s' % out_name + '/swaninit')
    
    prompt = 'cd ' + out_name + '; export PATH="/Tailored/executables/:${PATH}"' + ';swanrun -input swanconf -omp 16'
    os.system(prompt)
   
 
    print('finished running')
    try:
        os.system('taskkill /F /IM swan.exe')
    except:
        print('SWAN run finished succesfully')

##############################################################################
