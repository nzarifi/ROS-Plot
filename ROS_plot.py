# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 16:44:14 2020

@author: NZarifi
"""



import pandas as pd
import re
import statistics as st
import os
import numpy as np
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
import glob
import sys
#import pkg_resources.py2_warn  #pyinstaller --hidden-import pkg_resources.py2_warn example.py



if len(sys.argv) != 2:
    print("put the data directory where the ROS*.log exist")
    print("For example: python script.py  " + "C:\Temp\Log\80-000038")
    sys.exit()

data_dir = sys.argv[1]
os.chdir(data_dir)
data_directory = os.path.join(data_dir)
log_list = glob.glob(os.path.join(data_directory, '*.log'))
if len(log_list) == 0:
    print('There is no *.log file in ' + data_dir)
    sys.exit(1)


#name=[os.path.basename(x) for x in glob.glob(os.path.join(data_directory, '*.log'))]

for n in glob.glob(os.path.join(data_directory, '*.log'),recursive=True): ## first get full file name with directores using for loop
    name = os.path.basename(n)                 ## Now get the file name with os.path.basename
    name='./'+name


f = open(name, "r")
T1 = []
T2 = []
T3 = []
time = []

for l in f:
    if l.find('Thermistor') == -1:
        continue
    if l.find('Thermistor T1') != -1:
        #time.append(l[10:17])
        time.append(l[0:17])
        start = l.find('Thermistor T1') + 14
        t1 = l[start:start + 2]
        T1.append(t1)
    elif l.find('Thermistor T2') != -1:
        start = l.find('Thermistor T2') + 14
        t2 = l[start:start + 2]
        T2.append(t2)
    elif l.find('Thermistor T3') != -1:
        start = l.find('Thermistor T3') + 14
        t3 = l[start:start + 2]
        T3.append(t3)

Pilot_V =[]
EWS_V=[]
f = open(name, "r")
for l in f:
    if l.find('Pilot V:') != -1:
        start = l.find('Pilot V:')+9
        P = l[start:start + 6]
        Pilot_V.append(P)
    if l.find('EWS V:') !=-1:
        start = l.find('EWS V:')+7
        E=l[start:start + 6]
        EWS_V.append(E)

I_time=[]
I_list=[]
soc_list=[]
f = open(name, "r")
for l in f:
    if l.find('ABCCommandValue')!=-1:
        I_list.append(l.split()[-1])
        I_time.append(l[0:17])
    if l.find('Battery_SOC')!=-1:
        soc_list.append(l[-11:-6])

soc_list=[a.replace(':','') for a in soc_list] #this correction is for soc below 10 which shown like non-integer ': 5.0'

SOC ='SOC_level: Start/Max/End: '+ soc_list[0] + '/' + max(soc_list) + '/' + soc_list[-1] 

#I_list=[w[:5] for w in I_list]
#I_list.insert(0,'current value:')
max_I=('Max_I: '+max(I_list))[:-5]
min_I=('Min_I: '+min(I_list))[:-5]

dic = {'Time': time, 'Thermistor_T1': T1, 'Thermistor_T2': T2, 'Thermistor_T3': T3, 'Pilot_V':Pilot_V, 'EWS_V':EWS_V}
data = pd.DataFrame(dic)


data=data.astype({"Thermistor_T1": float, "Thermistor_T2": float, "Thermistor_T3": float, "Pilot_V": float,"EWS_V": float })

data.Time=pd.to_datetime(data.Time, format="%m/%d/%y %H:%M:%S")
#data.dtypes

y_max=data.loc[:, ['Thermistor_T1', 'Thermistor_T2','Thermistor_T3' ]].max().max()
y_min=data.loc[:, ['Thermistor_T1', 'Thermistor_T2','Thermistor_T3' ]].min().min()

plt.plot(data.Time,data['Thermistor_T1'])
plt.plot(data.Time,data['Thermistor_T2'])
plt.plot(data.Time,data['Thermistor_T3'])
plt.plot(data.Time,data['Pilot_V'])
plt.plot(data.Time,data['EWS_V'])
plt.legend(["T1(+)_lug", "T2(-)_lug","T3(-)_contactor",'Pilot','EWS'], loc='best')
plt.title('Thermistor on Contactors, Pilot, EWS, Current changes are dashed lines', loc='left', fontsize=10)
xformatter = mdates.DateFormatter('%H:%M:%S')
plt.gcf().axes[0].xaxis.set_major_formatter(xformatter)
plt.vlines(pd.to_datetime(I_time), -5, y_max+5, linestyles ="dashed", colors ="k")
plt.xticks(rotation=45)
plt.xlabel('Time')
plt.ylabel('Temperature (C)')
plt.text(pd.to_datetime(I_time[len(I_time)-1]), y_min-10, max_I, fontsize=10, ha='right')
plt.text(pd.to_datetime(I_time[len(I_time)-1]), y_min-20, min_I, fontsize=10, ha='right')
plt.text(pd.to_datetime(I_time[len(I_time)-1]), -7   , SOC, fontsize=10, ha='right')
plt.tight_layout()
plt.savefig('Thermistor_Pilot_EWS.png',dpi=200,bbox_inches='tight')
