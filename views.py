from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from collections import defaultdict
from django.conf import settings
from aip import AipSpeech
import requests
import pymongo,json
import pandas as pd
import numpy as np
from .models import QuestionClassifier
from .models import QuestionPaser
from .models import AnswerSearcher
import json
import os
from math import radians, cos, sin, asin, sqrt, ceil
import ast
import re
import math
import time

turing_api_key = "3c005cc7ace444f3a06cc28248626d4b"
api_url = "http://openapi.tuling123.com/openapi/api/v2"  # 图灵机器人api网址
headers = {'Content-Type': 'application/json;charset=UTF-8'}
# Create your views here.
def Data(request):
    data=["无线电业务"]#106.52.100.206
    myclient=pymongo.MongoClient("mongodb://localhost:27017")
    mydb=myclient["Django"]
    mycol=mydb["radios"]
    da=mycol.find_one()
    item=(dict(da))
    item.pop("_id")
    data.append(item)
    return JsonResponse({'status':200,"data":data})

def index(request):
    return render(request, 'index.html')


def reta(request):
    return render(request, 'reta.html')

def jiazai(request):
    return render(request, 'jiazai.html')



def buss(request):
    return render(request, 'buss.html')


def reta_list(resuest):
    return render(resuest, 'reta_list.html')


def buss_list(request):
    return render(request, 'buss_list.html')


def tu(request):
    return render(request, 'tu.html')


def geodistance(lng1,lat1,lng2,lat2):
        lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)])
        # 经纬度转换成弧度
        dlon=lng2-lng1
        dlat=lat2-lat1
        a=sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        distance=2*asin(sqrt(a))*6371*1000 # 地球平均半径，6371km
        distance=round(distance,0)
        return distance


def ganrao(request):
    jingweidu = str(request.POST.get('jingweidu'))
    client = pymongo.MongoClient('mongodb://localhost:27017')
    diqu = str(request.POST.get('diqu'))
    print('#####',diqu)
    db = client["node"]
    x=0
    y=0
    try:
        out4 = db.create_collection('diqu')
    except:
        out4 = db['diqu']
    df_diqu = pd.DataFrame(list(out4.find())).T
    if diqu == 'None':
        print('没有数据')
    else:
        diqu = np.int(diqu)
        c = diqu
        t = list(df_diqu.iloc[c, :])
        x = t[0].split(',')[0]
        y = t[0].split(',')[1]
    qiehuan = client['node']
    try:
        myku = qiehuan.create_collection('qiehuan', capped=True, size=1024 * 1024, max=1)
    except:
        myku = qiehuan['qiehuan']
    if jingweidu == 'None':
        name = '请在上面输入框输入您的设备的经纬度'
        myku1 = dict(name=name)
        myku.insert(myku1)
        print('没有数据')
    else:
        jingweidu=jingweidu.split(",")
        jingdu=float(jingweidu[0])
        weidu=float(jingweidu[1])
        print(jingdu)
        print(weidu)
        distance = geodistance(x,y,jingdu,weidu)
        print(distance)
        if distance > 5000:
            name = "您的设备未受到基站信号干扰"
        else:
            name = "您的设备已受到基站信号干扰，请及时调整设备位置"
        myku1 = dict(name=name)
        myku.insert(myku1)

    print(name)
    return render(request, 'ganrao.html',context={"name": name})
def plot2(request):
    client = pymongo.MongoClient('mongodb://localhost:27017')
    qiehuan = client['node']
    try:
        myku = qiehuan.create_collection('qiehuan')
    except:
        myku = qiehuan['qiehuan']
    ku2 = []
    for x in myku.find({}, {"_id": 0}):
        ku2.append(x)
    data4 = dict(countload=ku2,)
    return HttpResponse(json.dumps(data4))

def plot1(request):
    client = pymongo.MongoClient('mongodb://localhost:27017')
    diqu = np.int(request.POST.get('diqu'))
    db = client["node"]
    try:
        out4 = db.create_collection('diqu')
    except:
        out4 = db['diqu']
    df_diqu = pd.DataFrame(list(out4.find())).T
    if diqu == 'None':
        print('没有数据')
    else:
        c = diqu
        t = list(df_diqu.iloc[c, :])
        x = t[0].split(',')[0]
        y = t[0].split(',')[1]
    data4 = dict(countload='jjj',)
    return HttpResponse(json.dumps(data4))



