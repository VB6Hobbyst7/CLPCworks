# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 12:19:34 2020

@author: zhangxi
"""

import pandas as pd
import re

origin=pd.read_excel('F:/desktop_temp/AccSheet.xlsx')
AccCode={}

for index,row in origin.iterrows():
    #生成科目代码和科目名称的字典
    if row[0] not in AccCode.keys():
        temp='%s-%s-%s' %(row['一级科目'],row['二级科目'],row['三级科目'])
        temp=temp.replace('-nan','')
        temp1=str(row[0])
        temp1='%s-%s-%s' %(temp1[:4],temp1[4:6],temp1[6:])
        AccCode[temp1]=temp

    #对摘要的正则化表达处理
    txt_temp=row["业务摘要"]
    
    if row['科目代码']==6041010000:#职业年金收入-受托费
        nm=txt_temp[4:-9]
        origin.iloc[index,-2]=nm
        
        if re.search('\d(.*)月',txt_temp):
            dt=re.search('\d(.*)月',txt_temp)
            dt=dt.group(0)[:-1]
            if dt=='13':
                dt='12'              #SAP会出现虚拟的13月，对年度财务数据进行调整
            origin.iloc[index,-6]=dt
    
    if row['科目代码']==6041020000:#职业年金收入-投管费
        nm=txt_temp
        if re.search('职业年金--(.*)',txt_temp):
            nm=re.search('职业年金--(.*)',txt_temp)
            nm=nm.group(0)[6:]
            origin.iloc[index,-2]=nm
    
    if row['科目代码']==6039020100:#企业年金收入-账管费
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

            if nm_res[-6:]=="农村商业银行":
                nm_res=nm_res[:-6]+"农商行"
            
            if nm_res=="怀宁农村合作银行":
                nm_res="怀宁农商行"
            if nm_res=="淮北市供水总公司":
                nm_res="淮北市供水"
            if nm_res=="铜陵市规划勘测设计研究院":
                nm_res="中汇规划勘测设计研究院"
            
            origin.iloc[index,-2]=nm_res
            if nm_res in ['铜陵有色金属集团控股','叉车集团','古井集团']:
                origin.iloc[index,-1]="单一计划"
            else:
                origin.iloc[index,-1]="集合计划"
            
                
                    
            
dbp=origin.loc[origin.科目代码==6039020100]


        


        

