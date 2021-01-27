# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 17:11:20 2021

@author: zhangxi
"""

#/分析总公司提供的养老金产品收入情况/

import pandas as pd
import re

investor_list=['国寿','太平','嘉实','海富通','泰康','建信','平安','工银瑞信','中金',
               '华夏','南方','易方达']
customer_in_province_list=['安徽中烟','淮南矿业','铜陵有色','古井','中铁四局',
                           '.*烟草.*安徽.*','安徽.*电力','安徽新华','徽商集团',
                           '皖北煤电','安徽.*能源','安徽.*高速',"徽商银行",'淮北矿业',
                           '马钢'
                           ]
customer_out_province_list=['南方航空','中.*广核','民生银行','中国.*电.*建.*',
                            '中国国旅','中国航空','云南.*农.*信.*社.*','北京农.*商.*行',
                            '厦门港务','四川九洲','天津津融','太原供水','建信养老',
                            '昆明铁路局',"河钢.*唐山",'海航','深圳.*机场','深圳.*水务',
                            '神华','镇海石化建安','青岛四方','北京控股'
                            ]
fund_character_list=['受托直投','固收','债权','信托']


customer_total_list=customer_in_province_list+customer_out_province_list

path='E:/OneDrive/国寿养老工作/财务部工作/财务分析/财务收入分析/投管客户收入明细（总部区分）0715.xlsm'
origin=pd.read_excel(path,sheet_name="养老金明细")

origin['期间']=origin['期间'].astype(str)
origin['年度']=''
origin['月度']=''
origin['客户名称']=''
origin['组合']=''
origin['是否外销组合']=''
origin['产品类型']=''
origin['产品简称']=''
origin['产品规范简称']=''
origin["托管行"]=''
origin['投管人']=''
origin['组合特征']=''
for index,row in origin.iterrows():
    origin.loc[index,'年度']=row['期间'][:4]
    origin.loc[index,'月度']=row['期间'][5:7]
    if row['计划类型']=='集合计划':                     #第一分枝，集合计划
        origin.loc[index,'客户名称']=row['客户全称']
        pattern='企业年金集合计划'
        temp=re.search(pattern,row['客户全称'])
        if temp:
            dot1=temp.span()[1]
            origin.loc[index,'组合']=row['客户全称'][dot1:]
            nm_temp=row['客户全称'][:dot1]
            dot1=re.search(pattern,row['客户全称']).span()[0]
            #/分出托管行/
            pattern="(.*?)(行|光大|民生|中信)"
            temp=re.search(pattern,nm_temp)
            if temp:
                origin.loc[index,'托管行']=temp.group(0)
                dot2=temp.span()[1]
            #/分出计划名称/
                nm_temp=row['客户全称'][dot2:dot1]
                pattern='\A银行'
                if re.search(pattern,nm_temp):
                    nm_temp=nm_temp[re.search(pattern,nm_temp).span()[1]:]
                origin.loc[index,'客户名称']=nm_temp
            #/判断投管人/
            for investor in investor_list:
                if investor in origin.loc[index,'组合']:
                    origin.loc[index,"投管人"]=investor
                    break
            if not('国寿' or '') in origin.loc[index,"投管人"]:
                origin.loc[index,'是否外销组合']="Y"
            else:
                origin.loc[index,'是否外销组合']="N"
            #/判断集合计划的组合特征
            for character in fund_character_list:
                if character in origin.loc[index,'组合']:
                    origin.loc[index,"组合特征"]=character
                    break
                else:
                    origin.loc[index,"组合特征"]='标准'
        #/完善国寿集合计划信息
        pattern="永.+"
        temp=re.search(pattern,origin.loc[index,'客户名称'])
        if temp:
            origin.loc[index,'是否外销组合']="N"
            origin.loc[index,'投管人']='国寿'
    elif row['计划类型']=='职业年金':                      #第二分枝：职业年金
        pattern='职业年金计划'
        #/分出组合名称/
        dot1=re.search(pattern,row['客户全称']).span()[1]
        origin.loc[index,'组合']=row['客户全称'][dot1:]
        nm_temp=row['客户全称'][:dot1]
        #/分出托管行/
        pattern=".+(?=安徽省)"
        temp=re.search(pattern,nm_temp)
        if temp:
            origin.loc[index,'托管行']=temp.group(0)
        #/分出计划名称/
        pattern='安徽省.+号'
        nm_temp=re.search(pattern,nm_temp).group(0)
        origin.loc[index,'客户名称']=nm_temp
        nm_temp=re.search(pattern,nm_temp)
        
    elif row['计划类型']=='单一计划':                     #第三分枝，单一计划
        pattern='企业年金计划'
        #/分出组合名称/
        dot1=re.search(pattern,row['客户全称']).span()[1]
        origin.loc[index,'组合']=row['客户全称'][dot1:]
        nm_temp=row['客户全称'][:dot1]
        dot1=re.search(pattern,row['客户全称']).span()[0]
        #/分出托管行/
        pattern="(.*?)(行|光大|民生|中信)"
        temp=re.search(pattern,nm_temp)
        if temp:
            origin.loc[index,'托管行']=temp.group(0)
            dot2=temp.span()[1]
        #/分出计划名称/
            nm_temp=row['客户全称'][dot2:dot1]
            pattern='\A银行'
            if re.search(pattern,nm_temp):
                nm_temp=nm_temp[re.search(pattern,nm_temp).span()[1]:]
            origin.loc[index,'客户名称']=nm_temp
    #/分枝判断结束
    #/开始处理养老金产品名称
    nm_temp=row['基金名称']
    pattern='国寿养老(.*)养老金产品'
    nm_temp=re.search(pattern,nm_temp)
    fund=nm_temp.group(1)

    if re.search('存款型',fund):
        origin.loc[index,'产品类型']='存款型'
        origin.loc[index,'产品简称']=fund[:re.search('存款型',fund).span()[0]]
    elif re.search('股票型',fund):
        origin.loc[index,'产品类型']='股票型'
        origin.loc[index,'产品简称']=fund[:re.search('股票型',fund).span()[0]]
    elif re.search('固(定)?收(益)?型',fund):
        origin.loc[index,'产品类型']='固收型'
        origin.loc[index,'产品简称']=fund[:re.search('固(定)?收(益)?型',fund).span()[0]]
    elif re.search('混合型',fund):
        origin.loc[index,'产品类型']='混合型'
        origin.loc[index,'产品简称']=fund[:re.search('混合型',fund).span()[0]]
    elif re.search('信托',fund):
        origin.loc[index,'产品类型']='信托型'
        origin.loc[index,'产品简称']=fund[:re.search('信托',fund).span()[0]]
    elif re.search('基础设施债权',fund):
        origin.loc[index,'产品类型']='基础设施债权'
        origin.loc[index,'产品简称']=fund[:re.search('基础设施债权',fund).span()[0]]
    elif re.search('货币',fund):
        origin.loc[index,'产品类型']='货币型'
        origin.loc[index,'产品简称']=fund[:re.search('货币',fund).span()[0]]
    elif re.search('债券型',fund):
        origin.loc[index,'产品类型']='债券型'
        origin.loc[index,'产品简称']=fund[:re.search('债券型',fund).span()[0]]
    elif re.search('优先股',fund):
        origin.loc[index,'产品类型']='优先股型'
        origin.loc[index,'产品简称']=fund[:re.search('优先股',fund).span()[0]]
    elif re.search('保险产品型',fund):
        origin.loc[index,'产品类型']='保险型'
        origin.loc[index,'产品简称']=fund[:re.search('保险产品型',fund).span()[0]]
    origin.loc[index,'产品规范简称']='%s-%s' %(origin.loc[index,'产品简称'],origin.loc[index,'产品类型'])
    
    #/判断非集合计划的标的是否是外销养老金产品/
    if origin.loc[index,'计划类型']!='集合计划':
        if '国寿' in origin.loc[index,'组合']:
            origin.loc[index,"是否外销组合"]='N'
        else:
            origin.loc[index,"是否外销组合"]='Y'
    #/判断组合特征/
        for character in fund_character_list:
                if character in origin.loc[index,'组合']:
                    origin.loc[index,"组合特征"]=character
                    break
                else:
                    origin.loc[index,"组合特征"]='标准'
    #/判断投管人/
        for investor in investor_list:
            if investor in origin.loc[index,'组合']:
                origin.loc[index,"投管人"]=investor
                break
    #/判断客户简称
        for customer in customer_total_list:
            if re.search(customer,origin.loc[index,'客户名称']):
                customer=customer.replace('*',"")
                customer=customer.replace('.','')
                origin.loc[index,"客户名称"]=customer
                break
        
path='E:/OneDrive/国寿养老工作/财务部工作/财务分析/财务收入分析/养老金产品分析表.xlsx'
origin.to_excel(path,index=False)