def ceshi(request):
    zuobiao = str(request.POST.get('zuobiao'))
    fuwu= str(request.POST.get('fuwu'))
    print(zuobiao)
    print('#####',fuwu)
    client = pymongo.MongoClient('mongodb://localhost:27017')
    zuobiao1 = client['node']

    try:
        out5 = zuobiao1.create_collection('zuobiao', capped=True, size=1024 * 1024, max=1)
    except:
        out5 = zuobiao1['zuobiao']
    if zuobiao == 'None':
        print('没有数据')
    else:
        user_dict = ast.literal_eval(zuobiao)
        a=dict(a=user_dict)
        out5.insert(a)
    fuwu1 = client['node']
    try:
        out6 = fuwu1.create_collection('fuwu', capped=True, size=1024 * 1024, max=1)
    except:
        out6 = fuwu1['fuwu']

    if fuwu == 'None':
        print('没有数据')
    else:
        #p = re.findall(r'[{](.*?)[}]', zuobiao)
        user_dict = ast.literal_eval(fuwu)
        f=dict(f=user_dict)
        out6.insert(f)

    client = pymongo.MongoClient('mongodb://localhost:27017')
    db = client["node"]
    try:
        out5 = db.create_collection('zuobiao')
    except:
        out5 = db['zuobiao']
    t1 = []
    t2 = []
    t3 = []
    t4 = []
    p = []
    q = []
    r = []
    s = []
    px = []
    qx = []
    rx = []
    sx = []
    bh = []
    YH = []
    WH = []
    df_baohu = pd.DataFrame(list(out5.find())).T
    if len(df_baohu) == 0:
        print('没有数据')
    else:
        d = df_baohu.iloc[1].values
        df1 = pd.DataFrame(d)
        df2 = pd.DataFrame([df1.iloc[0, :][0]])
        for i in range(len(df2.columns)):
            x = np.float(df2.iloc[0, :][i].split(',')[1])
            y = np.float(df2.iloc[0, :][i].split(',')[2])
            x1 = np.float(df2.iloc[0, :][i].split(',')[3])
            y1 = np.float(df2.iloc[0, :][i].split(',')[4])
            z1 = np.float(df2.iloc[0, :][i].split(',')[5])
            t1.append(x)
            t2.append(y)
            t3.append(x1)
            t4.append(y1)
            bh.append(z1)
        for i in range(len(df2.columns)):
            if bh[i] == 0:
                YH.append(i)
            elif bh[i] == 1:
                WH.append(i)

        for i in YH:
            if 3400 <= t1[i] < 3600:
                p.append(i)
            elif 3600 <= t1[i] < 3700:
                q.append(i)
            elif 3700 <= t1[i] < 4200:
                r.append(i)
            elif 4500 <= t1[i] < 4900:
                s.append(i)
        for i in WH:
            if 3400 <= t1[i] < 3600:
                px.append(i)
            elif 3600 <= t1[i] < 3700:
                qx.append(i)
            elif 3700 <= t1[i] < 4200:
                rx.append(i)
            elif 4500 <= t1[i] < 4900:
                sx.append(i)

    db = client["node"]
    try:
        out6 = db.create_collection('fuwu')
    except:
        out6 = db['fuwu']
    t5 = []
    t6 = []
    t7 = []
    t8 = []
    t9 = []
    NY = []
    YY = []
    NN = []
    u = []
    v = []
    w = []
    z = []
    ux = []
    vx = []
    wx = []
    zx = []
    zxx = []
    zzx = []
    jl = []
    o = {}
    e = {}
    h = {}
    df_fuwu = pd.DataFrame(list(out6.find())).T
    d1 = df_fuwu.iloc[1].values
    df3 = pd.DataFrame(d1)
    df4 = pd.DataFrame([df3.iloc[0, :][0]])
    for i in range(len(df4.columns)):
        x2 = np.float(df4.iloc[0, :][i].split(',')[1])
        y2 = np.float(df4.iloc[0, :][i].split(',')[2])
        x3 = np.float(df4.iloc[0, :][i].split(',')[4])
        y3 = np.float(df4.iloc[0, :][i].split(',')[5])
        NY = np.float(df4.iloc[0, :][i].split(',')[3])
        t5.append(x2)
        t6.append(y2)
        t7.append(x3)
        t8.append(y3)
        t9.append(NY)

    for i in range(len(df4.columns)):
        if t9[i] == 0:
            YY.append(i)
        elif t9[i] == 1:
            NN.append(i)

    for i in YY:
        if 3400 <= t5[i] < 3600:
            u.append(i)
        elif 3600 <= t5[i] < 3700:
            v.append(i)
        elif 3700 <= t5[i] < 4200:
            w.append(i)
        elif 4800 <= t5[i] < 4900:
            z.append(i)
        elif 4900 <= t5[i] <= 5000:
            zxx.append(i)
    for i in NN:
        if 3400 <= t5[i] < 3600:
            ux.append(i)
        elif 3600 <= t5[i] < 3700:
            vx.append(i)
        elif 3700 <= t5[i] < 4200:
            wx.append(i)
        elif 4800 <= t5[i] < 4900:
            zx.append(i)
        elif 4900 <= t5[i] <= 5000:
            zzx.append(i)

    for m in p:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 42500:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(42500)
    for m in q:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 4000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(4000)
    for m in r:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 4000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(4000)
    for m in s:
        for n in z:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 4000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(4000)

    for m in p:
        for n in ux:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 1000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(1000)
    for m in q:
        for n in ux:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 50:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(50)
    for m in s:
        for n in zxx:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 2000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(2000)

    for m in rx:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 100:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(100)
    for m in sx:
        for n in zxx:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 100:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(100)

    print(e)
    for k, v, in o.items():
        v = set(v)
        v = list(v)
        for value in v:
            h.setdefault(k, []).append(value)

    return render(request, 'ceshi.html',{'data':e,'gh':h})


