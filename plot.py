# -*- coding: utf-8 -*-
"""
Created on Fri Jan  8 17:19:57 2021

@author: zhangxi
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt




#=======================================================================
# ==Date:==          ==Author:==                 ==description==
# 2021-1-22           zhangxi                    绘制财务分析的收入总图
#=======================================================================

#/绘制财务分析报告中管理费收入总体变动情况表/
this_path='E:/OneDrive/国寿养老工作/财务部工作/财务分析/财务收入分析/'
origin=pd.read_excel(this_path+'plotting.xlsx',sheet_name="管理费总收入制图")

pdt=list(set(origin['收入明细']))
pdt.sort()
origin.set_index('收入明细',inplace=True)
origin.loc['年度合计']=origin.sum(axis=0)
origin.loc['年度增长率']=''


for j in range(1,len(origin.columns)):
    temp_rate=(origin.iloc[len(origin)-2,j]-origin.iloc[len(origin)-2,j-1])/origin.iloc[len(origin)-2,j-1]
    temp_rate='%.2f%%' %(temp_rate*100)
    origin.iloc[len(origin)-1,j]=temp_rate
x_labels=[]
y_labels=[]
for i in range(len(origin.columns)):
    x_labels.append('%s' %(origin.columns[i]))
for i in range(len(origin)):
    y_labels.append('%s' %(origin.index[i]))

bar_tab=origin[:-2]
percent_tab=origin[:-1].copy()
for i in range(len(percent_tab)):
    for j in range(len(percent_tab.columns)):
         percent_tab.iloc[i,j]=percent_tab.iloc[i,j]/percent_tab.iloc[-1,j]
percent_tab=percent_tab[:-1]
percent_tab=pd.DataFrame(percent_tab.T,index=percent_tab.columns,columns=percent_tab.index)
#制作bar图的bottom矩阵
bar_bottom_tab=pd.DataFrame().reindex_like(bar_tab)
bar_bottom_tab.iloc[0,:]=0
for i in range(1,len(bar_bottom_tab)):
    for j in range(len(bar_bottom_tab.columns)):
        bar_bottom_tab.iloc[i,j]=bar_bottom_tab.iloc[i-1,j]+bar_tab.iloc[i-1,j]

bar_tab=pd.DataFrame(bar_tab.values.T,index=bar_tab.columns,columns=bar_tab.index)
bar_bottom_tab=pd.DataFrame(bar_bottom_tab.values.T,index=bar_bottom_tab.columns,columns=bar_bottom_tab.index)


plt.rcParams['font.sans-serif']=['SimHei']#这两句作用为防止中文乱码
plt.rcParams['axes.unicode_minus']=False

#绘制累积柱状图

color_dict={}
color_dict['1.企业-受托']='royalblue'
color_dict['2.企业-投资']='steelblue'
color_dict['3.企业-账管']='darkorange'
color_dict['4.职业-受托']='wheat'
color_dict['5.职业-投管']='burlywood'
color_dict['6.养老金产品']='indianred'
color_dict['7.养老保障产品']='salmon'

fig,ax1=plt.subplots()
ax1.set_ylabel('收入金额（万元）',fontsize=20)
#柱状图
for p in pdt:
    plt.bar(x=range(len(bar_tab.index)),height=bar_tab.loc[:,p],width=0.6,\
            bottom=bar_bottom_tab.loc[:,p],label=p,color=color_dict[p])
plt.legend(loc=0,ncol=3,fontsize=16)
ax1.yaxis.grid(True)
ax2=ax1
#标记年度合计数
ax2=plt.plot(range(len(x_labels)),origin.loc['年度合计',:],"r")
for s in range(len(x_labels)):
    plt.text(s,origin.iloc[-2,s]+100,round(origin.iloc[-2,s],2),fontsize=24)
#标记年度增长率
for s in range(len(x_labels)-1):
    plt.text((s+s+1)/2,(origin.iloc[-2,s]+origin.iloc[-2,s+1])/2+200,"(%s)" %origin.iloc[-1,s+1],color='r',fontsize=18,style='italic')
#标记柱状图的百分比
for s in range(len(x_labels)):
    for p in range(len(pdt)):
        if percent_tab.iloc[s,p]>0.02:
            plt.text(s*0.96,bar_bottom_tab.iloc[s,p]+bar_tab.iloc[s,p]/2.8,'{:.2%}'.format(percent_tab.iloc[s,p]),fontsize=20,color='k')
        
plt.xticks(range(len(x_labels)),labels=x_labels,fontsize=24)
plt.yticks(fontsize=18)
