import os
import glob
import datetime
import shutil
#list_of_files = glob.glob(r'D:\CREWS_TV\operational_TV_v1\runs\*') 
#latest_file2 = min(list_of_files, key=os.path.getctime)

dirname=r'D:\CREWS_TV\operational_TV_v1\runs'
for filename in os.listdir(dirname):
    latest_file=filename
    year = latest_file[:4]
    month = latest_file[4:6]
    day = latest_file[6:8]
    dt = datetime.datetime.strptime(year+'-'+month+'-'+day, '%Y-%m-%d')
    today = datetime.datetime.today()
    diff = abs((today - dt).days)
    if int(diff) > 70:
        remove_name = 'D:\\CREWS_TV\\operational_TV_v1\\runs\\'+filename
        #print(remove_name)
        print('removing..')
        shutil.rmtree(remove_name, ignore_errors=True)