def plot3(request):
    client = pymongo.MongoClient('mongodb://localhost:27017')
    db = client["node"]
    try:
        out5 = db.create_collection('zuobiao')
    except:
        out5 = db['zuobiao']
    t1 = []
    t2 = []
    t3 = []
    t4 = []
    p = []
    q = []
    r = []
    s = []
    px = []
    qx = []
    rx = []
    sx = []

    bh = []
    YH = []
    WH = []
    df_baohu = pd.DataFrame(list(out5.find())).T
    if len(df_baohu) == 0:
        print('没有数据')
    else:
        d = df_baohu.iloc[1].values
        df1 = pd.DataFrame(d)
        df2 = pd.DataFrame([df1.iloc[0, :][0]])
        for i in range(len(df2.columns)):
            x = np.float(df2.iloc[0, :][i].split(',')[1])
            y = np.float(df2.iloc[0, :][i].split(',')[2])
            x1 = np.float(df2.iloc[0, :][i].split(',')[3])
            y1 = np.float(df2.iloc[0, :][i].split(',')[4])
            z1 = np.float(df2.iloc[0, :][i].split(',')[5])
            t1.append(x)
            t2.append(y)
            t3.append(x1)
            t4.append(y1)
            bh.append(z1)

        for i in range(len(df2.columns)):
            if bh[i] == 0:
                YH.append(i)
            elif bh[i] == 1:
                WH.append(i)

        for i in YH:
            if 3400 <= t1[i] < 3600:
                p.append(i)
            elif 3600 <= t1[i] < 3700:
                q.append(i)
            elif 3700 <= t1[i] < 4200:
                r.append(i)
            elif 4500 <= t1[i] < 4900:
                s.append(i)

        for i in WH:
            if 3400 <= t1[i] < 3600:
                px.append(i)
            elif 3600 <= t1[i] < 3700:
                qx.append(i)
            elif 3700 <= t1[i] < 4200:
                rx.append(i)
            elif 4500 <= t1[i] < 4900:
                sx.append(i)

    db = client["node"]
    try:
        out6 = db.create_collection('fuwu')
    except:
        out6 = db['fuwu']
    t5 = []
    t6 = []
    t7 = []
    t8 = []
    t9 = []
    NY = []
    YY = []
    NN = []
    u = []
    v = []
    w = []
    z = []
    ux = []
    vx = []
    wx = []
    zx = []
    zxx = []
    zzx = []
    jl = []
    o = {}
    e = {}
    h = {}
    df_fuwu = pd.DataFrame(list(out6.find())).T
    d1 = df_fuwu.iloc[1].values
    df3 = pd.DataFrame(d1)
    df4 = pd.DataFrame([df3.iloc[0, :][0]])
    for i in range(len(df4.columns)):
        x2 = np.float(df4.iloc[0, :][i].split(',')[1])
        y2 = np.float(df4.iloc[0, :][i].split(',')[2])
        x3 = np.float(df4.iloc[0, :][i].split(',')[4])
        y3 = np.float(df4.iloc[0, :][i].split(',')[5])
        NY = np.float(df4.iloc[0, :][i].split(',')[3])
        t5.append(x2)
        t6.append(y2)
        t7.append(x3)
        t8.append(y3)
        t9.append(NY)

    for i in range(len(df4.columns)):
        if t9[i] == 0:
            YY.append(i)
        elif t9[i] == 1:
            NN.append(i)

    for i in YY:
        if 3400 <= t5[i] < 3600:
            u.append(i)
        elif 3600 <= t5[i] < 3700:
            v.append(i)
        elif 3700 <= t5[i] < 4200:
            w.append(i)
        elif 4800 <= t5[i] < 4900:
            z.append(i)
        elif 4900 <= t5[i] <= 5000:
            zxx.append(i)
    for i in NN:
        if 3400 <= t5[i] < 3600:
            ux.append(i)
        elif 3600 <= t5[i] < 3700:
            vx.append(i)
        elif 3700 <= t5[i] < 4200:
            wx.append(i)
        elif 4800 <= t5[i] < 4900:
            zx.append(i)
        elif 4900 <= t5[i] <= 5000:
            zzx.append(i)

    for m in p:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 42500:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(42500)
    for m in q:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 4000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(4000)
    for m in r:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 4000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(4000)
    for m in s:
        for n in z:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 4000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(4000)

    for m in p:
        for n in ux:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 1000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(1000)
    for m in q:
        for n in ux:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 50:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(50)
    for m in s:
        for n in zxx:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 2000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(2000)

    for m in rx:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 100:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(100)
    for m in sx:
        for n in zxx:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 100:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(100)


    data = dict(x=t3,y=t4,x1=t7,y1=t8)
    return HttpResponse(json.dumps(data))


def ceshi1(request):
    baohu = str(request.POST.get('baohu'))
    jizhan= str(request.POST.get('jizhan'))
    print(baohu)
    print('#####',jizhan)
    client = pymongo.MongoClient('mongodb://localhost:27017')
    baohu1 = client['node']
    try:
        out10 = baohu1.create_collection('baohu', capped=True, size=1024 * 1024, max=1)
    except:
        out10 = baohu1['baohu']
    if baohu == 'None':
        print('没有数据')
    else:
        user_dict = ast.literal_eval(baohu)
        a=dict(a=user_dict)
        out10.insert(a)
    jizhan1 = client['node']
    try:
        out11 = jizhan1.create_collection('jizhan', capped=True, size=1024 * 1024, max=1)
    except:
        out11 =jizhan1['jizhan']

    if jizhan == 'None':
        print('没有数据')
    else:
        #p = re.findall(r'[{](.*?)[}]', zuobiao)
        user_dict = ast.literal_eval(jizhan)
        f=dict(f=user_dict)
        out11.insert(f)

    client = pymongo.MongoClient('mongodb://localhost:27017')
    db = client["node"]
    try:
        out10= db.create_collection('baohu')
    except:
        out10 = db['baohu']
    t1 = []
    t2 = []
    t3 = []
    t4 = []
    p = []
    q = []
    r = []
    s = []
    px = []
    qx = []
    rx = []
    sx = []
    bh = []
    YH = []
    WH = []
    df_baohu = pd.DataFrame(list(out10.find())).T
    if len(df_baohu) == 0:
        print('没有数据')
    else:
        d = df_baohu.iloc[1].values
        df1 = pd.DataFrame(d)
        df2 = pd.DataFrame([df1.iloc[0, :][0]])
        for i in range(len(df2.columns)):
            x = np.float(df2.iloc[0, :][i].split(',')[1])
            y = np.float(df2.iloc[0, :][i].split(',')[2])
            x1 = np.float(df2.iloc[0, :][i].split(',')[3])
            y1 = np.float(df2.iloc[0, :][i].split(',')[4])
            z1 = np.float(df2.iloc[0, :][i].split(',')[5])
            t1.append(x)
            t2.append(y)
            t3.append(x1)
            t4.append(y1)
            bh.append(z1)
        for i in range(len(df2.columns)):
            if bh[i] == 0:
                YH.append(i)
            elif bh[i] == 1:
                WH.append(i)

        for i in YH:
            if 3400 <= t1[i] < 3600:
                p.append(i)
            elif 3600 <= t1[i] < 3700:
                q.append(i)
            elif 3700 <= t1[i] < 4200:
                r.append(i)
            elif 4500 <= t1[i] < 4900:
                s.append(i)

        for i in WH:
            if 3400 <= t1[i] < 3600:
                px.append(i)
            elif 3600 <= t1[i] < 3700:
                qx.append(i)
            elif 3700 <= t1[i] < 4200:
                rx.append(i)
            elif 4500 <= t1[i] < 4900:
                sx.append(i)


    db = client["node"]
    try:
        out11= db.create_collection('jizhan')
    except:
        out11 = db['jizhan']
    t5 = []
    t6 = []
    t7 = []
    t8 = []
    t9=[]
    NY=[]
    YY=[]
    NN=[]
    u = []
    v = []
    w = []
    z = []
    ux = []
    vx = []
    wx= []
    zx = []
    zxx = []
    zzx = []
    jl=[]
    o = {}
    e = {}
    h = {}
    df_fuwu = pd.DataFrame(list(out11.find())).T
    d1 = df_fuwu.iloc[1].values
    df3 = pd.DataFrame(d1)
    df4 = pd.DataFrame([df3.iloc[0, :][0]])
    for i in range(len(df4.columns)):
        x2 = np.float(df4.iloc[0, :][i].split(',')[1])
        y2 = np.float(df4.iloc[0, :][i].split(',')[2])
        x3 = np.float(df4.iloc[0, :][i].split(',')[4])
        y3 = np.float(df4.iloc[0, :][i].split(',')[5])
        NY= np.float(df4.iloc[0, :][i].split(',')[3])
        t5.append(x2)
        t6.append(y2)
        t7.append(x3)
        t8.append(y3)
        t9.append(NY)

    for i in range(len(df4.columns)):
        if t9[i]==0:
            YY.append(i)
        elif t9[i]==1:
            NN.append(i)

    for i in YY:
        if 3400 <= t5[i] < 3600:
            u.append(i)
        elif 3600 <= t5[i] < 3700:
            v.append(i)
        elif 3700 <= t5[i] < 4200:
            w.append(i)
        elif 4800 <= t5[i] < 4900:
            z.append(i)
        elif 4900<=t5[i]<=5000:
            zxx.append(i)
    for i in NN:
        if 3400 <= t5[i] < 3600:
            ux.append(i)
        elif 3600 <= t5[i] < 3700:
            vx.append(i)
        elif 3700 <= t5[i] < 4200:
            wx.append(i)
        elif 4800 <= t5[i] < 4900:
            zx.append(i)
        elif 4900<=t5[i]<=5000:
            zzx.append(i)




    for m in p:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 42500:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(42500)
    for m in q:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 4000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(4000)
    for m in r:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 4000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(4000)
    for m in s:
        for n in z:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 4000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(4000)

    for m in p:
        for n in ux:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 1000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(1000)
    for m in q:
        for n in ux:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 50:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(50)
    for m in s:
        for n in zxx:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 2000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(2000)

    for m in rx:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 100:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(100)
    for m in sx:
        for n in zxx:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 100:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(100)

    print(e)
    for k, v, in o.items():
        v = set(v)
        v = list(v)
        for value in v:
            h.setdefault(k, []).append(value)

    return render(request, 'ceshi1.html',{'data':e,'gh':h})


