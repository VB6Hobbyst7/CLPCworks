# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 08:56:39 2020

@author: zhangxi
"""
import pandas as pd
import pymysql
import numpy as np
import os
import datetime
import time
import functools
import sys
import re
from gadgets import timer

import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt



#月累积柱状图&总额线图
this_path='E:/OneDrive/国寿养老工作/财务部工作/财务分析/财务收入分析/'
origin=pd.read_excel(this_path+'三栏账数据源.xlsx',sheet_name='数据源',dtype={'日期':str,'业务摘要':str,'凭证号':str})
    
cost_account='业务招待费'

cost=origin[origin.二级科目==cost_account]

cost['科目余额计算列']=cost['科目余额计算列']*-1/10000
for index,row in cost.iterrows():
    
    if re.search('冲销(\d*)号凭证',cost.loc[index,'业务摘要']):
        acc_num=re.search('冲销(\d*)号凭证',cost.loc[index,'业务摘要']).group(1)
        temp_index="%s-%s" %(cost.loc[index,'年度'],acc_num)
        
        temp_dpt=cost[cost.凭证索引==temp_index]['可辨认的成本中心'].values
        cost.loc[index,'可辨认的成本中心']=temp_dpt
        
pt=cost.pivot_table('科目余额计算列',index=['年度',"月度"],columns='可辨认的成本中心',aggfunc=np.sum)
pt.fillna(0,inplace=True)
dpt=['综合管理部','市场一部','市场二部','市场三部','职业年金部','业务运营部','财务会计部']

index_1=pt.index.levels[0]
index_2=[1,2,3,4,5,6,7,8,9,10,11,12]
col=pt.columns
multi_index=[]
for i in index_1:
    for j in index_2:
        multi_index.append((i,j))
ptt=pd.DataFrame(index=multi_index,columns=col)
for index,row in ptt.iterrows():
    ptt.loc[index,'年度']=(index[0])
    ptt.loc[index,'月度']=(index[1])
ptt.set_index(['年度','月度'],drop=True,inplace=True)

a=set(pt.index)
b=set(ptt.index)
c=b-a
dff=pd.DataFrame(index=c,columns=col)
pt=pd.concat([pt,dff],axis=0,join='outer')
pt.reset_index(inplace=True)
pt.sort_values(by=['年度','月度'],ascending=True,inplace=True)

pt['月度']=pt['月度'].astype(int).astype(str)
pt['年度']=pt['年度'].astype(int).astype(str)

pt.set_index(['年度','月度'],drop=True,inplace=True)

pt=pt[dpt]           #pivot_tab
pct=pt.copy()        #pivot_cumsum_tab
#制作累积柱状图的bottom
pct.iloc[:,0]=0
for i in range(len(pct)):
    for j in range(1,len(pct.columns)):
        pct.iloc[i,j]=pct.iloc[i,j-1]+pt.iloc[i,j-1]

#预处理x轴的标签
x_label=[]
for i in range(len(pt.index)):
    if pt.index[i][1]=='1':
        x_label.append("%s\n%s" %(pt.index[i][1],pt.index[i][0]))
    else:
        x_label.append("%s" %(pt.index[i][1]))

plt.rcParams['font.sans-serif']=['SimHei']#这两句作用为防止中文乱码
plt.rcParams['axes.unicode_minus']=False

fig,ax1=plt.subplots()
ax1.set_ylabel('当月金额')

for dpt in pt.columns.values:
    plt.bar(x=range(len(pt.index)),height=pt.loc[:,dpt],bottom=pct.loc[:,dpt],label=dpt)
    
plt.legend(loc='upper left',ncol=7)

#按年求出累积数并画图
pt['本月求和']=pt.sum(axis=1)
pt['当年累积求和']=pt['本月求和'].groupby('年度').cumsum()
ax2=ax1.twinx()
ax2.set_ylabel('当年累积金额')
ax2=plt.plot(range(len(pt.index)),pt['当年累积求和'],'r-.',label='当年累积')
for s in range(len(pt.index)):
    if (s+1)%3==0:
        plt.text(s,pt.iloc[s,-1]+1,round(pt.iloc[s,-1],2))
        
plt.legend(loc='upper left',bbox_to_anchor=(0,0.96))
plt.xticks(range(len(pt.index)),labels=x_label,fontsize=12,rotation=45)
