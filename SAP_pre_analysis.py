# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 12:19:34 2020

@author: zhangxi
"""
import functools
import pandas as pd
import numpy as np
import re
from gadgets import voucher_relating
from gadgets import cash_flow_tab_gen
this_path='E:/OneDrive/国寿养老工作/财务部工作/财务分析/财务收入分析/'

origin=pd.read_excel(this_path+'三栏账数据源.xlsx',sheet_name='数据源',dtype={'日期':str,'业务摘要':str,'凭证号':str})
origin['业务摘要'].fillna('(此行原始记录空白)',inplace=True)

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

#银行存款流水记录，收付实现制的预处理
bank_account=origin[origin['一级科目']=='银行存款']
bank_journal=[]
for index,row in bank_account.iterrows():
    if pd.isnull(row['凭证号'])==False:
        bank_journal.append(str(row['年度'])+str(row['凭证号']))
#bank_journal只是列表，会有重复的
        
for index,row in origin.iterrows():
    #生成科目代码和科目名称的字典
    origin.loc[index,'日期']=origin.loc[index,'日期'][:10]

    if row[0] not in AccCode.keys():
        temp='%s-%s-%s' %(row['一级科目'],row['二级科目'],row['三级科目'])
        temp=temp.replace('-nan','')
        temp1=str(row[0])
        temp1='%s-%s-%s' %(temp1[:4],temp1[4:6],temp1[6:])
        AccCode[temp1]=temp
    
    if len(str(origin.loc[index,'月度']))==1:
        origin.loc[index,'月度']='0%s' %(origin.loc[index,'月度'])
    else:
        origin.loc[index,'月度']='%s' %(origin.loc[index,'月度'])
    
    origin.loc[index,'凭证索引']='%s-%s' %(origin.loc[index,'年度'],origin.loc[index,'凭证号'])
    
    txt_temp=row["业务摘要"]
    nm_res=""
    if re.search('单据号:',txt_temp):
        filenum=re.search('单据号:',txt_temp)
        filenum=txt_temp[filenum.span()[1]:]
        origin.loc[index,'公文系统单据号']=filenum
        
    if row['科目代码']==6041010000:#职业年金收入-受托费
        nm=txt_temp[4:-9]
        origin.loc[index,'可辨认的客户名称']=nm
        origin.loc[index,'可辨认的受托/账管客户类型']="职业年金受托"
        
        if re.search('\d(.*)月',txt_temp):
            dt=re.search('\d(.*)月',txt_temp)
            dt=dt.group(0)[:-1]
            if dt=='13':
                dt='12'              #SAP会出现虚拟的13月，对年度财务数据进行调整
            origin.loc[index,'月度']=dt
    
    if row['科目代码']==6041020000:#职业年金收入-投管
        nm=txt_temp
        if re.search('职业年金--(.*)|业绩报酬--(.*)',txt_temp):
            nm=re.search('职业年金--(.*)|业绩报酬--(.*)',txt_temp)
            nm=nm.group(0)[6:]
            origin.loc[index,'可辨认的客户名称']=nm
            origin.loc[index,'可辨认的受托/账管客户类型']="职业年金投管"
        if re.search('业绩报酬',txt_temp):
            origin.iloc[index,3]='业绩报酬'
        else:
            origin.iloc[index,3]='常规投管'
    
    if row['科目代码']==1130090000:#应收管理费-职业年金受托费
        if re.search('(?<=确认(应|实)收).*(?=受托费)',txt_temp):
            nm_res=re.search('(?<=确认(应|实)收).*(?=受托费)',txt_temp).group(0)
        elif re.search('(?<=安徽省).*(?=年金计划)',txt_temp):
            nm_res=txt_temp
        origin.loc[index,'可辨认的客户名称']=nm_res
    
    if row['科目代码']==6039020100 or row['科目代码']==1130020000: #企业年金收入-账管、应收管理费-账管
        nm_pattern=re.compile('(?<=确认(应|实)收).*(?=账管费)')
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
            
            origin.loc[index,'可辨认的客户名称']=nm_res
            if nm_res in ['铜陵有色','叉车集团','古井集团','新华传媒']:
                origin.loc[index,'可辨认的受托/账管客户类型']="单一计划"
            else:
                origin.loc[index,'可辨认的受托/账管客户类型']="集合计划"
            
    if row['科目代码']==6039010000 or row['科目代码']==1130010000:#企业年金收入-受托
        nm_pattern=re.compile('(?<=确认(应|实)收).*(?=受托费)')
        nm_raw=nm_pattern.search(txt_temp) 
        #常规的受托费项目
        if not nm_raw is None:
            nm_raw=nm_raw.group(0)
            nm_res=nm_raw
            origin.loc[index,'可辨认的客户名称']=reduct(nm_res)
            #处理调整的表述
            nm_head=re.compile('\A调整')
            nm_hd=nm_head.match(nm_raw)
            if not nm_hd is None:
                slc=nm_hd.span()[1]
                nm_res=nm_raw[slc:]
                origin.loc[index,'可辨认的客户名称']=reduct(nm_res)
            origin.loc[index,'可辨认的受托/账管客户类型']='单一计划'
            #处理集合计划
            nm_clt=re.compile('.*(?=企业年金集合计划)')
            nm_clt_pln=nm_clt.search(nm_raw)
            if not nm_clt_pln is None:
                nm_raw=nm_clt_pln.group(0)
                nm_res=nm_raw[2:]
                origin.loc[index,'可辨认的客户名称']=nm_res
                origin.loc[index,'可辨认的受托/账管客户类型']="集合计划"
        else:
            origin.loc[index,'可辨认的受托/账管客户类型']='税金及其他调整'
    
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
                origin.loc[index,'可辨认的客户名称']=reduct(nm_res)
            else:                       #还有几行不带银行的倒霉玩意
                nm_res=nm_raw
                origin.loc[index,'可辨认的客户名称']=reduct(nm_res)
            origin.loc[index,'可辨认的受托/账管客户类型']='单一计划'
    
    if row['科目代码']==6051020500: #其他业务收入-养老保障
        if '团体' in txt_temp:
            origin.iloc[index,3]='团养'
        else:
            origin.iloc[index,3]='个养'
            
    if row['科目代码']==6421000000 or row['科目代码']==2201000000: 
        #业管费-手续费支出/应付款-应付手续费
        
        if re.search('寿',txt_temp):
            origin.loc[index,'可辨认的成本中心']='寿险'
        if re.search('财.?险',txt_temp):
            origin.loc[index,'可辨认的成本中心']='财险'
        if re.search('手续费',txt_temp):
            origin.loc[index,'可辨认的受托/账管客户类型']='手续费'
        if re.search('推动',txt_temp) or re.search('奖励',txt_temp):
            origin.loc[index,'可辨认的受托/账管客户类型']='推动奖励'
        
        if origin.loc[index,'可辨认的受托/账管客户类型']=='推动奖励' or\
           origin.loc[index,'可辨认的受托/账管客户类型']=='手续费'and\
           pd.isnull(origin.loc[index,'可辨认的成本中心'])==True:
           origin.loc[index,'可辨认的成本中心']="寿险"
        
        #现金账索引出实际支付的手续费
        if str(row['年度'])+str(row['凭证号']) in bank_journal:
            origin.loc[index,'现金流量标注']='实际支付的手续费'
    
    #现金账索引引出实际支付的薪酬
    if '应付职工薪酬' in row['一级科目']:
        if str(row['年度'])+str(row['凭证号']) in bank_journal:
            origin.loc[index,'现金流量标注']='实际支付的薪酬'
    
    #其他应付款中代职工支付的社保等公积金等费用
    try:
        if str(row['科目代码'])[:4]=="2241" and ('职工部分' in row['三级科目']):
            if str(row['年度'])+str(row['凭证号']) in bank_journal:
                origin.loc[index,'现金流量标注']='实际支付的薪酬'
    except:
        pass     
    
    #对业管费科目处理，业管费一级科目代码6601
    #从业管费的摘要中提取业管费的部门名称
    if str(row['科目代码'])[:4]=="6601":
        try:
            if re.search('(市场|(职业)|业务|财务|综合|运营).*部',txt_temp):
                
                nm_temp=re.search('(市场|(职业)|业务|财务|综合|运营).*部',txt_temp).group(0)
                if nm_temp=="综合部":
                    nm_temp="综合管理部"
                elif nm_temp=='运营部':
                    nm_temp="业务运营部"
                origin.loc[index,'可辨认的成本中心']=nm_temp
                
        except:
            pass
        #对业管费的现金流量标注
        if str(row['年度'])+str(row['凭证号']) in bank_journal:
            origin.loc[index,'现金流量标注']='实际支付的业管费-%s' %(row['二级科目'])
    
    #对应交税费科目处理，应交税费一级科目代码2221
    if str(row['科目代码'])[:4]=="2221" and\
        str(row['年度'])+str(row['凭证号']) in bank_journal:
        #处理企业所得税
        if str(row['二级科目'])=='企业所得税':
            origin.loc[index,'现金流量标注']='实际支付的企业所得税'
        #处理个人所得税
        elif str(row['二级科目'])=='个人所得税':
            origin.loc[index,'现金流量标注']='实际支付的个人所得税'
        #处理增值税及附加
        else:
            origin.loc[index,'现金流量标注']='实际支付的增值税金及附加'
    
    #对固定资产科目处理，固定资产一级科目代码1601
    if str(row['科目代码'])[:4]=="1601":
        if str(row['年度'])+str(row['凭证号']) in bank_journal:
            origin.loc[index,'现金流量标注']='实际支付的固定资产'
    
    #对营业外收入处理，营业外收入一级科目代码6301
    if str(row['科目代码'])[:4]=="6301":
        if str(row['年度'])+str(row['凭证号']) in bank_journal:
            origin.loc[index,'现金流量标注']='应收应付变动-其他'
    
    #对其他应收款处理,一级科目代码1221
    if str(row['科目代码'])[:4]=="1221":
        if str(row['二级科目'])=="押金及保证金":
            if str(row['年度'])+str(row['凭证号']) in bank_journal:
                origin.loc[index,'现金流量标注']='实际支付的押金及保证金'
        if str(row['二级科目'])=="员工":
            if str(row['年度'])+str(row['凭证号']) in bank_journal:
                origin.loc[index,'现金流量标注']='实际支付的员工借款'
        
    #对其他应付款处理，一级科目2241
    try:
        if str(row['科目代码'])[:4]=="2241": 
            if str(row['年度'])+str(row['凭证号']) in bank_journal:
                if(re.search('工程|设备',row['二级科目'])):
                    origin.loc[index,'现金流量标注']='实际支付的固定资产'
                if(re.search('租赁',row['二级科目'])):
                    origin.loc[index,'现金流量标注']='实际支付的租赁费'
                if row['二级科目']=='其他':
                    pass
    except:
        pass     
    
    #对应收管理费处理，一级科目1130
    if str(row['科目代码'])[:4]=="1130":
        if str(row['年度'])+str(row['凭证号']) in bank_journal:
            origin.loc[index,'现金流量标注']='实际收到的管理费收入'
    
    #对利息收入处理，科目代码6111101100
    if row['科目代码']==6111101100:
        if str(row['年度'])+str(row['凭证号']) in bank_journal:
            origin.loc[index,'现金流量标注']='实际收到的存款利息'
    
    #对待摊费用处理，一级科目1401
    if str(row['科目代码'])[:4]=="1401":
        if "租赁" in row['二级科目']:
            if str(row['年度'])+str(row['凭证号']) in bank_journal:
                origin.loc[index,'现金流量标注']='实际支付的租赁费'
            
    #对系统往来处理，一级科目1161
    if str(row['科目代码'])[:4]=="1161":
        if str(row['年度'])+str(row['凭证号']) in bank_journal:
            origin.loc[index,'现金流量标注']='实际支付的总公司往来款'
            
    #对税金及附加处理，一级科目6401
    if str(row['科目代码'])[:4]=="6401":
        if str(row['年度'])+str(row['凭证号']) in bank_journal:
            origin.loc[index,'现金流量标注']='实际支付的其他税金'
    
    #对预收账款处理，一级科目2210
    if str(row['科目代码'])[:4]=="2210":
        if str(row['年度'])+str(row['凭证号']) in bank_journal:
            origin.loc[index,'现金流量标注']='实际收到的管理费收入'
    
    #对其他应收款-其他的处理，科目代码1221990000
    #对请他应付款-其他的处理，科目代码
    #这块要区分是与业务相关的还是代收代付的难度有点大，就先全归集到不计入现金流量科目

    if row['科目代码']==1221990000 or row['科目代码']==2241990000:
        if str(row['年度'])+str(row['凭证号']) in bank_journal:
            origin.loc[index,'现金流量标注']='应收应付变动-其他'
        #利用应收应付实际经济业务备查字典进行修正的工作在gadgets.cash_flow_tab_gen()中进行

origin['科目余额计算列']=origin["贷方"]-origin["借方"]
origin.to_excel(this_path+'三栏账数据源.xlsx',sheet_name='数据源',index=False)
relating_db=this_path+'三栏账数据源.xlsx'

voucher_relating(relating_db) #用公文号关联凭证号

        

