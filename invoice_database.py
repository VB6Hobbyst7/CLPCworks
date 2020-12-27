# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 13:57:18 2020

@author: zhangxi
"""
import os
import pymysql
import pandas as pd
from invoice_inspect import inspector
import shutil
import re
from gadgets import timer
import time


#检查发票信息，生成导入数据库表


def grand_tab_gen():
    rw_text=pd.read_csv('E:/OneDrive/国寿养老工作/invoice.txt',error_bad_lines=False)
    y="2020"
    m=["10",'11','12']
    
    grand_tab=inspector(rw_text,y,m)
    grand_tab[grand_tab['系统公文号']==""]
    
    for index,row in grand_tab.iterrows():
        if '错误' in row['预警标志']:
            grand_tab.loc[index,'系统公文号']='作废'
    return grand_tab

@timer
def OAfile_gen():             #导出数据库中公文号为空的表
    db = pymysql.connect("localhost","root","abcd1234",'clpc_ah')
    cursor = db.cursor()
    
    sql="select 发票号码,价税合计,销售方名称,报销部门（参考）,入库时间戳,发票明细 from invoice where 系统公文号 is null or 系统公文号=''"
    cursor.execute(sql)
    rows=cursor.fetchall()
    columnDes = cursor.description #获取连接对象的描述信息
    columnNames = [columnDes[i][0] for i in range(len(columnDes))] #获取列名
    x_tab= pd.DataFrame([list(i) for i in rows],columns=columnNames)
    x_tab['系统公文号']=''
    x_tab['价税合计']=x_tab['价税合计'].apply(pd.to_numeric)
    x_tab.sort_values(by='价税合计',inplace=True)
    for index,row in x_tab.iterrows():
        if '餐饮' in row['发票明细']:
            x_tab.loc[index,'发票明细']='招待费-餐饮'
        elif '酒' in row['发票明细']:
            x_tab.loc[index,'发票明细']='招待费-酒'
        else:
            x_tab.loc[index,'发票明细']=''
    x_tab=x_tab[['入库时间戳','发票明细','发票号码','销售方名称','价税合计','报销部门（参考）','系统公文号']]
    x_tab.to_excel('C:/Users/ZhangXi/Desktop/update_tosql.xlsx',index=False)
    
    cursor.close()
    db.close()
    return x_tab

@timer
def OAfile_update():                        #更新系统公文号
    #付款时间戳
    stamp_time=time.localtime(time.time())
    timestamp=(time.strftime("%Y-%m-%d %H:%M:%S",stamp_time))
    update_tab=pd.read_excel('C:/Users/ZhangXi/Desktop/update_tosql.xlsx',dtype={'发票号码':str})
    update_tab.dropna(subset=['系统公文号'],inplace=True)
    update_tab['付款时间戳']=timestamp
    
    update_tab=update_tab.to_dict(orient='list')
    dict1=dict(zip(update_tab['发票号码'],update_tab['系统公文号']))
    dict2=dict(zip(update_tab['发票号码'],update_tab['报销部门（参考）']))
    dict3=dict(zip(update_tab['发票号码'],update_tab['付款时间戳']))
    
    db = pymysql.connect("localhost","root","abcd1234",'clpc_ah')
    cursor = db.cursor()
    temp1=update_tab['发票号码']
    sql1=("UPDATE invoice set 系统公文号=%s where 发票号码=%s;")
    sql2=("UPDATE invoice set 报销部门（参考）=%s where 发票号码=%s;")
    sql3=("UPDATE invoice set 付款时间戳=%s where 发票号码=%s;")
    
    for j in range(len(temp1)):
        cursor.execute(sql1,(dict1.get(temp1[j]),temp1[j]))
        cursor.execute(sql2,(dict2.get(temp1[j]),temp1[j]))
        cursor.execute(sql3,(dict3.get(temp1[j]),temp1[j]))
    db.commit()
    cursor.close()
    db.close()
    
    file_name1='C:/Users/ZhangXi/Desktop/update_tosql.xlsx'
    file_name2='g:/备份仓库/发票更新信息入库备份/update_tosql_%s.xlsx' %(timestamp)
    shutil.copyfile(file_name1,file_name2)
    os.remove(file_name1)

@timer
def length_test():                 
    #检查发票明细的长度是否一致
    test_tab=pd.read_excel('C:/Users/ZhangXi/Desktop/invoice_to_sql.xlsx',dtype={'发票号码':str})
    items=pd.DataFrame()
    
    for i in range(len(test_tab)):
        print('检查第 %s张凭证，凭证号：%s' %(i,test_tab.loc[i,'发票号码']))
        temp=eval(test_tab.loc[i,'发票明细'])
        temp1=pd.DataFrame(temp)
        items=pd.concat([items,temp1])
        temp.clear()
    print('检查完成')
    
    print('记录入库...')
    db = pymysql.connect("localhost","root","abcd1234",'clpc_ah')
    cursor = db.cursor()
    col=str(tuple(test_tab.columns.values))
    col=col.replace("\'","")
    
    for i in range(len(test_tab)):
        rec=str(tuple(test_tab.loc[i,:]))
        rec=rec.replace('nan','null')
        insert_sql="insert into invoice%s values%s;" %(col,rec)
        cursor.execute(insert_sql)
    
    try:
        db.commit()
        print('入库成功')
        stamp_time=time.localtime(time.time())
        timestamp=(time.strftime("%Y-%m-%d-%H-%M-%S",stamp_time))
        
        file_name1='C:/Users/ZhangXi/Desktop/invoice_to_sql.xlsx'
        file_name2='g:/备份仓库/发票更新信息入库备份/invoice_to_sql_%s.xlsx' %(timestamp)
        shutil.copyfile(file_name1,file_name2)
        os.remove(file_name1)
    except:
        db.rollback()
        print('入库失败')
    cursor.close
    db.close
    return items

@timer
def items_detail():
    #打开MYSQL数据库导出流水单
    db = pymysql.connect("localhost","root","abcd1234",'clpc_ah')
    cursor = db.cursor()
    sql=("select * from invoice where 系统公文号 like 'B%';")
    cursor.execute(sql)
    temp=cursor.fetchall()
    columnDes = cursor.description #获取连接对象的描述信息
    columnNames = [columnDes[i][0] for i in range(len(columnDes))] #获取列名
    data_rw= pd.DataFrame([list(i) for i in temp],columns=columnNames)
    items=pd.DataFrame()
    
    for index,row in data_rw.iterrows():
        temp=eval(row['发票明细'])
        temp['发票号码']=row['发票号码']
        temp['开票日期']=row['开票日期']
        temp['价税合计']=row['价税合计']
        temp['报销部门（参考）']=row['报销部门（参考）']
        temp['销售方名称']=row['销售方名称']
        temp['系统公文号']=row['系统公文号']
        temp['凭证号']=row['凭证号']
        
        temp1=pd.DataFrame(temp)
        items=pd.concat([items,temp1],ignore_index=True)
        temp.clear()
    
    items['商品明细']=''
    for i in range(len(items)):
        item_split=items.loc[i,'项目'].split("*")
        if not item_split[1] is None:
            items.loc[i,'项目']=item_split[1]
        if not item_split[2] is None:
            items.loc[i,'商品明细']=item_split[2]
            
            restauant=re.search('餐(饮|费)',item_split[2])
            if restauant:
                items.loc[i,'商品明细']='餐饮'
    data_rw.to_excel('C:/Users/ZhangXi/Desktop/已入账发票清单.xlsx',index=False)
    items.to_excel('C:/Users/ZhangXi/Desktop/已入账商品明细.xlsx',index=False)
    return items

a="0"
a=input('请选择本次处理的任务：\n1-查验发票、生成数据库表预备导入\n2-校验拟导入的发票明细长度并入库\n3-导出数据库中空公文号的条目\n4-更新系统公文号\n5-导出发票项目明细\n>>>')

if a=="0":
    pass
elif a=="1":
    temp_tab=grand_tab_gen()
    #辅助列借用餐饮标志
    temp_tab=temp_tab[temp_tab['餐饮标志'].isin([2])]
    temp_tab.drop('餐饮标志',axis=1,inplace=True)
    
    temp_tab.to_excel('C:/Users/ZhangXi/Desktop/invoice_to_sql.xlsx',index=False)
    alert_tab = temp_tab[temp_tab["预警标志"] != ""]
elif a=="2":
    test=length_test()
elif a=="3":
    load_tab=OAfile_gen()
elif a=="4":
    OAfile_update()
elif a=="5":
    items_detail=items_detail()