def plot4(request):
    client = pymongo.MongoClient('mongodb://localhost:27017')
    db = client["node"]
    try:
        out10 = db.create_collection('baohu')
    except:
        out10 = db['baohu']
    t1 = []
    t2 = []
    t3 = []
    t4 = []
    p = []
    q = []
    r = []
    s = []
    px = []
    qx = []
    rx = []
    sx = []

    bh=[]
    YH=[]
    WH=[]
    df_baohu = pd.DataFrame(list(out10.find())).T
    if len(df_baohu) == 0:
        print('没有数据')
    else:
        d = df_baohu.iloc[1].values
        df1 = pd.DataFrame(d)
        df2 = pd.DataFrame([df1.iloc[0, :][0]])
        for i in range(len(df2.columns)):
            x = np.float(df2.iloc[0, :][i].split(',')[1])
            y = np.float(df2.iloc[0, :][i].split(',')[2])
            x1 = np.float(df2.iloc[0, :][i].split(',')[3])
            y1 = np.float(df2.iloc[0, :][i].split(',')[4])
            z1=np.float(df2.iloc[0, :][i].split(',')[5])
            t1.append(x)
            t2.append(y)
            t3.append(x1)
            t4.append(y1)
            bh.append(z1)

        for i in range(len(df2.columns)):
            if bh[i]==0:
                YH.append(i)
            elif bh[i]==1:
                WH.append(i)

        for i in YH:
            if 3400 <= t1[i] < 3600:
                p.append(i)
            elif 3600 <= t1[i] < 3700:
                q.append(i)
            elif 3700 <= t1[i] < 4200:
                r.append(i)
            elif 4500 <= t1[i] < 4900:
                s.append(i)

        for i in WH:
            if 3400 <= t1[i] < 3600:
                px.append(i)
            elif 3600 <= t1[i] < 3700:
                qx.append(i)
            elif 3700 <= t1[i] < 4200:
                rx.append(i)
            elif 4500 <= t1[i] < 4900:
                sx.append(i)


    db = client["node"]
    try:
        out11 = db.create_collection('jizhan')
    except:
        out11 = db['jizhan']
    t5 = []
    t6 = []
    t7 = []
    t8 = []
    t9 = []
    NY = []
    YY = []
    NN = []
    u = []
    v = []
    w = []
    z = []
    ux = []
    vx = []
    wx = []
    zx = []
    zxx=[]

    jl = []
    o = {}
    e = {}
    h = {}

    df_fuwu = pd.DataFrame(list(out11.find())).T
    d1 = df_fuwu.iloc[1].values
    df3 = pd.DataFrame(d1)
    df4 = pd.DataFrame([df3.iloc[0, :][0]])
    for i in range(len(df4.columns)):
        x2 = np.float(df4.iloc[0, :][i].split(',')[1])
        y2 = np.float(df4.iloc[0, :][i].split(',')[2])
        x3 = np.float(df4.iloc[0, :][i].split(',')[4])
        y3 = np.float(df4.iloc[0, :][i].split(',')[5])
        NY = np.float(df4.iloc[0, :][i].split(',')[3])
        t5.append(x2)
        t6.append(y2)
        t7.append(x3)
        t8.append(y3)
        t9.append(NY)

    for i in range(len(df4.columns)):
        if t9[i] == 0:
            YY.append(i)
        elif t9[i] == 1:
            NN.append(i)

    for i in YY:
        if 3400 <= t5[i] < 3600:
            u.append(i)
        elif 3600 <= t5[i] < 3700:
            v.append(i)
        elif 3700 <= t5[i] < 4200:
            w.append(i)
        elif 4800 <= t5[i] < 4900:
            z.append(i)
        elif 4900<=t5[i]<=5000:
            zxx.append(i)
    for i in NN:
        if 3400 <= t5[i] < 3600:
            ux.append(i)
        elif 3600 <= t5[i] < 3700:
            vx.append(i)
        elif 3700 <= t5[i] < 4200:
            wx.append(i)
        elif 4800 <= t5[i] < 4900:
            zx.append(i)


    for m in p:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 42500:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(42500)
    for m in q:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 4000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(4000)
    for m in r:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 4000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(4000)
    for m in s:
        for n in z:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 4000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(4000)

    for m in p:
        for n in ux:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 1000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(1000)
    for m in q:
        for n in ux:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 50:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(50)
    for m in s:
        for n in zxx:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 2000:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(2000)

    for m in rx:
        for n in u:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 100:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(100)
    for m in sx:
        for n in zxx:
            distance = geodistance(t3[m], t4[m], t7[n], t8[n])
            if distance < 100:
                k = df2.columns[m]
                l = df4.columns[n]
                e.setdefault(l, []).append(k)
                e.setdefault(l, []).append(distance)
                o.setdefault(k, []).append(t3[m])
                o.setdefault(k, []).append(t4[m])
                jl.append(100)




    print(jl)

    data = dict(x=t3, y=t4, x1=t7, y1=t8,jl=jl)
    return HttpResponse(json.dumps(data))


