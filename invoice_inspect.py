# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 12:50:15 2020

@author: zhangxi
"""

import pandas as pd
import re


rw=pd.read_csv('C:/Users/ZhangXi/Desktop/invoice.txt')
rw.columns=['描述文本']
rw['分组标志']=""

grand_tab=pd.DataFrame()
immediate_dict={}
#对原始数据标记分组
flag=0
for i in range(len(rw)):
    text=rw.iloc[i,0]
    if re.search(".*发票查验明细",text):
        flag+=1
        rw.iloc[i,1]=flag
    if re.search(".*任何单位或个人有权拒收并向当地税务机关举报",text):
        rw.iloc[i,1]="aaa"
print("本次共处理%s张发票：" %(flag))
cnts=flag    #获得处理发票的次数counts

flag=""

for i in range(len(rw)):
    if rw.iloc[i,1]!="" and rw.iloc[i,1]!="aaa":
        flag=rw.iloc[i,1]
    if rw.iloc[i,1]=='':
        rw.iloc[i,1]=flag
    if rw.iloc[i,1]=="aaa":
        flag=""


    
    
def iv_clean1(immediate_dict):
#############类专票的处理块#####################
    immediate_dict['发票种类']=test.iloc[3,0]             #0.发票种类
    flag=""
    for i in range(len(test)):
        text=test.iloc[i,0]
        if text=="购":        # 专门用于专票格式的处理购销方
            flag="购"
        elif text=="销":
            flag="销"
        
        items=re.search('(?<=查验次数：).*',text)
        if not items is None:
            immediate_dict['查验次数']=items.group(0)[:3]  #1.查验次数
        items=re.search('(?<=查验时间：).*',text)
        if not items is None:
            immediate_dict['查验时间']=items.group(0)  #2.查验时间
        items=re.search('(?<=发票代码：).*',text)
        if not items is None:
            immediate_dict['发票代码']=items.group(0)  #3.发票代码
        items=re.search('(?<=发票号码：).*',text)
        if not items is None:
            immediate_dict['发票号码']=items.group(0)  #4.发票号码
        items=re.search('(?<=开票日期：).*',text)
        if not items is None:
            immediate_dict['开票日期']=items.group(0)  #5.开票日期
        items=re.search('(?<=校验码：).*',text)
        if not items is None:
            immediate_dict['校验码']=items.group(0)  #6.校验码
        items=re.search('(?<=机器编号：).*',text)
        if not items is None:
            immediate_dict['机器编号']=items.group(0)  #7.机器编号
        items=re.search('(?<=（小写）￥).*',text)
        if not items is None:
            immediate_dict['价税合计']=items.group(0)  #8.价税合计
        items=re.search('价税合计.*',text)
        if not items is None:
            immediate_dict['税额']=test.iloc[i-1,0][1:]  #13.税额
            immediate_dict['不含税金额']=test.iloc[i-2,0][1:]  #14.不含税金额
        
        #判断购买方代码块
        items=re.match('名称.*',text)    #此处用match
        if not items is None and flag=="购":
            immediate_dict['购买方名称']=test.iloc[i+1,0]  #9.购买方名称
        items=re.search('.*纳税人识别号.*',text)
        if not items is None and flag=="购":
            immediate_dict['购买方纳税人识别号']=test.iloc[i+1,0]  #10.购买方纳税人识别号
        items=re.search('.*地址、电话.*',text)
        if not items is None and flag=="购":
            immediate_dict['购买方地址、电话']=test.iloc[i+1,0]  #11.购买方地址、电话
        items=re.search('.*开户行及账号.*',text)
        if not items is None and flag=="购":
            immediate_dict['购买方开户行及账号']=test.iloc[i+1,0]  #11.购买方开户行及账号
        
        #判断销售方代码块
        items=re.search('.*名称.*',text)
        if not items is None and flag=="销":
            immediate_dict['销售方名称']=test.iloc[i+1,0]  #9.销售方名称
        items=re.search('.*纳税人识别号.*',text)
        if not items is None and flag=="销":
            immediate_dict['销售方纳税人识别号']=test.iloc[i+1,0]  #10.销售方纳税人识别号
        items=re.search('.*地址、电话.*',text)
        if not items is None and flag=="销":
            immediate_dict['销售方地址、电话']=test.iloc[i+1,0]  #11.销售方地址、电话
        items=re.search('.*开户行及账号.*',text)
        if not items is None and flag=="销":
            immediate_dict['销售方开户行及账号']=test.iloc[i+1,0]  #12.销售方开户行及账号
        '''
        items=re.search('(?<=代开).*',text)
        if not items is None:
            agent=items.group(0)  #处理代开
            #更新代开发票的企业税号有点问题，回头处理吧
            agt1=re.search('([A-Z]|[0-9])+',agent).group(0) #代开企业税号
            immediate_dict.update({'销售方纳税人识别号':agt1})
            agt2=re.search("(?<=名称:)",agent)
            immediate_dict['销售方名称']=agent[agt2.span()[1]:]   #代开企业名称
        
    #最后清洗商品、劳务信息
        if test.iloc[i,0]=="税额":
            a=i
        if test.iloc[i,0]=="合计":
            b=i
    
    items_row_index=list(range(1,int((b-a-1)/8)+1))
    temp_items=pd.DataFrame(index=items_row_index,columns=["项目","规格型号","单位","数量","单价","金额","税率","税额"])
    j=0
    for i in range(a+1,b):
        temp_items.iloc[divmod(j,8)[0],divmod(j,8)[1]]=test.iloc[i,0]
        j+=1
    immediate_dict['发票明细']=temp_items.to_dict(orient='records') #以字典储存发票业务明细
    '''
    df=pd.DataFrame.from_dict(immediate_dict,orient="index")
    df=df.T
    
    return df

####################卷票的处理块
def iv_clean2(immediate_dict):
    immediate_dict['发票种类']=test.iloc[3,0]             #0.发票种类
    for i in range(len(test)):
        text=test.iloc[i,0]
        
        items=re.search('(?<=查验次数：).*',text)
        if not items is None:
            immediate_dict['查验次数']=items.group(0)[:3]  #1.查验次数
            
        items=re.search('(?<=查验时间：).*',text)
        if not items is None:
            immediate_dict['查验时间']=items.group(0)  #2.查验时间
            
        items=re.search('(?<=发票代码：).*',text)
        if not items is None:
            immediate_dict['发票代码']=items.group(0)  #3.发票代码
            
        items=re.search('(?<=发票号码：).*',text)
        if not items is None:
            immediate_dict['发票号码']=items.group(0)  #4.发票号码
            
        items=re.search('(?<=开票日期：).*',text)
        if not items is None:
            immediate_dict['开票日期']=items.group(0)  #5.开票日期
            
        items=re.search('(?<=校验码：).*',text)
        if not items is None:
            immediate_dict['校验码']=items.group(0)  #6.校验码
            
        items=re.search('(?<=机器编(号|码)：).*',text)
        if not items is None:
            immediate_dict['机器编号']=items.group(0)  #7.机器编号
            
        items=re.search('(?<=（小写）：￥).*',text)
        if not items is None:
            immediate_dict['价税合计']=items.group(0)  #8.价税合计
        items=re.search('(?<=购买方单位：).*',text)
        if not items is None:
            immediate_dict['购买方名称']=items.group(0)  #9.购买方名称
        
        items=re.search('(?<=购买方税号：).*',text)
        if not items is None:
            immediate_dict['购买方纳税人识别号']=items.group(0)  #9.购买方税号
        
        items=re.search('(?<=销售方名称：).*',text)
        if not items is None:
            immediate_dict['销售方名称']=items.group(0)  #10.销售方名称
        
        items=re.search('(?<=销售方税号：).*',text)
        if not items is None:
            immediate_dict['销售方纳税人识别号']=items.group(0)  #11.销售方税号
        
        
    #最后清洗商品、劳务信息
        if test.iloc[i,0]=="金额":
            a=i
        if test.iloc[i,0]=="备注：":
            b=i
    
    immediate_dict['发票明细']=test.iloc[a+1,0]
    
    df=pd.DataFrame.from_dict(immediate_dict,orient="index")
    df=df.T
    return df
#####################################################################
##主程序
for c in range(1,cnts+1):
    immediate_dict.clear()
    
    test=rw[rw['分组标志']==c]
    test=test.reset_index(drop=True)
    signal=test.iloc[3,0]
    if '卷票' in signal:
        df=iv_clean2(immediate_dict)
        grand_tab=pd.concat([grand_tab,df],join='outer',ignore_index=True)
    else:
        df=iv_clean1(immediate_dict)
        grand_tab=pd.concat([grand_tab,df],join='outer',ignore_index=True)

grand_tab['预警标志']=""

for index,row in grand_tab.iterrows():
    if row['购买方名称']!="中国人寿养老保险股份有限公司安徽省分公司":
        grand_tab.loc[index,'预警标志']=1
    if row['购买方纳税人识别号']!="91340000MA2MUGNP93":
        grand_tab.loc[index,'预警标志']=1
    if '娱乐' in row['销售方名称']:
        grand_tab.loc[index,'预警标志']=1
        

alert_tab=grand_tab[grand_tab['预警标志']==1]