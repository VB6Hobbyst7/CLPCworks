# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 13:09:51 2020

@author: zhangxi
"""

def cyptogram():
    import datetime as dt
    import numpy as np
    import warnings
    warnings.filterwarnings("ignore")
    
    today=dt.datetime.today()
    year=today.year
    month=today.month
    day=today.day
    authentication=77
    if month<4:
        step=(month+10)
    else:
        step=month*2
    tri=np.zeros((step,step+1),int)
    
    for i in range(0,step):
        for j in range(i+1):
            tri[i][0]=(month+year)//day
            tri[j][j]=(year-month)//day
            if i>1 and j<i+1:
                tri[i][j]=tri[i-1][j-1]*(-1)**day+tri[i-1][j]*(authentication+year)//day
    
    cypto_raw1=abs(tri[step-1])
    cypto_raw2=abs(tri[step-2])
    
    if len(cypto_raw1)//2==0:
        l=int(len(cypto_raw1)/2)
    else:
        l=int((len(cypto_raw1)-1)/2)
    
    cypto_1=str(cypto_raw1[l-1:l])[-5:-1]
    cypto_2=str(cypto_raw2[l:l+1])[1:5]
    
    cyptogram='%s-%s' % (cypto_1,cypto_2)
    
    return cyptogram

d=cyptogram()


login=input("输入密码:\n")
if login==d:
    print('验证通过，执行程序\n')
else:
    login=input("密码错误1次，再输入密码:\n")
    if login==d:
        print('验证通过，执行程序\n')
    else:
        input("密码错误2次，再输入密码:\n")
        if login==d:
            print('验证通过，执行程序\n')
        else:
            if login==d:
                print('验证通过，执行程序\n')
            else:
                print('密码错误3次，退出程序')
            
'''
tri[0,step-1]=1
#tri[1,step-1]=0
for i in range(1,step):
    for j in range(2*step-1):
        tri[i][step-1-i]=1
        tri[i][step-1+i]=1
        if i>1 and (step-1-i<j<step-1+i):
            tri[i][j]=tri[i-1][j-1]+tri[i-1][j+1]
'''