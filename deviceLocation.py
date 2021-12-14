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

server='xds'
uploadXID='7d951000'
# 876a1000 
XID='0300005C'
# 老師手錶

# Connecting代表嘗試連線
# Connected代表完成連線
# Disconnected代表斷線
def getRawList(server,XID,updateurl): 
    try: 
        if not updateurl:
            urlstart="http://"+server+".ym.edu.tw/"+XID       
        if updateurl:
            urlstart="http://"+server+".ym.edu.tw/"+XID+"/"+updateurl 
    except:
            print('Error: {}. {}, line: {}'.format(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2].tb_lineno))   
    r = requests.get(urlstart)
    rawtxt=r.text
    rawtxt=rawtxt.replace("/","-")
    rawlist=rawtxt.split("\r\n")
    return rawlist
    
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


def getUploadXIDDict(serverXID,rawdata):#input機上盒設備跟原始資料
    df=pd.DataFrame()
    connected_time=0
    disconnected_time=0
    dict_XID={}
    for i in range(len(rawdata)):#加入設備編號
                                
        if 'BLE connected' in rawdata[i]:    
            XID=(rawdata[i].split(' ')[4])
            connected_time=(rawdata[i].split(' ')[1]).split(',')[0]
            if XID not in dict_XID:
                dict_XID[XID]=[[connected_time]]
                continue
            
            if XID in dict_XID:
                dict_XID[XID].append([connected_time])
                continue
                
            
        if 'BLE disconnected' in rawdata[i]:
            XID=(rawdata[i].split(' ')[4])
            disconnected_time=(rawdata[i].split(' ')[1]).split(',')[0]
            if XID not in dict_XID:
                dict_XID[XID]=disconnected_time
                continue
                
            elif XID in dict_XID:
                lg=len(dict_XID[XID])-1
                dict_XID[XID][lg].append(disconnected_time)
                continue

            
            continue
          
    return dict_XID

def getConnectDevice(dict_XID):
    XIDs=[]
    for key in dict_XID:
        XIDs.append(key)
    return XIDs

def getLastStatus(dict_XID):
    dict_XID_laststatus={}

    for key in dict_XID:
        lg=len(dict_XID[key])-1
        dict_XID_laststatus[key]= dict_XID[key][lg]
        
    return dict_XID_laststatus

def checkisnotConnect(dict_last):
    dict_XID_status={}
    
    for key in dict_last:
        if len(dict_last[key])==1:
            dict_XID_status[key]='Connected'
            
        elif len(dict_last[key])>1:
            dict_XID_status[key]='Disconnected'
    
    return dict_XID_status


            
        
    

#撈設備
connect_time=[]
connect_XID=[]
connect_RSSI=[]


aUpload_newupdatetime, aUpload_timeurl = getNewUpdatetime(server,uploadXID)
a_rawdata=getRawList(server,uploadXID,aUpload_timeurl)
dict_XIDtrace=getUploadXIDDict('7d951000',a_rawdata)
list_xids=getConnectDevice(dict_XIDtrace)
dict_laststaus=getLastStatus(dict_XIDtrace)

str_status=checkisnotConnect(dict_laststaus)


a=datetime.datetime.now()







                                   



