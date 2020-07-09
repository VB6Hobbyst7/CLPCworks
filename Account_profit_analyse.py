# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 08:56:28 2020

@author: zhangxi
"""

import numpy as np
import pandas as pd
import datetime as dt
#读取清洗数据源
data_rw=pd.read_excel('e:/OneDrive/18383资金流水.xlsx',dtype={"证券代码":str},sheet_name="资金流水")
stockholdings=pd.read_excel('e:/OneDrive/18383资金流水.xlsx',sheet_name='持仓明细')
stockholdings=stockholdings.loc[:,['证券代码','最新市值']]
                          
data_rw['证券代码'].fillna("cash",inplace=True)
data_rw['路费']=np.nan
#配股，发新股等的代码清理，未来应做成一个函数
data_rw.loc[data_rw.证券代码=='080589','证券代码']='000589'   #黔轮胎配股
data_rw.loc[data_rw.证券代码=='780916','证券代码']='601916'   #浙江银行申购
data_rw.loc[data_rw.证券代码=='787009','证券代码']='688009'   #通号申购
data_rw.loc[data_rw.证券代码=='787369','证券代码']='688369'   #致远申购
data_rw.loc[data_rw.证券代码=='783233','证券代码']='113032'   #桐昆发债
data_rw.loc[data_rw.证券代码=='733909','证券代码']='110067'   #华安发债
data_rw.loc[data_rw.证券代码=='733711','证券代码']='110066'   #盛屯发债
data_rw.loc[data_rw.证券代码=='370433','证券代码']='123003'   #蓝思发债
data_rw.loc[data_rw.证券代码=='072382','证券代码']='128108'   #蓝帆发债
#########################################

#data_rw['成交日期']=data_rw['成交日期'].astype(dt.datetime)
counter=data_rw['业务名称'].str.split(":",expand=True)
counter.columns=['业务类型','参考证券名称']
data=pd.concat([data_rw,counter],axis=1)

        
money_sum=data_rw.groupby('证券代码').sum()
money_sum=money_sum.loc[:,["发生金额","成交数量"]]
#money_sum['成交价']=money_sum['发生金额']/money_sum['成交数量']

code=list(set(data_rw['证券代码']))


code_dict=dict.fromkeys(code," ")
data.loc[data.业务类型=='银证双边资金蓝补','证券代码']='reserve'

for index,row in data.iterrows():
    code_dict[row['证券代码']]=row['证券名称']
    if type(row['证券名称'])==float:
        code_dict[row['证券代码']]=row['证券代码']
        
    if row['业务类型']=="转托转入":
        data.loc[index,'业务类型']='托管转入'
    if row['业务类型']=="融券购回":
        data.loc[index,'业务类型']='债券赎回'
    if row['业务类型']=="拆出购回":
        data.loc[index,'业务类型']='债券赎回'
    if row['业务类型']=="回购融券":
        data.loc[index,'业务类型']='押入债券'
    #计算路费
    if row['业务类型'] in ['证券买入','证券卖出']:
        data.loc[index,'路费']=data.loc[index,'成交价格']*data.loc[index,'成交数量']+data.loc[index,'发生金额']

code_dict['cash']="资金进出"
code_dict['reserve']='备用金'

commission=data.groupby('证券名称').sum()['路费']
commission=pd.DataFrame(commission)
commission=commission[commission['路费']<0]

print(commission)
print('路费合计：',commission.sum())


#计算逻辑：银行转存+结息=银行转取+理论计算的场内价值
#实际场内价值-理论计算的场内价值=账户的总体盈利
transition=set(data['业务类型'])
banking=set(['银行转存','银行转取','批量利息归本'])
stakeholder=transition-banking


single_stock=data[data['证券代码']=='002140']
inspect=data[data['业务类型'].isin([])]

stock_code_transition=list(set(single_stock['业务类型']))
grand_pivot=pd.pivot_table(data,index=['证券代码'],values=['发生金额'],columns=['业务类型'],aggfunc=np.sum)
grand_pivot.columns=grand_pivot.columns.get_level_values(1)
#merge持仓市值
grand_pivot=grand_pivot.merge(stockholdings,on='证券代码',how='outer')
grand_pivot.set_index('证券代码',inplace=True)

#用证券名称取代证券代码做索引
grand_pivot['证券名称']=''
for i in range(len(grand_pivot)):
    grand_pivot.iloc[i,-1]=code_dict[grand_pivot.index[i]]

grand_pivot.iloc[[-1,-2],:]=grand_pivot.iloc[[-2,-1],:]
grand_pivot.set_index('证券名称',inplace=True)

#制作决算报告
stock_account=grand_pivot.sum(axis=1)
stock_account=stock_account[:-2]
#print('证券盈利行合计：',stock_account.sum())

fund_account=round(grand_pivot.sum(axis=0),2)

fund_transfer=fund_account['托管转入']*-1
fund_interests=fund_account['批量利息归本']
fund_income=fund_account['银行转存']
fund_out=fund_account['银行转取']
fund_computing=fund_transfer+fund_interests+fund_income+fund_out
fund_stake=fund_account['最新市值']

print('         盈亏计算表')
print('==============================')
print(' 存入资金：',format(fund_income,","))
print('+托管转入：',format(fund_transfer,','))
print('+ 结 息 ：',format(fund_interests,","))
print('-转出资金：',format(fund_out*-1,','))
print('==============================')
print('=理论计算的场内价值:',format(round(fund_computing,2),','))
print('-实际的场内价值:',format(fund_stake,','))
print('==============================')
print('=账户总体盈亏：',format(round(fund_stake-fund_computing,2),','))
print('==============================')
print('*理论上盈利应为负数，已做调整')

grand_pivot.to_excel('E:\OneDrive\资金决算分析.xlsx')


