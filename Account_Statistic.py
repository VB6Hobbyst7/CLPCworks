# -*- coding: utf-8 -*-
"""
Created on Wed May 27 13:13:54 2020

@author: zhangxi
"""

import pandas as pd
import numpy as np
import datetime

raw_tab=pd.read_excel("E:/OneDrive/国寿养老工作/财务部工作/银行存款日记账/国寿养老安徽分公司银行存款日记账.xlsm",sheet_name="广发基本户")
raw_tab['年']=raw_tab['日期'].dt.year
raw_tab['月']=raw_tab['日期'].dt.month
raw_tab['日']=raw_tab['日期'].dt.day
raw_tab['日期']=raw_tab['日期'].dt.date
raw_tab['贷方']=raw_tab['贷方']
raw_tab['部门']=""
raw_tab=raw_tab.dropna(subset=['日期'])
refine_tab=raw_tab
#四大费用列表
#four_cost=['差旅费','业务招待费','宣传费','会议费']
#refine_tab=refine_tab[refine_tab['对方科目']#.isin(four_cost)]

for index,row in refine_tab.iterrows():
    if type(row['经办部门'])==str:
        if '市场' in row['经办部门']:
            refine_tab.loc[index,"部门"]="市场中心"
        else:
            refine_tab.loc[index,'部门']=refine_tab.loc[index,'经办部门']

#temp=refine_tab.eval('贷方/10000')
department=set(refine_tab['经办部门'])
#refine_tab=refine_tab[refine_tab['部门'].isin(['职业年金部','业务运营部'])]
piovt_tab=refine_tab.pivot_table('贷方',index=['年','月'],columns=['对方科目'],aggfunc='sum',margins=True)
piovt_tab.to_excel("f:\p.xlsx")
#ref=refine_tab.set_index('流转文件号')
#rk=refine_tab.to_dict(orient="list")

f=refine_tab.groupby("部门")['贷方'].median()

