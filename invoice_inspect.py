# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 12:50:15 2020

@author: zhangxi
"""

import pandas as pd
import re

rw=pd.read_csv('E:/OneDrive/Python工作/CLPCworks/invoice.txt')
rw.columns=['描述文本']
rw['分组标志']=""

grand_tab=pd.DataFrame()
immediate_dict={}
black_list=[]
departments_list=["市场一部",'市场二部','综合管理部','财务会计部','职业年金部','业务运营部']
#对原始数据标记分组
flag=0
dpt="lalala"
for i in range(len(rw)):    
    text=rw.iloc[i,0]
    if text in departments_list:
        dpt=text    
    if re.search(".*发票查验明细",text):
        flag+=1
        rw.iloc[i,1]=flag
    if re.search(".*任何单位或个人有权拒收并向当地税务机关举报",text):
        rw.iloc[i,1]='aaa'
        rw.iloc[i-1,0]=dpt
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
    
def iv_clean1(immediate_dict,c):
#############类专票的处理块#####################
    items_dict={}
    immediate_dict['发票种类']=test.iloc[3,0]             #0.发票种类
    immediate_dict['报销部门（参考）']=test.iloc[-1,0]
    flag=""
    #专票会出现一张票面上有不同的开票明细，就需要辨识出一张票上有几个开票明细
    
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
        items=re.match('名称.*',text)    #此处用match
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
        
        items=re.search('(?<=代开企业).*',text)
        if not items is None:
            flag="代"
            agent=items.group(0)  #处理代开
            agt1=re.search('([A-Z]|[0-9])+',agent).group(0) #代开企业税号
            agt2=re.search("(?<=名称:)",agent)
    
        #清洗商品、劳务信息，以字典-列表的形式储存
        e1=[] #项目
        e2=[] #规格型号
        e3=[] #单位
        e4=[] #数量
        e5=[] #单价
        e6=[] #金额
        e7=[] #税率
        e8=[] #税额
        
        if test.iloc[i,0]=="税额":
            a=i
        if test.iloc[i,0]=="合计":
            b=i
            if test.iloc[i,1]==c:
                for j in range(a+1,b-1):
                    items=re.search('\*(.*)',test.iloc[j,0])   #首先定位出项目名称
                    if not items is None:
                        e1.append(items.group(0))
                        items_dict['项目']=e1
                        #对规格型号和单位进行判断
                        compl='[^((-)?(\d*)(\.\d*)?)]'  #非数值的正则化表达
                        items=re.search(compl,test.iloc[j+1,0])
                        if not items is None:
                            #print(c,test.iloc[j+1,0],len(test.iloc[j+1,0]))
                            if len(test.iloc[j+1,0])>2:   #判断出了规格型号
                                e2.append(test.iloc[j+1,0])
                                items_dict['规格型号']=e2
                                
                                compl='[\u4e00-\u9fa5]([\u4e00-\u9fa5]*?)' #单位的正则化表达
                                items=re.search(compl,test.iloc[j+2,0])
                                if not items is None:
                                    e3.append(test.iloc[j+2,0])
                                    items_dict['单位']=e3
                                    
                                    compl='\d+(\.\d+)?'   #数量的正则化表达
                                    items=re.search(compl,test.iloc[j+3,0])
                                    if not items is None:
                                        e4.append(test.iloc[j+3,0])
                                        items_dict['数量']=e4
                                        e5.append(test.iloc[j+4,0])
                                        items_dict['单价']=e5
                                #完美的处理（规格、单位、数量、单价、要素齐全）
                                    
                            elif len(test.iloc[j+1,0])==1:   #没有规格，直接判断型号
                                    e3.append(test.iloc[j+1,0])
                                    items_dict['单位']=e3
                                    
                                    compl='\d+(\.\d+)?'   #数量的正则化表达
                                    items=re.search(compl,test.iloc[j+3,0])
                                    if not items is None:
                                        e4.append(test.iloc[j+2,0])
                                        items_dict['数量']=e4
                                        e5.append(test.iloc[j+3,0])
                                        items_dict['单价']=e5
                        #此处预留只有数量、单价的表达
                        
                    items=re.search('\d\d?%|(免税)',test.iloc[j,0])  #定位税率
                    if not items is None:
                        e7.append(items.group(0))
                        e8.append(test.iloc[j+1,0])
                        e6.append(test.iloc[j-1,0])
                        items_dict['税率']=e7
                        items_dict['税额']=e8
                        items_dict['金额']=e6
                    
    immediate_dict['发票明细']=items_dict
    #最后修正下代开发票信息
    if flag=="代":
        immediate_dict['销售方纳税人识别号']=agt1
        immediate_dict['销售方名称']=agent[agt2.span()[1]:]   #代开企业名称
    
    df=pd.DataFrame.from_dict(immediate_dict,orient="index")
    df=df.T
    
    return df

####################卷票的处理块
def iv_clean2(immediate_dict):
    immediate_dict['发票种类']=test.iloc[3,0]             #0.发票种类
    immediate_dict['报销部门（参考）']=test.iloc[-1,0]
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
    items=re.search('\*(.*)',test.iloc[a+1,0]).group(0)
    immediate_dict['发票明细']={"项目":[items],"金额":[immediate_dict['价税合计']]}
    
    df=pd.DataFrame.from_dict(immediate_dict,orient="index")
    df=df.T
    return df
##############################
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
        df=iv_clean1(immediate_dict,c)
        grand_tab=pd.concat([grand_tab,df],join='outer',ignore_index=True)

#检查模块#
grand_tab['备注']=""
for index,row in grand_tab.iterrows():
    if row['购买方名称']!="中国人寿养老保险股份有限公司安徽省分公司":
        grand_tab.loc[index,'备注']="公司名称错误"
    if row['购买方纳税人识别号']!="91340000MA2MUGNP93":
        grand_tab.loc[index,'备注']="税号错误"
    if re.search(".*娱乐.*|.*会所.*",row['销售方名称']):
        grand_tab.loc[index,'备注']="销售方娱乐、会所字样"
    if row['销售方名称'] in black_list:
        grand_tab.loc[index,'备注']=grand_tab.loc[index,'备注']+",销售方黑名单预警"
        
for i in range(len(grand_tab)):
    dst1=grand_tab.loc[i,'发票号码']
    for j in range(i+1,len(grand_tab)):
        dst2=grand_tab.loc[j,'发票号码']
        if dst1[:-1]==dst2[:-1]:
            grand_tab.loc[i,'备注']=grand_tab.loc[i,'备注']+str((i,j))
            grand_tab.loc[j,'备注']=grand_tab.loc[j,'备注']+str((i,j))

grand_tab.drop_duplicates(subset='校验码',keep="first",inplace=True)

alert_tab = grand_tab[grand_tab["备注"] != ""]