def fushe(request):
    canshu = str(request.POST.get('canshu'))
    client = pymongo.MongoClient('mongodb://localhost:27017')
    canshu1 = client['node']
    try:
        out12 = canshu1.create_collection('canshu', capped=True, size=1024 * 1024, max=1)
    except:
        out12 = canshu1['canshu']
    if canshu== 'None':
        print('没有数据')
    else:
        user_dict = ast.literal_eval(canshu)
        a=dict(a=user_dict)
        out12.insert(a)
    df_canshu = pd.DataFrame(list(out12.find())).T

    c = []
    f = {}

    r = 0.017
    p = 0.413
    b = [0, 10, 20,  40,  60,  100,  120]
    if len(df_canshu) == 0:
        print('没有数据')
    else:
        d = df_canshu.iloc[1].values
        df1 = pd.DataFrame(d)
        df2 = pd.DataFrame([df1.iloc[0, :][0]])
        for i in range(len(df2.columns)):
            x = np.float(df2.iloc[0, :][i].split(',')[0])
            y = np.float(df2.iloc[0, :][i].split(',')[1])
            x1 = np.float(df2.iloc[0, :][i].split(',')[2])
            y1 = np.float(df2.iloc[0, :][i].split(',')[3])
            E=y1
            ha=x
            hb=y
            a=x1
            for i in b:
                d = i
                r = 0.017
                p = 0.413
                b = [0, 10, 20, 40,  60, 100, 120]
                q = 4 * math.pi
                s1 = (E * math.pow((1 + p), 2)) / (q * (math.pow(d, 2) + math.pow(ha - hb, 2)))
                s2 = (1 + r * a) * math.pow(math.atan(d / (ha - hb)), 2)
                s = s1 * s2
                c.append(s)
                f[d]=s

    return render(request, 'fushe.html',{'data':b,'data1':c,'data2':f})


def wxgr(request):
    client = pymongo.MongoClient('mongodb://localhost:27017')
    mx1 = client['node']
    try:
        out13 = mx1.create_collection('mx', capped=True, size=1024 * 1024, max=6)
    except:
        out13 = mx1['mx']
    df_mx = pd.DataFrame(list(out13.find())).T
    index_list=[-30,-25,-20,-15,-10,-5,0,5,10,15,20]
    a0 = df_mx.iloc[1:, 0]
    a1 = df_mx.iloc[1:, 1]
    a2 = df_mx.iloc[1:, 2]
    a3 = df_mx.iloc[1:, 3]
    a4 = df_mx.iloc[1:, 4]
    a5 = df_mx.iloc[1:, 5]
    c0 = [float(val) for val in list(a0.values)]
    c1 = [float(val) for val in list(a1.values)]
    c2 = [float(val) for val in list(a2.values)]
    c3 = [float(val) for val in list(a3.values)]
    c4 = [float(val) for val in list(a4.values)]
    c5 = [float(val) for val in list(a5.values)]

    return render(request, 'wxgr.html',{'data':index_list,'data0':c0,'data1':c1,'data2':c2,'data3':c3,'data4':c4,'data5':c5})


