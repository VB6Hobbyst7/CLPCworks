# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 12:19:34 2020

@author: zhangxi
"""
import functools
import pandas as pd
import numpy as np
import re

origin=pd.read_excel('E:/OneDrive/国寿养老工作/财务部工作/财务分析/财务收入分析/三栏账数据源.xlsx'
                     ,sheet_name='数据源',dtype={'日期':str,'业务摘要':str})
#origin['业务摘要']=origin['业务摘要'].astype("str")
AccCode={}

def reduct(nm):#对企业年金收入-受托-单一计划客户名称进行精简，可能需要定期维护
    #单一计划客户列表
    sg_cstm=['徽商银行','歙县供电','古井','安徽省能源','农村信用社','安徽省邮政',
             '安徽中烟','新华传媒','淮南矿业','淮北矿业','皖北煤电','马钢',
             '铜陵有色']
    for n in sg_cstm:
        if n in nm:
            nm=n
            break
    if nm=='歙县供电':
        nm='歙县电力'
    elif nm=='安徽省能源':
        nm='安徽能源'
    elif nm=='安徽省邮政':
        nm='安徽邮政'
    elif nm=='农村信用社':
        nm='省联社'
    
    return nm
#代理费科目切片
agent_fee=origin[origin.科目代码==6421000000]


for index,row in origin.iterrows():
    #生成科目代码和科目名称的字典
    origin.loc[index,'日期']=origin.loc[index,'日期'][:10]

    if row[0] not in AccCode.keys():
        temp='%s-%s-%s' %(row['一级科目'],row['二级科目'],row['三级科目'])
        temp=temp.replace('-nan','')
        temp1=str(row[0])
        temp1='%s-%s-%s' %(temp1[:4],temp1[4:6],temp1[6:])
        AccCode[temp1]=temp
    
    txt_temp=row["业务摘要"]
    if re.search('单据号:',txt_temp):
        filenum=re.search('单据号:',txt_temp)
        filenum=txt_temp[filenum.span()[1]:]
        origin.iloc[index,14]=filenum
    print(index,txt_temp)
        
    if row['科目代码']==6041010000:#职业年金收入-受托费
        nm=txt_temp[4:-9]
        origin.iloc[index,-2]=nm
        
        if re.search('\d(.*)月',txt_temp):
            dt=re.search('\d(.*)月',txt_temp)
            dt=dt.group(0)[:-1]
            if dt=='13':
                dt='12'              #SAP会出现虚拟的13月，对年度财务数据进行调整
            origin.iloc[index,-6]=dt
    
    if row['科目代码']==6041020000:#职业年金收入-投管
        nm=txt_temp
        if re.search('职业年金--(.*)|业绩报酬--(.*)',txt_temp):
            nm=re.search('职业年金--(.*)|业绩报酬--(.*)',txt_temp)
            nm=nm.group(0)[6:]
            origin.iloc[index,-2]=nm
        if re.search('业绩报酬',txt_temp):
            origin.iloc[index,3]='业绩报酬'
        else:
            origin.iloc[index,3]='常规投管'
    
    if row['科目代码']==6039020100:#企业年金收入-账管
        nm_pattern=re.compile('(?<=确认应收).*(?=账管费)')
        nm_raw=nm_pattern.search(txt_temp)
        if not nm_raw is None:    
            nm_raw=nm_raw.group(0)
            
            if len(nm_raw)<9:
                nm_res=nm_raw
            else:
                re_tail=re.compile('(股份)?有限')
                re_head=re.compile('\A安徽(省)?')
                
                nm_hd=re_head.match(nm_raw)
                if not nm_hd is None:
                    slc=nm_hd.span()[1]
                    nm_res=nm_raw[slc:]
                else:
                    nm_res=nm_raw
                    
                nm_tl=re_tail.search(nm_res)
                if not nm_tl is None:
                    slc=nm_tl.span()[0]
                    nm_res=nm_res[:slc]
                else:
                    nm_res=nm_res
            
            rural_bank=re.compile('农村.*银行')
            nm_rb=rural_bank.search(nm_res)
            if not nm_rb is None:
                nm_res=nm_res[:-6]+"农商行"
            #例外：简称优化
            if nm_res=="淮北市供水总公司":
                nm_res="淮北市供水"
            if nm_res=="铜陵市规划勘测设计研究院":
                nm_res="中汇规划勘测设计研究院"
            if nm_res=="铜陵有色金属集团控股":
                nm_res="铜陵有色"
            
            origin.iloc[index,-2]=nm_res
            if nm_res in ['铜陵有色','叉车集团','古井集团','新华传媒']:
                origin.iloc[index,-1]="单一计划"
            else:
                origin.iloc[index,-1]="集合计划"
            
    if row['科目代码']==6039010000:#企业年金收入-受托
        nm_pattern=re.compile('(?<=确认应收).*(?=受托费)')
        nm_raw=nm_pattern.search(txt_temp) 
        #常规的受托费项目
        if not nm_raw is None:
            nm_raw=nm_raw.group(0)
            nm_res=nm_raw
            origin.iloc[index,-2]=reduct(nm_res)
            #处理调整的表述
            nm_head=re.compile('\A调整')
            nm_hd=nm_head.match(nm_raw)
            if not nm_hd is None:
                slc=nm_hd.span()[1]
                nm_res=nm_raw[slc:]
                origin.iloc[index,-2]=reduct(nm_res)
            origin.iloc[index,-1]='单一计划'
            #处理集合计划
            nm_clt=re.compile('.*(?=企业年金集合计划)')
            nm_clt_pln=nm_clt.search(nm_raw)
            if not nm_clt_pln is None:
                nm_raw=nm_clt_pln.group(0)
                nm_res=nm_raw[2:]
                origin.iloc[index,-2]=nm_res
                origin.iloc[index,-1]="集合计划"
        else:
            origin.iloc[index,-1]='税金及其他调整'
    
        #单一计划受托财产分析
        nm_tail=re.compile('.*(?=企业年金计划受托财产)')
        nm_tl=nm_tail.search(txt_temp)
        if not nm_tl is None:
            nm_raw=nm_tl.group(0)
            nm_head=re.compile('(?=行).*')#去掉词头的银行，但也有工行、中行的字样
            nm_hd=nm_head.search(nm_raw)
            if not nm_hd is None:
                slc=nm_hd.span()[0]
                nm_res=nm_raw[slc+1:]
                origin.iloc[index,-2]=reduct(nm_res)
            else:                       #还有几行不带银行的倒霉玩意
                nm_res=nm_raw
                origin.iloc[index,-2]=reduct(nm_res)
            origin.iloc[index,-1]='单一计划'
    
    if row['科目代码']==6051020500: #其他业务收入-养老保障
        if '团体' in txt_temp:
            origin.iloc[index,3]='团养'
        else:
            origin.iloc[index,3]='个养'
            
    if row['科目代码']==6421000000: #手续费
        
        if re.search('寿',txt_temp):
            origin.loc[index,'可辨认的客户名称']='寿险'
        if re.search('财.?险',txt_temp):
            origin.loc[index,'可辨认的客户名称']='财险'
        if re.search('手续费',txt_temp):
            origin.loc[index,'可辨认的受托/账管客户类型']='手续费'
        if re.search('推动',txt_temp) or re.search('奖励',txt_temp):
            origin.loc[index,'可辨认的受托/账管客户类型']='推动奖励'
            if origin.loc[index,'可辨认的客户名称']=='':
                origin.loc[index,'可辨认的客户名称']='寿险'
        #if re.search('冲',txt_temp):
            #_num=re.search('\d+',txt_temp).group(0)
           # print(txt_temp,file_num)


origin['科目余额计算列']=origin["贷方"]-origin["借方"]

dbp=origin.loc[origin.科目代码==6051020500]
origin.to_excel('E:/OneDrive/国寿养老工作/财务部工作/财务分析/财务收入分析/三栏账数据源.xlsx',sheet_name='数据源',index=False)
        


        

