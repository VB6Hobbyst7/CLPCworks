# -*- coding: utf-8 -*-
"""
Created on Mon Sep 14 12:50:15 2020

@author: zhangxi
"""

import pandas as pd
import re
import time
import pymysql

def iv_clean1(immediate_dict,c,test):
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
            print('正在处理第%s张发票，发票号码：%s' %(c,immediate_dict['发票号码']))
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
        e9=[] #价税小计
        nail=[] #钉住项目的位置
        
        if test.iloc[i,0]=="税额":
            a=i
        if test.iloc[i,0]=="合计":
            b=i
            if test.iloc[i,1]==c:
                sht=divmod((b-a-1),8)  #发票明细的条目数和余数，出现余数则需要补足占用位
                if sht[1]!=0:
                    mo=sht[0]+1        #mo是发票的条目数
                else:
                    mo=sht[0]
                
                for j in range(a+1,b-1):
                    items=re.search('\*(.*)',test.iloc[j,0])   #首先定位出项目名称
                    if not items is None:
                        e1.append(items.group(0))
                        items_dict['项目']=e1   #有的明细项是没有*号的，要写个判断自己补上
                        nail.append(j)
                    items=re.search('\d\d?%|(免税)',test.iloc[j,0])  #定位税率
                    if not items is None:
                        e7.append(items.group(0))
                        e8.append(test.iloc[j+1,0])
                        e6.append(test.iloc[j-1,0])
                        #价税小计
                        if not test.iloc[j+1,0]=="***":
                            e9.append(float(test.iloc[j-1,0])+float(test.iloc[j+1,0]))
                        else:
                            e9.append(float(test.iloc[j-1,0]))
                            
                        items_dict['税率']=e7
                        items_dict['税额']=e8
                        items_dict['金额']=e6
                        items_dict['价税小计']=e9
               
                for n in range(len(nail)):
                    e_t2="~"
                    e_t3="~"
                    e_t4="~"
                    e_t5="~"   
                    #确保占位，后面做分析时要把字典拆成dataframe，len不一样会有麻烦
                    
                    context=[]
                    for nl_temp in range(nail[n]+1,nail[n]+5):
                        context.append(test.iloc[nl_temp,0])
                    
                    for c_cnt in range(len(context)):
                        items=re.search('\d\d?%|免税',context[c_cnt])  #定位税率,要出现有两个空格才能出现税率的格
                        if not items is None:
                            break
                        else:
                            c_cnt=4
                    context=context[:c_cnt]
                    #print(context)
                    
                    if sht[1]==0:
                        #要素齐全，完美填充
                        e_t2=context[0]
                        e_t3=context[1]
                        e_t4=context[2]
                        e_t5=context[3]
                        
                    else: #sht[1]!=0,有空缺栏，非完美
                          #要素不齐全，难度全在这了
                        if len(context)==1:
                            #只有一个要素，这个要素很可能是单价
                            items=re.search('(-)?(\d*)(\.\d*)?',context[0])
                            if not items is None:
                                #此处应该有一个本数值和发票总价的匹配控制
                                e_t5=context[0]
                        elif len(context)==2:
                            print("注意context=2的模块没写:",context)
                        elif len(context)==3:
                            #三个要素都是数字
                            compl='(-)?(\d*)(\.\d*)?'
                            items=re.search(compl,context[0])
                            if not items is None:
                                e_t4=context[0]
                            else:
                                print("注意出现汉字的模块没写:",context)
                            items=re.search(compl,context[1])
                            if not items is None:
                                e_t5=context[1]
                            else:
                                print("注意出现汉字的模块没写:",context)
                            
                        elif len(context)==4:
                            #可能会出现有整体不完整，但逐条完整的判断
                            
                            compl1='[^((-)?(\d*)(\.\d*)?)]' #非数值的正则表达
                            compl2='[\u4E00-\u9FA5][\u4E00-\u9FA5]?'        #最多两个汉字的正则表达
                            items=re.search(compl1,context[0])
                            if not items is None:
                                #第一格非数值
                                items=re.search(compl1,context[1])
                                if not items is None:
                                #第二格非数值:规格、单位、数量、单价
                                    e_t2=context[0]
                                    e_t3=context[1]
                                    e_t4=context[2]
                                    e_t5=context[3]
                                else:
                                #第二格数值：规格|单位、数量、单价
                                #正则化判断非数值的是规格还是单位
                                    items=re.search(compl2,context[0])
                                    if not items is None:
                                        e_t3=context[0]
                                    else:
                                        e_t2=context[0]
                                    
                                    e_t4=context[1]
                                    e_t5=context[2]
                                
                    e2.append(e_t2)
                    e3.append(e_t3)
                    e4.append(e_t4)
                    e5.append(e_t5)
                    
                    items_dict['规格型号']=e2
                    items_dict['单位']=e3
                    items_dict['数量']=e4
                    items_dict['单价']=e5
    immediate_dict['发票明细']=items_dict
    #最后修正下代开发票信息
    if flag=="代":
        immediate_dict['销售方纳税人识别号']=agt1
        immediate_dict['销售方名称']=agent[agt2.span()[1]:]   #代开企业名称
    
    df=pd.DataFrame.from_dict(immediate_dict,orient="index")
    df=df.T
    
    return df

