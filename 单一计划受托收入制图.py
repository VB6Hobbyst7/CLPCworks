# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 10:40:32 2021

@author: zhangxi
"""
#=======================================================================
#==Date:==          ==Author:==                 ==description==
# 2021-1-22           zhangxi                  单一计划受托分布制图
#=======================================================================

import pandas as pd
import matplotlib.pyplot as plt
#/绘制财务分析报告中管理费收入总体变动情况表/
this_path='E:/OneDrive/国寿养老工作/财务部工作/财务分析/财务收入分析/'
origin=pd.read_excel(this_path+'plotting.xlsx',sheet_name="单一计划受托")

pdt=list(set(origin['单一计划受托']))
pdt.sort()
origin.set_index('单一计划受托',inplace=True)
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

color_dict['淮北矿业']='steelblue'
color_dict['淮南矿业']='orangered'
color_dict['皖北煤电']='tan'
color_dict['马钢']='coral'
color_dict['安徽中烟']='g'
color_dict['铜陵有色']='orange'
color_dict['新华传媒']='mediumslateblue'
color_dict['古井']='b'
color_dict['安徽能源']='darkgoldenrod'

color_dict['安徽邮政']='slategray'
color_dict['省联社']='lightgray'
color_dict['歙县电力']='grey'
color_dict['徽商银行']='grey'


fig,ax1=plt.subplots()
ax1.set_ylabel('单一计划受托（万元）',fontsize=20)
plt.ylim(0,1600)
#柱状图
for p in pdt:
    plt.bar(x=range(len(bar_tab.index)),height=bar_tab.loc[:,p],width=0.6,\
            bottom=bar_bottom_tab.loc[:,p],label=p,color=color_dict[p])
plt.legend(loc='upper right',ncol=8,fontsize=14)
ax1.yaxis.grid(True)
ax2=ax1
#标记年度合计数
ax2=plt.plot(range(len(x_labels)),origin.loc['年度合计',:],"r")
for s in range(len(x_labels)):
    plt.text(s,origin.iloc[-2,s]+30,round(origin.iloc[-2,s],2),fontsize=24)
#标记年度增长率
for s in range(len(x_labels)-1):
    plt.text((s+s+1)/2,(origin.iloc[-2,s]+origin.iloc[-2,s+1])/2+65,"(%s)" %origin.iloc[-1,s+1],color='r',fontsize=16,style='italic')
#标记柱状图的百分比
for s in range(len(x_labels)):
    for p in range(len(pdt)):
        if percent_tab.iloc[s,p]>0.04:
            plt.text(s-0.08,bar_bottom_tab.iloc[s,p]+bar_tab.iloc[s,p]/2,'{:.2%}'.format(percent_tab.iloc[s,p]),fontsize=20,color='k')
        
plt.xticks(range(len(x_labels)),labels=x_labels,fontsize=24)
plt.yticks(fontsize=18)

