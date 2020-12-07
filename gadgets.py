# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 16:11:32 2020

@author: zhangxi
"""

import functools
import time
import pymysql
import pandas as pd
import numpy as np
import re

#计时器
def timer(func):
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        start_time = time.time()
        func(*args,**kwargs)
        end_time = time.time()
        print('函数%s运行时间为：%.2fs' % (func.__name__,end_time - start_time))
    return wrapper

#关联数据库中invoice表的凭证号
@timer
def voucher_relating(db_account):
    db = pymysql.connect("localhost","root","abcd1234",'clpc_ah')
    cursor = db.cursor()
    
    sql="select  * from invoice where (凭证号 is null or `凭证号`='')"
    cursor.execute(sql)
    rows=cursor.fetchall()
    columnDes = cursor.description #获取连接对象的描述信息
    columnNames = [columnDes[i][0] for i in range(len(columnDes))] #获取列名
    x_tab= pd.DataFrame([list(i) for i in rows],columns=columnNames)
    
    inter_tab=pd.read_excel(db_account,dtype={'凭证号':str})
    inter_tab=inter_tab[['公文系统单据号','凭证号']]
    inter_tab.dropna(subset=['公文系统单据号'],inplace=True)
    
    relating_dict={}
    #制作系统公文号-凭证号字典
    for index,row in inter_tab.iterrows():
        sys_num=re.search('B\d*',row['公文系统单据号'])
        inter_tab.loc[index,'公文系统单据号']=sys_num.group(0)
        relating_dict[sys_num.group(0)]=row['凭证号']
    
    sql1=("UPDATE invoice set 凭证号=%s where 系统公文号=%s;")
    sql2=("UPDATE invoice set 凭证号='---' where 系统公文号='作废';")
    cursor.execute(sql2)
    
    for i in range(len(x_tab)):
        temp=x_tab.loc[i,'系统公文号']
        try:
            sys_num=re.search('B\d*',temp)
            if sys_num:
                cursor.execute(sql1,(relating_dict.get(temp),temp))
        except:
            pass
    
    db.commit()
    cursor.close()
    db.close()