def iv_clean2(immediate_dict,c,test):
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
            print('正在处理第%s张发票，发票号码：%s' %(c,immediate_dict['发票号码']))
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

#发票核查主程序
def inspector(rw_text,y,m):
    rw=rw_text
    rw.columns=['描述文本']
    rw['分组标志']=""
    grand_tab=pd.DataFrame()
    immediate_dict={}
    black_list=[]
    departments_list=["市场一部",'市场二部','综合管理部','财务会计部','职业年金部','业务运营部']
    #对原始数据标记分组
    flag=0
    dpt="未做标识"
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
    
    for c in range(1,cnts+1):
        immediate_dict.clear()
        test=rw[rw['分组标志']==c]
        test=test.reset_index(drop=True)
        signal=test.iloc[3,0]
        #print(test)
        if '卷票' in signal:
            df=iv_clean2(immediate_dict,c,test)
            grand_tab=pd.concat([grand_tab,df],join='outer',ignore_index=True)
            
        else:
            df=iv_clean1(immediate_dict,c,test)
            grand_tab=pd.concat([grand_tab,df],join='outer',ignore_index=True)

    #检查模块#
    grand_tab['预警标志']=""
    grand_tab['系统公文号']=""
    grand_tab['凭证号']=''
    grand_tab['入库时间戳']=''
    
    for index,row in grand_tab.iterrows():
        #print(row)
        if row['购买方名称']!="中国人寿养老保险股份有限公司安徽省分公司":
            grand_tab.loc[index,'预警标志']=grand_tab.loc[index,'预警标志']+"公司名称错误"
        if row['购买方纳税人识别号']!="91340000MA2MUGNP93":
            grand_tab.loc[index,'预警标志']=grand_tab.loc[index,'预警标志']+"税号错误"
        if re.search(".*娱乐.*|.*会所.*",row['销售方名称']):
            grand_tab.loc[index,'预警标志']=grand_tab.loc[index,'预警标志']+"销售方娱乐、会所字样错误"
        if row['开票日期'][:4]!=y or row['开票日期'][5:7] not in m:
            grand_tab.loc[index,'预警标志']=grand_tab.loc[index,'预警标志']+"开票日期错误"
        
        if row['销售方名称'] in black_list:
            grand_tab.loc[index,'预警标志']=grand_tab.loc[index,'预警标志']+"销售方黑名单预警"
        #检查餐饮供应商的名称
        restautant=row['发票明细'].get("项目")
        
        if "餐饮" in restautant[0]:
            compl='.*(餐|饮|酒|菜|饭|烧|烤|锅|鱼|渔|牛|鸡|羊|猪|狗|肠|卤|吃|食|饺|肉|粥|虾)'
            items=re.search(compl,row['销售方名称'])
            if items is None:       
                grand_tab.loc[index,"预警标志"]=grand_tab.loc[index,'预警标志']+"销售方无餐饮店字样"
        
        inspect_time=time.localtime(time.time())
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S",inspect_time)
        grand_tab.loc[index,'入库时间戳']=timestamp
        
    #调取数据库记录进行发票号码比对
    db = pymysql.connect("localhost","root","abcd1234",'clpc_ah')
    cursor = db.cursor()
    sql="select * from invoice"
    cursor.execute(sql)
    rows=cursor.fetchall()
    columnDes = cursor.description #获取连接对象的描述信息
    columnNames = [columnDes[i][0] for i in range(len(columnDes))] #获取列名
    db_df=pd.DataFrame([list(i) for i in rows],columns=columnNames)
    cursor.close()
    db.close()
    db_df['预警标志'].replace(to_replace=[None],value="",inplace=True)

    instant_tab_list=grand_tab['校验码'].tolist()
    grand_tab=pd.concat([grand_tab,db_df],axis=0,ignore_index=True,join='outer')
    
    #链接数据库对发票号码进行号码比对
    for i in range(len(grand_tab)):
        dst1=grand_tab.loc[i,'发票号码']
        
        for j in range(i+1,len(grand_tab)):
            dst2=grand_tab.loc[j,'发票号码']
            
            if dst1[:-1]==dst2[:-1] and abs(int(dst1[-1])-int(dst2[-1]))<2:
                grand_tab.loc[i,'预警标志']=grand_tab.loc[i,'预警标志']+"(%s)" % grand_tab.loc[j,'发票号码']
                grand_tab.loc[j,'预警标志']=grand_tab.loc[j,'预警标志']+"(%s)" % grand_tab.loc[i,'发票号码']
                
                x=grand_tab.loc[i,'校验码'] in instant_tab_list
                y=grand_tab.loc[j,'校验码'] in instant_tab_list
                
                if (x and not(y)): 
                    instant_tab_list.append(grand_tab.loc[j,'校验码'])
                elif (not(x) and y):
                    instant_tab_list.append(grand_tab.loc[i,'校验码'])
            
    grand_tab=grand_tab[grand_tab['校验码'].isin(instant_tab_list)]
    return grand_tab