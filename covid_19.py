#!/usr/bin/env python
# coding: utf-8


import requests
import time
import numpy as np
import pandas as pd
import pymysql
import datetime

def load_date(s):
    mon,day,year = s.split('/')
    return '20'+year+'-'+mon+'-'+day

def get_data(data):
    #亚洲国家
    country = ['Afghanistan', 'Armenia', 'Azerbaijan', 'Bahrain', 'Bangladesh', 'Bhutan', 
           'Brunei', 'Burma', 'Cambodia', 'China', 'Cyprus', 'Georgia', 'India', 
           'Indonesia', 'Iran', 'Iraq', 'Israel', 'Japan', 'Jordan', 'Kazakhstan', 
           'Korea, South', 'Kuwait', 'Kyrgyzstan', 'Laos', 'Lebanon', 'Malaysia', 
           'Maldives', 'Mongolia', 'Nepal', 'Oman', 'Pakistan', 'Philippines', 
           'Qatar', 'Saudi Arabia', 'Singapore', 'Sri Lanka', 'Syria', 'Tajikistan', 
           'Thailand', 'Timor-Leste', 'Turkey', 'United Arab Emirates', 'Uzbekistan', 'Vietnam', 'Yemen']
    
    # 转换为dataframe格式，行是国家，列是日期
    df = pd.DataFrame(columns=data[0].split(','))
    for i in range(1,len(data[1:])):
        data[i] = data[i].replace('&quot;','"')
        tmp = data[i].split(',')
        if(len(tmp)>df.shape[1]):
            tmp = [tmp[0]]+[tmp[1]+','+tmp[2]]+tmp[3:]
        tmp = [' ' if x=='' else x for x in tmp]
        tmp = tmp[:4] + [int(x) for x in tmp[4:]]
        if(tmp[1]=='"Korea, South"'):
            tmp[1] = 'Korea, South'
        df.loc[i-1] = tmp
    X1 = df.iloc[:,1]
    X2 = df.iloc[:,4:]
    X = pd.concat([X1,X2],axis=1)
    X = X[X['Country/Region'].isin(country)].groupby('Country/Region').sum()
    
    return X

def Update_table(col, X):
    conn = pymysql.connect(host='192.168.118.131', port=3306, user='root', password='123', db='COVID')
    dates = np.array(X.columns[1:])
    days = X.iloc[0].index.tolist()
    for i in range(len(X)):
        country = X.iloc[i].name
        nums = np.array(X.iloc[i])
        for j in range(len(days)):
            if(col=='Confirm'):
                sql = "insert into Confirm (Country,Date,Confirm) values ('%s','%s','%s')"%(country,load_date(days[j]),nums[j])
                with conn.cursor() as cursor:
                    cursor.execute(sql)
            else:
                sql = "update Confirm set %s='%s' where Country='%s' and Date='%s'"%(col,nums[j],country,load_date(days[j]))
                print(sql)
                with conn.cursor() as cursor:
                    cursor.execute(sql)
    conn.commit()
    conn.close()
    
def Find_last(col):
    conn = pymysql.connect(host='192.168.118.131', port=3306, user='root', password='123', db='COVID')
    with conn.cursor() as cursor:
        cursor.execute('select max(Date) from Confirm where %s is not null '%(col))
        last_date = cursor.fetchone()[0]
    conn.close()
    return last_date


if __name__ == '__main__':

    url_base = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
    url_confirmed = url_base + 'time_series_covid19_confirmed_global.csv'
    url_deaths = url_base + 'time_series_covid19_deaths_global.csv'
    url_recovered = url_base + 'time_series_covid19_recovered_global.csv'

    Dict = {url_confirmed: 'Confirm', url_deaths: 'Deaths', url_recovered: 'Recovered'}
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    for url, col in Dict.items():
        print("%s:"%(col))
        # requests请求数据
        while True:  # 一直循环，直到访问站点成功
            try:
                responce = requests.get(url=url, timeout=(3.05, 20))
                break
            except requests.exceptions.ConnectionError:
                print('ConnectionError -- please wait 3 seconds')
                time.sleep(3)
            except requests.exceptions.ChunkedEncodingError:
                print('ChunkedEncodingError -- please wait 3 seconds')
                time.sleep(3)
            except:
                print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
                time.sleep(3)
        # 处理数据，挑出亚洲国家的所有日期数据
        data = get_data(responce.text.split('\n'))

        # 数据库中table表 最新的日期
        last_date = Find_last(col)

        # git数据源 最新的日期
        new_year, new_mon, new_day = [int(x) for x in load_date(data.columns[-1]).split('-')]
        new_date = datetime.date(new_year, new_mon, new_day)

        predays = -1000000
        # 如果数据库中col字段已经有数据
        if (last_date != None):
            # 计算数据库中col需要更新几天
            predays = -1 * (new_date - last_date).days

        if (predays == 0):
            print('%s已是最新' % (col))
        else:
            Update_table(col, data.iloc[:, predays:])
            print("%s更新完成\n最新日期:%s" % (col, load_date(data.columns[-1])))