def shebei(request):
    client = pymongo.MongoClient("localhost")
    db = client["Django"]
    out4 = db["shebei"]
    df = pd.DataFrame(list(out4.find())).T


    f_pro_list = list(df.iloc[1:, 8].value_counts()[:10].index)    # 厂家生产设备种类
    f_sum_list = list(df.iloc[1:, 8].value_counts()[:10].values)


    f_mac_list = list(df.iloc[1:, 3].value_counts()[:5].index)    # 设备种类
    f_mac_sum_list = list(df.iloc[1:, 3].value_counts()[:5].values)
    mac_dict = dict(zip(f_mac_list, f_mac_sum_list))


    fre_list = list(df.iloc[1:, 5].values)[:-1]    # 设备发射功率
    new_fre_list = []
    for val in fre_list:
        a = val.strip()
        b = a.replace("（", "(")
        c = b.replace("）", ")")
        new_fre_list.append(c)
    f_new_fre_list = []
    for val in new_fre_list:
        if val != '－－－':
            f_new_fre_list.append(val)
    end_fre_list = list(pd.Series(f_new_fre_list).value_counts()[:8].index)
    end_fre_sum_list = list(pd.Series(f_new_fre_list).value_counts()[:8].values)
    fre_dict = dict(zip(end_fre_list, end_fre_sum_list))


    init_date_list = [val.split('-') for val in list(df.iloc[1:, 9].values)]   # 年度设备发证数量
    spring_list_2014 = []
    spring_list_2015 = []
    spring_list_2016 = []
    spring_list_2017 = []
    spring_list_2018 = []
    spring_list_2019 = []
    summer_list_2014 = []
    summer_list_2015 = []
    summer_list_2016 = []
    summer_list_2017 = []
    summer_list_2018 = []
    summer_list_2019 = []
    autumn_list_2014 = []
    autumn_list_2015 = []
    autumn_list_2016 = []
    autumn_list_2017 = []
    autumn_list_2018 = []
    autumn_list_2019 = []
    winter_list_2014 = []
    winter_list_2015 = []
    winter_list_2016 = []
    winter_list_2017 = []
    winter_list_2018 = []
    winter_list_2019 = []
    for val in init_date_list:
        if val[0] == '2014':
            if (int(val[1]) >= 1) and (int(val[1]) <= 3):
                spring_list_2014.append(val)
            elif (int(val[1]) >= 4) and (int(val[1]) <= 6):
                summer_list_2014.append(val)
            elif (int(val[1]) >= 7) and (int(val[1]) <= 9):
                autumn_list_2014.append(val)
            else:
                winter_list_2014.append(val)
        elif val[0] == '2015':
            if (int(val[1]) >= 1) and (int(val[1]) <= 3):
                spring_list_2015.append(val)
            elif (int(val[1]) >= 4) and (int(val[1]) <= 6):
                summer_list_2015.append(val)
            elif (int(val[1]) >= 7) and (int(val[1]) <= 9):
                autumn_list_2015.append(val)
            else:
                winter_list_2015.append(val)
        elif val[0] == '2016':
            if (int(val[1]) >= 1) and (int(val[1]) <= 3):
                spring_list_2016.append(val)
            elif (int(val[1]) >= 4) and (int(val[1]) <= 6):
                summer_list_2016.append(val)
            elif (int(val[1]) >= 7) and (int(val[1]) <= 9):
                autumn_list_2016.append(val)
            else:
                winter_list_2016.append(val)
        elif val[0] == '2017':
            if (int(val[1]) >= 1) and (int(val[1]) <= 3):
                spring_list_2017.append(val)
            elif (int(val[1]) >= 4) and (int(val[1]) <= 6):
                summer_list_2017.append(val)
            elif (int(val[1]) >= 7) and (int(val[1]) <= 9):
                autumn_list_2017.append(val)
            else:
                winter_list_2017.append(val)
        elif val[0] == '2018':
            if (int(val[1]) >= 1) and (int(val[1]) <= 3):
                spring_list_2018.append(val)
            elif (int(val[1]) >= 4) and (int(val[1]) <= 6):
                summer_list_2018.append(val)
            elif (int(val[1]) >= 7) and (int(val[1]) <= 9):
                autumn_list_2018.append(val)
            else:
                winter_list_2018.append(val)
        else:
            if (int(val[1]) >= 1) and (int(val[1]) <= 3):
                spring_list_2019.append(val)
            elif (int(val[1]) >= 4) and (int(val[1]) <= 6):
                summer_list_2019.append(val)
            elif (int(val[1]) >= 7) and (int(val[1]) <= 9):
                autumn_list_2019.append(val)
            else:
                winter_list_2019.append(val)
    spring_list = [len(spring_list_2014), len(spring_list_2015), len(spring_list_2016), len(spring_list_2017), len(spring_list_2018), len(spring_list_2019)]
    summer_list = [len(summer_list_2014), len(summer_list_2015), len(summer_list_2016), len(summer_list_2017), len(summer_list_2018), len(summer_list_2019)]
    autumn_list = [len(autumn_list_2014), len(autumn_list_2015), len(autumn_list_2016), len(autumn_list_2017), len(autumn_list_2018), len(autumn_list_2019)]
    winter_list = [len(winter_list_2014), len(winter_list_2015), len(winter_list_2016), len(winter_list_2017), len(winter_list_2018), len(winter_list_2019)]
    year_data_list = ['2014年', '2015年', '2016年', '2017年', '2018年', '2019年']


    tech_list = list(df.iloc[1:, 3].values)   # 设备网络通讯标准统计图
    f_tech_list = []
    for val in tech_list:
        m_tech_list = val.split('/')
        for val1 in m_tech_list:
            f_tech_list.append(val1)
    obj1 = pd.Series(f_tech_list)
    obj_net = obj1.value_counts()
    net_list = ['GSM', 'TD-SCDMA', 'WCDMA', 'cdma2000', 'TD-LTE', 'LTE FDD']    # 通讯技术标准
    # 对应通讯技术标准对应设备的种类数目
    net_sum_list = [obj_net[net_list[0]], obj_net[net_list[1]], obj_net[net_list[2]], obj_net[net_list[3]], obj_net[net_list[4]], obj_net[net_list[5]]]

    max_value_list = list(df.iloc[1:, 6].values)   # 设备占用带宽统计图
    new_value_list = []
    for val in max_value_list:
        a = val.strip()
        new_value_list.append(a)
    f_new_value_list = []
    for val in new_value_list:
        if val != '－－－':
            f_new_value_list.append(val)
    f_value_list = pd.Series(f_new_value_list).value_counts()[:6]
    end_value_list = list(f_value_list.index)   # 设备占用带宽名称
    end_value_sum_list = list(f_value_list.values)   # 设备占用带宽种类数目
    value_dict = dict(zip(end_value_list, end_value_sum_list))

    lan_obj = (df.loc[(df[3] == '蓝牙设备') & (df[8] == '华为技术有限公司')]).iloc[0, :]  # 蓝牙设备的数据
    ji_obj = (df.loc[(df[3] == 'GSM基站') & (df[8] == '华为技术有限公司')]).iloc[0, :]  # GSM基站的数据


    return render(request, 'shebei.html', context={'data': f_sum_list, 'data1': f_pro_list, 'data2': mac_dict, 'data3': fre_dict,'data4': spring_list, 'data5': summer_list, 'data6': autumn_list, 'data7': winter_list,'data8': year_data_list, 'data9': net_list, 'data10': net_sum_list, 'data11': value_dict, 'data12': lan_obj, 'data13': ji_obj})


