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
import shutil

#===================重要的Excel文件自动备份到本地SD卡和git备份仓库=================
def code_back_up():
    code_list=pd.read_excel('E:/OneDrive/Python工作/CLPCworks/VBA_PY_Code_List.xlsx')
    code_list['file_name']=code_list['文件名称'].str.cat(code_list['后缀'])
    
    for index,row in code_list.iterrows():
        try:
            shutil.copyfile(row['文件所在目录']+row['file_name'],'G:/备份仓库/Excel_VBA_files/'+row['file_name'])
            shutil.copyfile(row['文件所在目录']+row['file_name'],row['git备份目录']+row['file_name'])
        except:
            print("failed:",row['文件所在目录']+row['file_name'])
            pass
#==================================计时器===================================
def timer(func):
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        start_time = time.time()
        func(*args,**kwargs)
        end_time = time.time()
        print('函数%s运行时间为：%.2fs' % (func.__name__,end_time - start_time))
    return wrapper

#========================关联数据库中invoice表的凭证号============================
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
#=========================表格日期切片器（切成字典）=============================
def date_cutting_dict(begin_year,begin_month,end_year,end_month):
    res={}
    
    if begin_year==end_year:  #不跨年的切片
        if begin_month>end_month:
            begin_month,end_month=end_month,begin_month
        
        month=[i for i in range(begin_month,end_month+1)]
        res[begin_year]=month
    elif begin_year<end_year:  #跨年的切片
        year=[i for i in range(begin_year,end_year)]
        month=[i for i in range(1,13)]
        for y in year:
            res[y]=month
        
        month=[i for i in range(begin_month,13)]
        res[begin_year]=month
        month=[i for i in range(1,end_month+1)]
        res[end_year]=month
        
    else:
        print('起始年度不应大于结束年度！')
    return res
#==========================利用字典对应收应付科目的现金流量科目予以修正============
#2020-12-16   SAP应收应付科目，通过人工进行识别干预，调高现金流量表的准确性

def modify_due_account():
    due_memo=pd.read_excel('E:/OneDrive/国寿养老工作/财务部工作/财务分析/财务收入分析/SAP-现金流量切表-其他应收应付款备忘录-字典.xlsx',
                           dtype={'年度':str,'凭证号':str})
    due_memo.dropna(subset=['现金流量标注'],inplace=True)
    due_memo['凭证索引']=due_memo['年度'].str.cat(due_memo['凭证号'])
    memo={}
    memo=dict(zip(due_memo['凭证索引'],due_memo['现金流量标注']))
    return memo

#=================================pandas生成现金流量表============================================
#2020-12-15 只生成现金流量的科目字典，后续和Excel报表编制底稿配合出表
#2020-12-18 增加了查询现金余额，现金流量额的功能
    
