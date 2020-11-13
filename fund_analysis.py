# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 14:21:25 2020
v1.0 has finished on 2020-2-18
@author: zhangxi
个养销售分析
"""

import pandas as pd
import numpy as np
import os
import datetime
import time
import functools
import sys

#对函数执行时的计时器
def timer(func):
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        start_time = time.time()
        func(*args,**kwargs)
        end_time = time.time()
        print('函数运行时间为：%.2fs' % (end_time - start_time))
    return wrapper

#取得完整的产品周期，预备制作全寿命大账户
def whole_date(pdtinfo):          
    date1=pdtinfo['CONTRACTENDDATE'].dropna()
    date1=pd.to_datetime(date1)
    date1=list(date1.sort_values())
    year_pdt_duedate=datetime.timedelta(days=365)+datetime.datetime.now()
    st_date=date1[0]
    end_date=date1[len(date1)-1]
    if year_pdt_duedate>end_date:
        end_date=year_pdt_duedate
    date_series=pd.date_range(start=st_date,end=end_date)
    date_series=date_series.strftime('%Y-%m-%d')
    return date_series

#对个养销售记录表格记录进行汇总、清洗
def tab_processing(pdtinfo):
    original=pd.DataFrame()
    for root,dirs,files,in os.walk(db_path,topdown=True):
        for i in files:
            temp=(os.path.join(root,i))
            df1=pd.read_csv(temp)
            original=pd.concat([original,df1],axis=0,join="outer")
    
    original=original.drop(['FUND_ACCT2'],axis=1)
    original=original.merge(pdtinfo,how="left",on='FUND_NAME')
    
    title_raw=pd.read_excel(cardre_path+"Title.xlsx",squeeze=True)
    title=list(title_raw)
    refine=pd.DataFrame(original,columns=title)
    refine["ACK_MONEY"]=refine["ACK_MONEY"].str.replace(",",'')
    refine["ACK_MONEY"]=refine["ACK_MONEY"].astype('float')
    refine['DUE_DATE']=refine['CONTRACTENDDATE'].map(str)+refine['REDEEM_DATE'].map(str)
    refine['DUE_DATE']=refine['DUE_DATE'].str.replace('nan','')
    refine["DUE_DATE"]=pd.to_datetime(refine["DUE_DATE"])
    refine["ACK_DATE"]=pd.to_datetime(refine["ACK_DATE"])
    refine['REFERID']=refine['REFERID'].str.upper()
    refine.dropna(how='all',inplace=True)
    return refine

@timer
def Acc_gen(raw_tab,path,a):
    f=raw_tab
    f['FUND_CLASS']=f['FUND_NAME']
    
    f.loc[f['FUND_CODE']=='CL8010','FUND_CLASS']='月月盈'
    f.loc[f['FUND_CODE']=='CL8010','FUND_ZBXS']=1/12
    f.loc[f['FUND_CODE']=='CL8012','FUND_CLASS']='半年盈'
    f.loc[f['FUND_CODE']=='CL8012','FUND_ZBXS']=1/2
    f.loc[f['FUND_CODE']=='CL8013','FUND_CLASS']='年年盈'
    f.loc[f['FUND_CODE']=='CL8013','FUND_ZBXS']=1
    f.loc[f['FUND_CODE']=='CL8016','FUND_CLASS']='广源366A'
    f.loc[f['FUND_CODE']=='CL8016','FUND_ZBXS']=1
    f.loc[f['FUND_CODE']=='CL8017','FUND_CLASS']='嘉年188'
    f.loc[f['FUND_CODE']=='CL8017','FUND_ZBXS']=1/2
    f.loc[f['FUND_CODE']=='CL8018','FUND_CLASS']='年年利'
    f.loc[f['FUND_CODE']=='CL8018','FUND_ZBXS']=1
    f.loc[f['FUND_CODE']=='CL8020','FUND_CLASS']='广园366'
    f.loc[f['FUND_CODE']=='CL8020','FUND_ZBXS']=1
    
    f.loc[~f['FUND_CODE'].isin(['CL8010','CL8012','CL8013','CL8016','CL8017','CL8018','CL8020']),'FUND_CLASS']='封闭型'
    
    f.loc[f['AGENCY_NAME']=="徽商银行",'SALE_COMPANY_NAME_FEE']='徽商银行'
    f['performance']=f['ACK_MONEY']*f['FUND_ZBXS']/10000
    
    district=set(f['CT_REFER'])
    channel=set(f['SALE_COMPANY_NAME_FEE'])
    district.remove(np.nan)
    
    f['REFERID'].fillna(value='anonym',inplace=True)
    
    cust={}
    feature={}
    feature_d={}
    #样本分组的特征值矩阵
    alter_matrix=[[''         ,''              ,'客户姓名*产品名称*地市名称*分支机构*推荐人代码'],
                  ['FUND_ACCT','CUST_NAME'     ,'产品名称*推荐人代码'],
                  ['REFERID'  ,'CUSTNAME_REFER','客户姓名*产品名称'],
                  ['CT_REFER' ,''              ,'客户姓名*产品名称*分支机构'],
                  ['SALE_COMPANY_NAME_FEE',''  ,'客户姓名*产品名称*地市名称*分支机构*推荐人代码']
                  ]
    alter_para1=alter_matrix[a][0]
    alter_para2=alter_matrix[a][1]
    alter_para3=alter_matrix[a][2]
    general_tab=pd.DataFrame()
    
    if a==0:
        cust={'总账账户':" "}
    elif a==3:
        for dst in district:
            cust[dst]=""
    elif a==4:
        for chl in channel:
            cust[chl]=""
    else:
        cust=dict(zip(f[alter_para1],f[alter_para2]))
    
    #注意字典列表要去掉nan,不然会报错
    cust_list=list(cust.keys())
    
    for i in range(len(cust_list)):
        print(i,cust_list[i])
        try:
            if a==1:              #按样本的特征矩阵筛选出小表
                f_temp_raw=f.loc[f.FUND_ACCT==cust_list[i]]
            elif a==2:
                f_temp_raw=f.loc[f.REFERID==cust_list[i]]
            elif a==0:
                f_temp_raw=f
            elif a==3:
                f_temp_raw=f.loc[f.CT_REFER==cust_list[i]]
            elif a==4:
                f_temp_raw=f.loc[f.SALE_COMPANY_NAME_FEE==cust_list[i]]
            
            cust_temp=cust_list[i]
            Acct_prs=pd.DataFrame()
            f_temp=f_temp_raw[['ACK_DATE','DUE_DATE','FUND_NAME','CUST_NAME',
                               'ACK_MONEY','REFERID','CT_REFER','CR_REFER',
                               'SALE_COMPANY_NAME_FEE']]
            
            for itm in range(len(f_temp)):
                f_temp1=f_temp.iloc[itm]
                acct_temp=pd.DataFrame(index=['A','D'],columns=['日期',alter_para3,'购买','赎回','结余'])
                
                acct_temp.iloc[0,0]=f_temp1['ACK_DATE']
                acct_temp.iloc[1,0]=f_temp1['DUE_DATE']
                
                if a==1:
                    acct_temp.iloc[0,1]='%s*%s' %(f_temp1['FUND_NAME'],f_temp1['REFERID'])
                    acct_temp.iloc[1,1]='%s*%s' %(f_temp1['FUND_NAME'],f_temp1['REFERID'])
                elif a==2:
                    acct_temp.iloc[0,1]='%s*%s' %(f_temp1['CUST_NAME'],f_temp1['FUND_NAME'])
                    acct_temp.iloc[1,1]='%s*%s' %(f_temp1['CUST_NAME'],f_temp1['FUND_NAME'])
                elif a==0:
                    acct_temp.iloc[0,1]='%s*%s*%s*%s*%s' %(f_temp1['CUST_NAME'],f_temp1['FUND_NAME'],f_temp1['CT_REFER'],f_temp1['CR_REFER'],f_temp1['REFERID'])
                    acct_temp.iloc[1,1]='%s*%s*%s*%s*%s' %(f_temp1['CUST_NAME'],f_temp1['FUND_NAME'],f_temp1['CT_REFER'],f_temp1['CR_REFER'],f_temp1['REFERID'])
                elif a==3:
                    acct_temp.iloc[0,1]='%s*%s*%s' %(f_temp1['CUST_NAME'],f_temp1['FUND_NAME'],f_temp1['CR_REFER'])
                    acct_temp.iloc[1,1]='%s*%s*%s' %(f_temp1['CUST_NAME'],f_temp1['FUND_NAME'],f_temp1['CR_REFER'])
                elif a==4:
                    acct_temp.iloc[0,1]='%s*%s*%s*%s*%s' %(f_temp1['CUST_NAME'],f_temp1['FUND_NAME'],f_temp1['CT_REFER'],f_temp1['CR_REFER'],f_temp1['REFERID'])
                    acct_temp.iloc[1,1]='%s*%s*%s*%s*%s' %(f_temp1['CUST_NAME'],f_temp1['FUND_NAME'],f_temp1['CT_REFER'],f_temp1['CR_REFER'],f_temp1['REFERID'])
            
                acct_temp.iloc[0,2]=f_temp1['ACK_MONEY']/10000
                acct_temp.iloc[1,3]=f_temp1['ACK_MONEY']/10000
            
                Acct_prs=pd.concat([Acct_prs,acct_temp],axis=0,join='outer')
                
            Acct_prs['日期']=Acct_prs['日期'].map(lambda x:x.strftime("%Y/%m/%d"))
            Acct_prs.fillna(value=0,inplace=True)
            Acct_prs.sort_values(by=["日期"],ascending=[True],inplace=True)
            Acct_prs.reset_index(inplace=True,drop=True)
            
            for bls in range(len(Acct_prs)):
                if bls==0:
                    Acct_prs.iloc[0,4]=Acct_prs.iloc[0,2]-Acct_prs.iloc[bls,3]
                else:
                    Acct_prs.iloc[bls,4]=Acct_prs.iloc[bls-1,4]+Acct_prs.iloc[bls,2]-Acct_prs.iloc[bls,3]
            
            feature[cust_temp]=Acct_prs['结余'].max()
            rec_date_ind=Acct_prs[Acct_prs['结余']==feature[cust_temp]].index[-1]
            feature_d[cust_temp]=Acct_prs.iloc[rec_date_ind,0]
            
            Acct_prs.to_excel("g:/pdt/account/%s-%s.xlsx" %(cust_temp,cust.get(cust_temp)))
            s_temp=pd.Series([cust_temp,cust.get(cust_temp),feature.get(cust_temp),feature_d.get(cust_temp)])
            general_tab=general_tab.append(s_temp,ignore_index=True)
            general_tab.sort_values(by=[2],ascending=False,inplace=True)
            
        except OSError:
            pass
        continue
    # 生成透视表
    if a==3 or a==4:
        city_pivot=pd.pivot_table(f,values=['performance'],index=[alter_para1],columns=['FUND_CLASS'],aggfunc=np.sum)
    elif a==1 or a==2:
        city_pivot=pd.pivot_table(f,values=['performance'],index=[alter_para2],columns=['FUND_CLASS'],aggfunc=np.sum)
    else:
        city_pivot=pd.DataFrame()

    city_pivot.to_excel("%sGeneral_pivot.xlsx" %path)
    
    general_tab.rename(columns={0:'账户编码',1:'账户名称',2:'账户最大值',3:'最大值最新日期'},inplace=True)
    general_tab.to_excel("%sgeneral.xlsx" %path)
    print('理论应生成的账户数：%s 个' % len(cust_list))
    
    return
    
#分析程序主模块
#选择分析的类型----------------------------------------------
a=input('请选择需要生成的账户分组类型：\n0-总账户\n1-客户个人账户\n2-推荐人账户\n3-寿险地市账户\n4-销售渠道账户\n>>>')
if a in ["0","1","2","3","4"]:
    print("开始执行分析...")
else:
    print("BE CAREFUL:请输入合法的账户类型代码")
    sys.exit()
#-----------------------------------------------------------
db_path="E:/OneDrive/Python工作/CLPCworks/database"
cardre_path="E:/OneDrive/Python工作/CLPCworks/"
pdtinfo=pd.read_csv(cardre_path+"产品基本信息查询.csv")
pdtinfo=pdtinfo.rename(columns=lambda x:x.replace('C_FUNDNAME','FUND_NAME'))
pdtinfo=pdtinfo[3:]    #前三条是月月盈、半年盈等，有重复

whole_date=whole_date(pdtinfo)
tab_refine=tab_processing(pdtinfo)
tab_refine.to_csv(cardre_path+'grand_tab.csv')
#account_raw=pd.DataFrame(index=whole_date)

#类SQL查询
#tab_refine=tab_refine[tab_refine['COMPANY_REFER'].isin(['养老险公司'])]
#tab_refine=tab_refine[tab_refine['FUND_ACCT'].isin(['CL1000063547','CL1000007334'])]
#tab_refine=tab_refine.loc[tab_refine.CUSTNAME_REFER=="张曦"]
#tab_refine=tab_refine[tab_refine['ACK_DATE']>'2019-12-31']
#tab_refine=tab_refine[tab_refine['ACK_DATE']<'2019-06-30']


#debug
#debug_print=tab_refine.loc[tab_refine.FUND_ACCT=='abnoraml_acct']
#debug_print.to_excel(cardre_path+'debug_print.xlsx')

to_anal=tab_refine
path='g:/pdt/account/'
f=os.listdir(path)
for files in f:
    os.remove(path+files)

print("*REPORT*path:%s-%s files have been removed" %(path,len(f)))
Acc_gen(to_anal,cardre_path,int(a))
to_anal.to_excel(path+'analyse.xlsx')