def shebei1(request):
    question = str(request.POST.get('wenti'))
    if question == 'None':
        q4 = "请在上方输入框输入问题"
        print('没有数据')
    else:
        print(question)
        q1 = QuestionClassifier().classify(question)
        print(q1)
        q2 = QuestionPaser().parser_main(q1)
        print(q2)
        q3 = AnswerSearcher().search_main(q2)
        print(q3)
        if not q3:
            q4 = "无结果"
        else:
            q4 = q3

    return JsonResponse({"data14":q4})


def zhanyongdu(request):
    x = []
    for root, dirs, files in os.walk("D:/工程/111/static/datas"):
        for f in files:
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf8')as fp:
                json_data = json.load(fp)
                x.append(json_data)

    time = []
    time1 = []
    arr = -67
    tz = []
    tz0=[]
    tz1 = []
    tz2 = []
    tz3 = []
    tz4 = []
    tz5 = []
    tz6 = []
    tz7 = []
    pz = []
    da = []
    pzx=[]
    for i in range(0, 144):
        d = x[i]
        q = d["spectrum"]
        da.append(q)
        z = 0
        z0 = 0
        z1 = 0
        z2 = 0
        z3 = 0
        z4 = 0
        z5 = 0
        z6 = 0
        z7 = 0

        for k in range(478, 482):
            if q[k] > arr:
                z = z + 1
        zz = (z / 5)*100
        tz.append(zz)
        for K in (78, 82):
            if q[K] > arr:
                z0 = z0 + 1
        zz0 = (z0 / 5) * 100
        tz0.append(zz0)
        for k in range(30, 34):
            if q[k] > arr:
                z1 = z1 + 1
        zz1 = (z1 / 5) * 100
        tz1.append(zz1)
        for k in range(150, 154):
            if q[k] > arr:
                z2 = z2 + 1
        zz2 = (z2 / 5) * 100
        tz2.append(zz2)
        for k in range(398, 402):
            if q[k] > arr:
                z3 = z3 + 1
        zz3 = (z3 / 5) * 100
        tz3.append(zz3)
        for k in range(438, 442):
            if q[k] > arr:
                z4 = z4 + 1
        zz4 = (z4 / 5) * 100
        tz4.append(zz4)
        for k in range(478, 482):
            if q[k] > arr:
                z5 = z5 + 1
        zz5 = (z5 / 5)*100
        tz5.append(zz5)
        for k in range(610,614):
            if q[k] > arr:
                z6 = z6 + 1
        zz6 = (z6 / 5) * 100
        tz6.append(zz6)
        for k in range(758, 762):
            if q[k] > arr:
                z7 = z7 + 1
        zz7 = (z7 / 5) * 100
        tz7.append(zz7)

    da1 = np.array(da)

    for j in range(0, 80):
        y = 0
        for i in range(0, 144):
            if da1[:, j][i] > arr:
                y = y + 1
        yy = (y / 144)*100
        pz.append(round(yy))

    for i in range(0,144):
        ii=i/6
        time.append(int(ii))
    for i in range(0,24):
        time1.append(i)
    for i in range(0,80) :
        d = x[1]["freq"][i]/1000000
        pzx.append(d)

    u1 = []
    u2 = []
    u3 = []
    u4 = []
    u5= []
    u6 = []
    u7 = []
    u8 = []
    u9 = []
    n = 6
    n4=1
    m1 = [tz1[i:i + n] for i in range(0, len(tz1), n)]
    m2 = [tz2[i:i + n] for i in range(0, len(tz2), n)]
    m3 = [tz3[i:i + n] for i in range(0, len(tz3), n)]
    m4 = [tz4[i:i + n] for i in range(0, len(tz4), n)]
    m5 = [tz5[i:i + n] for i in range(0, len(tz5), n)]
    m6 = [tz6[i:i + n] for i in range(0, len(tz6), n)]
    m7 = [tz7[i:i + n] for i in range(0, len(tz7), n)]
    m8 = [tz[i:i + n4] for i in range(0, len(tz), n4)]
    m9 = [tz0[i:i + n4] for i in range(0, len(tz0), n4)]
    for i in range(0, 24):
        c = 0
        for j in range(0, n):
            c = c + m1[i][j]
        cc = (c/n)
        u1.append(round(cc))
    for i in range(0, 24):
        c = 0
        for j in range(0, n):
            c = c + m2[i][j]
        cc = (c/n)
        u2.append(round(cc))
    for i in range(0, 24):
        c = 0
        for j in range(0, n):
            c = c + m3[i][j]
        cc = (c/n)
        u3.append(round(cc))
    for i in range(0, 24):
        c = 0
        for j in range(0, n):
            c = c + m4[i][j]
        cc = (c/n)
        u4.append(round(cc))
    for i in range(0, 24):
        c = 0
        for j in range(0, n):
            c = c + m5[i][j]
        cc = (c/n)
        u5.append(round(cc))
    for i in range(0, 24):
        c = 0
        for j in range(0, n):
            c = c + m6[i][j]
        cc = (c/n)
        u6.append(round(cc))
    for i in range(0, 24):
        c = 0
        for j in range(0, n):
            c = c + m7[i][j]

        cc = (c/n)
        u7.append(round(cc))
    for i in range(0, 144):
        c = 0
        for j in range(0, n4):
            c = c + m8[i][j]
        cc = (c / n4)
        u8.append(round(cc))
    for i in range(0, 144):
        c = 0
        for j in range(0, n4):
            c = c + m9[i][j]

        cc = (c / n4)
        u9.append(round(cc))

    q1 =dict(zip(time1, u1))
    q2 =dict(zip(time1, u2))
    q3 =dict(zip(time1, u3))
    q4 =dict(zip(time1, u4))
    q5 =dict(zip(time1, u5))
    q6 =dict(zip(time1, u6))
    q7 =dict(zip(time1, u7))

    pz2=[]
    timee = []
    for i in range(0, 144):
        timee.append(i)
    n11 = 18
    m11 = [timee[i:i + n11] for i in range(0, len(timee), n11)]
    for j in range(0, 801):
        for k in range(0, 8):
            y = 0
            for i in m11[k]:
                if da1[:, j][i] > arr:
                    y = y + 1
            yy = (y / 18) * 100
            pz2.append(yy)
    n2 = 8
    m22 = [pz2[i:i + n2] for i in range(0, len(pz2), n2)]
    pz1 = []
    pzx1=[]
    for i in range(0, 801):
        for j in range(0, 8):
            q = [j, i, round(m22[i][j])]
            pz1.append(q)
    for i in range(0,801) :
        d = x[1]["freq"][i]/1000000
        pzx1.append(d)

    # n3 = 60
    # m3 = [timee[i:i + n3] for i in range(0, len(timee), n3)]
    # s1 = []
    # s2 = []
    # s3 = []
    # s4 = []
    # s5 = []
    # s6 = []
    # s7 = []
    #
    # for i in range(0, 24):
    #     k = 0
    #     for j in m3[i]:
    #         if x[j]["spectrum"][28] > arr:
    #             k = k + 1
    #     z = (k / 60) * 100
    #     s1.append(round(z))
    #
    # for i in range(0, 24):
    #     k = 0
    #     for j in m3[i]:
    #         if x[j]["spectrum"][152] > arr:
    #             k = k + 1
    #     z = (k / 60) * 100
    #     s2.append(round(z))
    #
    # for i in range(0, 24):
    #     k = 0
    #     for j in m3[i]:
    #         if x[j]["spectrum"][360] > arr:
    #             k = k + 1
    #     z = (k / 60) * 100
    #     s3.append(round(z))
    # for i in range(0, 24):
    #     k = 0
    #     for j in m3[i]:
    #         if x[j]["spectrum"][440] > arr:
    #             k = k + 1
    #     z = (k / 60) * 100
    #     s4.append(round(z))
    # for i in range(0, 24):
    #     k = 0
    #     for j in m3[i]:
    #         if x[j]["spectrum"][480] > arr:
    #             k = k + 1
    #     z = (k / 60) * 100
    #     s5.append(round(z))
    # for i in range(0, 24):
    #     k = 0
    #     for j in m3[i]:
    #         if x[j]["spectrum"][548] > arr:
    #             k = k + 1
    #     z = (k / 60) * 100
    #     s6.append(round(z))
    #
    # for i in range(0, 24):
    #     k = 0
    #     for j in m3[i]:
    #         if x[j]["spectrum"][760] > arr:
    #             k = k + 1
    #     z = (k / 60) * 100
    #     s7.append(round(z))
    #
    # g1 = dict(zip(time1, s1))
    # g2 = dict(zip(time1, s2))
    # g3 = dict(zip(time1, s3))
    # g4 = dict(zip(time1, s4))
    # g5 = dict(zip(time1, s5))
    # g6 = dict(zip(time1, s6))
    # g7 = dict(zip(time1, s7))

    pjz = []
    max = []
    min = []
    for i in range(0, 801):
        pj = 0
        for j in range(0, 144):
            pj = da1[:, i][j] + pj
        zzz = round(pj / 144) + 107
        pjz.append(zzz)

    for i in range(0, 801):
        ma = -200
        for j in range(0, 144):
            if da1[:, i][j] > ma:
                ma = da1[:, i][j]
        max.append(round(ma) + 107)
    for i in range(0, 801):
        mi = 0
        for j in range(0, 144):
            if da1[:, i][j] < mi:
                mi = da1[:, i][j]
        min.append(round(mi) + 107)

    return render(request, 'zhanyongdu.html', context={"data30": time,"data31": pzx,"data32": u8,"data33": pz,"data34": u9 ,"data35": q1,"data36": q2,"data37":q3,"data38": q4 ,"data39": q5,"data40": q6,"data41": q7,"data42": time1,"data43": pz1,"data44": pzx1,"data45": pjz,"data46": max,"data47": min,})


