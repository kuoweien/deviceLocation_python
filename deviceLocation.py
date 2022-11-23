#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 11:55:02 2021

@author: weien
"""

import sys
import requests
import re
import numpy as np
import pandas as pd
import datetime


def getRawList(server,XID,updateurl): 
    try: 
        if not updateurl:
            urlstart="http://"+server+".ym.edu.tw/"+XID       
        if updateurl:
            urlstart="http://"+server+".ym.edu.tw/"+XID+'/'+XID+"_"+updateurl+'.txt'
            
        r = requests.get(urlstart)
        rawtxt=r.text
        rawtxt=rawtxt.replace("/","-")
        rawlist=rawtxt.split("\r\n")
        return rawlist
    
    except:
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))   
    
    
#查看是否有新上傳資料，updatetime_url為最新的上傳時間連結，帶入def getRawList的dateurl


#找今日是否有上傳資料 output updatetime
def getNewUpdatetime(server,uploadXID):
    try:
        update_rawlist=getRawList(server,uploadXID,'')
        for i in range(len(update_rawlist)):
            templist=update_rawlist[i].split("  ")   
            if 'txt' not in templist[2]:
                continue
            if 'txt' and '2021' in templist[2]:
                newupdatetime_str=templist[0]
                updatetime_url=(templist[2].split('>')[1]).split('<')[0]
                break
    except:
        print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))

    return newupdatetime_str,updatetime_url


# 找BLE連接狀況，並放進dict
def getUploadStateDict(rawdata):
    data=[]
    for i in range(len(rawdata)):
        if '0300005C' in rawdata[i]:
            if 'BLE disconnected' in rawdata[i] or 'BLE connected' in rawdata[i]:
                time=(rawdata[i].split(' ')[1]).split(',')[0]
                state=rawdata[i].split(' ')[2]+' '+(rawdata[i].split(' ')[3]).split('=')[0]
                temp_dict=dict(Time=time,State=state)
                data.append(temp_dict)    
        dict_XID=dict(XID='0300005C',Data=data)    
    return dict_XID



def getUploadXIDDict(serverXID,rawdata):#input機上盒設備跟原始資料
    df=pd.DataFrame()
    XIDstatusTime=[]
    connected_time=0
    disconnected_time=0
    for i in range(len(rawdata)):#加入設備編號
                                
        if 'BLE connected' in rawdata[i]:    
            XID=(rawdata[i].split(' ')[4])
            connected_time=(rawdata[i].split(' ')[1]).split(',')[0]
            # dic_time={str(XID):[connected_time]}
            df=df.append({
                'XID':XID,
                'Time':connected_time,
                'Status':'BLE connected'                
                }, ignore_index=True)
            
            
        if 'BLE disconnected' in rawdata[i]:
            XID=(rawdata[i].split(' ')[4])
            disconnected_time=(rawdata[i].split(' ')[1]).split(',')[0]
            # if connected_time==0:#如果connect_time是空值（先掃到disconnect的狀況）
            #     dic_time={str(XID):[0,disconnected_time]}
            # if connected_time!=0:               
            #     dic_time[str(XID)].append(disconnected_time)
            # dictX['ConnectXID'].append(dic_time)
            df=df.append({
                'XID':XID,
                'Time':disconnected_time,
                'Status':'BLE disconnected'                
                }, ignore_index=True)
            
            continue
    
    '''避免刪除 先保留
        if 'BLE connected' in rawdata[i] and '0165005C' in rawdata[i]:    
            XID=(rawdata[i].split(' ')[4])
            connected_time=(rawdata[i].split(' ')[1]).split(',')[0]

            
        if 'BLE disconnected' in rawdata[i] and '0165005C' in rawdata[i]:
            disconnected_time=(rawdata[i].split(' ')[1]).split(',')[0]
            time=[connected_time,disconnected_time]
            aXIDTime.append(time)
        '''
        

          
    return df

server='xds'
uploadXID='7F571000'

# Connecting代表嘗試連線, Connected代表完成連線, Disconnected代表斷線

#撈設備
connect_time=[]
connect_XID=[]
connect_RSSI=[]

df_thelastStatus=pd.DataFrame()


# Get new upload time
try:
    update_rawlist=getRawList(server,uploadXID,'')
    for i in range(len(update_rawlist)):
        
        if 'txt' not in update_rawlist[i]:
            continue
        
        elif 'txt' in update_rawlist[i]:
            uploadtime_str=update_rawlist[i].split("  ")[0]  
            upload_date = (uploadtime_str.split(' ')[0]).replace('-', '')
            break
except:
    print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))


rawlist=getRawList(server,uploadXID,upload_date)

all_device = []
dict_XID = {}

for i in range(len(rawlist)-1, -1, -1):
    if 'BLE' in rawlist[i]:
        situation = (rawlist[i].split(',')[1]).split('=')[0].lstrip()
        xid = (rawlist[i].split(',')[1]).split('=')[1].lstrip()
        time = (rawlist[i].split(',')[0]).split(' ')[1].lstrip()
        
        if xid not in all_device:
            all_device.append(xid)
            # dict_XID = {xid : {'BLE Connected':[], 'BLE Disconnected' : [], 'BLE connecting' : []}}            
            dict_XID[xid] = {'BLE connected':[], 'BLE disconnected' : [], 'BLE connecting' : []}
            
            if situation=='BLE connected':
                dict_XID[xid]['BLE connected'].append(time)
                
            elif situation=='BLE disconnected':
                dict_XID[xid]['BLE disconnected'].append(time)
                
            elif situation=='BLE connecting':
                dict_XID[xid]['BLE connecting'].append(time)
        
        
        elif xid in all_device:
            if situation=='BLE connected' and len(dict_XID[xid]['BLE connected'])==0:
                dict_XID[xid]['BLE connected'].append(time)
                
            elif situation=='BLE disconnected' and len(dict_XID[xid]['BLE disconnected'])==0:
                dict_XID[xid]['BLE disconnected'].append(time)
                
            elif situation=='BLE connecting' and len(dict_XID[xid]['BLE connecting'])==0:
                dict_XID[xid]['BLE connecting'].append(time)

df = pd.DataFrame(data=dict_XID)
df = df.T

print('Now: {}'.format(datetime.datetime.now()))
print('XID: {}'.format(uploadXID))
print('Update Date: {}'.format(upload_date))
print('Update Time:')
print('')
print(df)

    









                                   