@timer
def cash_flow_tab_gen(begin_year,begin_month,end_year=-1,end_month=-1):    #开始结束年月
    #对起始年月缺省值的处理，缺省就是当年当月
    if end_year==-1:
        end_year=begin_year
    if end_month==-1:
        end_month=begin_month
    
    this_path='E:/OneDrive/国寿养老工作/财务部工作/财务分析/财务收入分析/'
    origin=pd.read_excel(this_path+'三栏账数据源.xlsx',sheet_name='数据源',dtype={'日期':str,'业务摘要':str,'凭证号':str})
    mda=modify_due_account()
    
    #按传入的日期对origin进行切片
    by=begin_year
    bm=begin_month
    ey=end_year
    em=end_month
    date_orient=date_cutting_dict(by,bm,ey,em)
    cutting_df=pd.DataFrame()
    res_df=pd.DataFrame()
    for k in date_orient.keys():
        cutting_df=origin[origin['年度'].isin([k])]
        cutting_df=cutting_df[cutting_df['月度'].isin(date_orient.get(k))]
        res_df=pd.concat([res_df,cutting_df],axis=0)
    origin=res_df
    #切片完成
    
    #类现金的科目列表、字典初始化
    cash_flow_dict={}           #现金流量表项目字典
    bank_journal_amount={}      #索引项是现金类金额字典
    cash_like_list=['银行存款']  #*********现金流量的核心列表（重要）***********
    
    #现金类三栏账的切片
    bank_account=origin[origin['一级科目'].isin(cash_like_list)]   
    bank_journal=[]             #涉及现金类（年度+凭证号）的索引列表
    
    #用现金类三栏账表bank_account计算现金类期初期末余额模块
    acc_code=list(set(bank_account['科目代码']))
    bank_account.sort_values(['科目代码','年度'],ascending=True,inplace=True)
    cash_flow_dict['期初现金类余额']=0
    cash_flow_dict['期末现金类余额']=0
    
    for i in range(len(acc_code)):
        bank_acc=bank_account[bank_account.科目代码==acc_code[i]]
        bank_acc.dropna(subset=['凭证号'],inplace=True)
        
        bank_acc.reset_index(drop=True,inplace=True)
        
        a=bank_acc.loc[0,'余额']+bank_acc.loc[0,'科目余额计算列']
        b=bank_acc.loc[len(bank_acc)-1,'余额']
        cash_flow_dict['期初现金类余额']=round(cash_flow_dict['期初现金类余额']+a,2)
        cash_flow_dict['期末现金类余额']=round(cash_flow_dict['期末现金类余额']+b,2)
    a=cash_flow_dict['期初现金类余额']
    b=cash_flow_dict['期末现金类余额']
    #余额取数结束
    for index,row in bank_account.iterrows():
            bank_journal.append(str(row['年度'])+str(row['凭证号']))
    bank_journal_amount=bank_journal_amount.fromkeys(bank_journal,0)
    
    for index,row in bank_account.iterrows():
        if pd.isnull(row['凭证号'])==False:
            bank_journal_amount[str(row['年度'])+str(row['凭证号'])]=bank_journal_amount[str(row['年度'])+str(row['凭证号'])]+row['科目余额计算列']*-1
    
    origin['现金流水额']=''
    origin['索引号']=''
    origin['现金流量标志']=''
    
    for index,row in origin.iterrows():
        origin.loc[index,'索引号']=str(row['年度'])+str(row['凭证号'])
        origin.loc[index,'现金流水额']=bank_journal_amount.get(origin.loc[index,'索引号'])
        if origin.loc[index,'索引号'] in bank_journal:
            origin.loc[index,'现金流量标志']=1
        else:
            origin.loc[index,'现金流量标志']=0
        if row['科目余额计算列']>0 and not(row['借方']<0 or row['贷方']<0):
                                    #排除冲账的可能性
            try:
                origin.loc[index,'现金流量标注']=row['现金流量标注'].replace("支付","收到")
            except:
                pass
    #利用mda字典对应收应付科目现金流量标注做人工修正
    for key in mda:
        origin.loc[origin.索引号==key,'现金流量标注']=mda[key]
    
    current_flows_tab=origin[origin.现金流量标志==1]
    non_current_tab=origin[origin.现金流量标志==0]
    current_flows_tab.drop('现金流量标志',axis=1,inplace=True)
    non_current_tab.drop('现金流量标志',axis=1,inplace=True)
    
    current_flows_tab=current_flows_tab[~current_flows_tab['一级科目'].isin(cash_like_list)]
    current_flows_tab.to_excel('G:/python练习/现金流量项目切表.xlsx')
    non_current_tab.to_excel('G:/python练习/非现金流量项目切表.xlsx')
    
    cash_flow_keys=set(current_flows_tab['现金流量标注'].dropna())
    cash_flow_dict=dict.fromkeys(cash_flow_keys,0)
    
    #特别项目的分类汇总明细处理
    cash_flow_dict['理论计算现金净增加额']=current_flows_tab['科目余额计算列'].sum()
    cash_flow_dict['寿险：手续费']=0
    cash_flow_dict['财险：手续费']=0
    cash_flow_dict['寿险：推动奖励']=0
    cash_flow_dict['实际支付的业管费']=0
    cash_flow_dict['实际收到的业管费']=0
    cash_flow_dict['起始日期']='%s-%s' %(begin_year,begin_month)
    cash_flow_dict['结束日期']='%s-%s' %(end_year,end_month)
    cash_flow_dict['期初现金类余额']=a
    cash_flow_dict['期末现金类余额']=b
    for index,row in current_flows_tab.iterrows():
        if row['现金流量标注'] in cash_flow_dict:
            cash_flow_dict[row['现金流量标注']]=cash_flow_dict[row['现金流量标注']]+round(row['科目余额计算列'],2)
        
        if row['可辨认的成本中心']=='寿险' and row['可辨认的受托/账管客户类型']=='手续费':
            cash_flow_dict['寿险：手续费']=cash_flow_dict['寿险：手续费']+round(row['科目余额计算列'],2)
        if row['可辨认的成本中心']=='财险' and row['可辨认的受托/账管客户类型']=='手续费':
            cash_flow_dict['财险：手续费']=cash_flow_dict['财险：手续费']+round(row['科目余额计算列'],2)
        if row['可辨认的成本中心']=='寿险' and row['可辨认的受托/账管客户类型']=='推动奖励':
            cash_flow_dict['寿险：推动奖励']=cash_flow_dict['寿险：推动奖励']+round(row['科目余额计算列'],2)
        try:
            if re.search('支付的业管费',row['现金流量标注']):
                cash_flow_dict['实际支付的业管费']=cash_flow_dict['实际支付的业管费']+round(row['科目余额计算列'],2)
            if re.search('收到的业管费',row['现金流量标注']):
                cash_flow_dict['实际收到的业管费']=cash_flow_dict['实际收到的业管费']+round(row['科目余额计算列'],2)
        except:
            pass
    #即期支付的租赁费在即期的业管费中体现，现金流量表把租赁费单独拎出来，所以要扣除
    cash_flow_dict['实际收到的业管费']=cash_flow_dict['实际收到的业管费']-cash_flow_dict['实际支付的业管费-租赁费']
    
    cash_flow_items=pd.DataFrame.from_dict(cash_flow_dict,orient='index')
    cash_flow_items.to_excel(this_path+'现金流量项目表-直接法.xlsx')
    
    return 

