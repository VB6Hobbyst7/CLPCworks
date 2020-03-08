# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 22:52:42 2020

@author: zhangxi
"""

import pandas as pd

def decypto(authentication,year,month,day):
    import datetime as dt
    import numpy as np
    
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

d=[d for d in range(1,32)]
m=[m for m in range(1,13)]

decyptogram=pd.DataFrame(index=d,columns=m)
year=2020
for i in m:
    for j in d:
        result=decypto(77,year,i,j)
        decyptogram.iloc[j-1,i-1]=result