def wenda(request):
    if request.method == "POST":
        img = request.FILES.get("upfile", None)
        print('cccccccccccccccccccccccc',type(img))
        path=settings.BASE_DIR
        with open(path+"\\static\\"+"\\voices\\"+"myvoices.wav", "wb") as f:
            for line in img.chunks():
                f.write(line)

        request = listen()
        n=Turing(request)
        hecheng(n)
    return HttpResponse("Hello world ! ")



APP_ID = '22997837'
API_KEY = 'bIHCz5kD9BnDQ4U14zeewtvT'
SECRET_KEY = 'Qz1cTUBNoYFpghYdq0dZm7KyOgGX1lQg'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

def listen():
    # 读取录音文件
    path = settings.BASE_DIR
    with open(path + "\\static\\" + "\\voices\\" + "myvoices.wav", 'rb') as fp:
        voices = fp.read()
    try:
        # 参数dev_pid：1536普通话(支持简单的英文识别)、1537普通话(纯中文识别)、1737英语、1637粤语、1837四川话、1936普通话远场
        result = client.asr(voices, 'wav', 16000, {'dev_pid': 1537, })
        # result = CLIENT.asr(get_file_content(path), 'wav', 16000, {'lan': 'zh', })
        # print(result)
        # print(result['result'][0])
        # print(result)
        result_text = result["result"][0]
        print("you said: " + result_text)
        return result_text
    except KeyError:
        print("KeyError")



def Turing(text_words=""):
    req = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": text_words
            },

            "selfInfo": {
                "location": {
                    "city": "北京",
                    "province": "北京",
                    "street": "车公庄"
                }
            }
        },
        "userInfo": {
            "apiKey": turing_api_key,  # 你的图灵机器人apiKey
            "userId": "Nieson"  # 用户唯一标识(随便填, 非密钥)
        }
    }

    req["perception"]["inputText"]["text"] = text_words
    response = requests.request("post", api_url, json=req, headers=headers)
    response_dict = json.loads(response.text)

    result = response_dict["results"][0]["values"]["text"]
    print("AI Robot said: " + result)
    return result

def hecheng(str=""):
    print("baiduVoiceGenerate: V1.0, by Guanagwei_Jiang, 20181121")
    path = settings.BASE_DIR
    result = client.synthesis(str, 'zh', 1, {'vol': 5, 'per': 4})

    if not isinstance(result, dict):
        with open(path + "\\static\\" + "\\voice\\" +'temp.mp3', 'wb') as f:
            f.write(result)

def wenda1(request):
        return render(request, 'wenda.html',)