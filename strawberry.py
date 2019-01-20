import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import datetime
import requests
import urllib
import pandas as pd
import json

# 函数: 承运公司名到文本
def GetComName(comCode):
        if comCode=='shentong':
            return '申通快递'
        elif comCode=='zhongtong':
            return '中通快递'
        elif comCode=='ems':
            return 'EMS'
        elif comCode=='huitongkuaidi':
            return '汇通快运'
        else:
            return comCode

# 函数: 取状态文本
def GetStateText(num):
        if num==0:
            return '运输中'
        elif num==1:
            return '揽件'
        elif num==2:
            return '疑难'
        elif num==3:
            return '已签收'
        elif num==4:
            return '退回签收'
        elif num==5:
            return '派送中'
        elif num==6:
            return '退回中'
def dataframe2str(datalist):
        datatable=""
        for this in datalist:
            datatable += this['time'] + "\t" + this['context'] + "\n"
        return datatable
    
def k100_find_order(company, id):
        if id.strip() == '':
                print("订单输入为空")
                return None
        print("[",id.strip(),"]",company)
        data = {}
        data['type'] = company
        data['postid'] = id
        data['valicode']=''
        data['id']=1
        data['temp']='0.14881871496191512'
        query = requests.get("http://www.kuaidi100.com/query", params=data)
        res = query.json()
        print("\n运单编号 --> " + "!"+res['nu']+"!")
        print("\n承运公司 --> " + GetComName(res['com']))
        print("\n当前状态 --> " + GetStateText(int(res['state'])))
        print("\n---------------- 跟踪信息 ------------------\n")
        if res['nu'] == '':
                mesg = "订单"+ id + "没有查到此单"
                print(mesg)
                return None
        #print(dataframe2str(res['data']))
        #for this in res['data']:
           # print(this['time'] + "\t" + this['context'] + "\n")
        return res




class Application(tk.Tk):
    '''
    文件夹选择程序
        界面与逻辑分离
    '''
    
    def __init__(self):
        '''初始化'''
        super().__init__() # 有点相当于tk.Tk()
        self.createWidgets()
        
    def searchcallback(self):
        order_var = self.textbox.get("0.0", "end")
        #messagebox.showinfo( "查询结果", order_var)
        i = 0 
        for myvar in order_var.split('\n'):
                i +=1
                print(i)
                myorder = k100_find_order('zhongtong',myvar)
                if myorder:
                        self.treeview.insert('', 1, values=(myorder['nu'], GetComName(myorder['com']),GetStateText(int(myorder['state'])),dataframe2str(myorder['data'])))
                
        
    def createWidgets(self):
        '''界面'''
        self.title('快递订单查询工具')
        self.columnconfigure(0, minsize=50)
        self.geometry('800x480+200+100')
        # 定义一些变量
        self.entryvar = tk.StringVar()
        self.keyvar = tk.StringVar()
        self.keyvar.set('订单状态过滤')
        items = ['运输中','揽件','疑难','已签收','退回签收','派送中','退回中']

        # 先定义顶部和左边栏，内容三个Frame，用来放置下面的部件
        topframe = tk.Frame(self, height=80)
        contentframe = tk.Frame(self)
        leftframe = tk.Frame(self)
        topframe.pack(side=tk.TOP)
        leftframe.pack(side=tk.LEFT,fill=tk.Y)
        contentframe.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
        
        # 顶部区域（四个部件）
        # -- 前三个直接用 tk 的 widgets，第四个下拉列表 tk 没有，ttk 才有，比较麻烦
        glabel = tk.Label(topframe, text='当前文件夹:')
        gentry = tk.Entry(topframe, textvariable=self.entryvar)
        gbutton = tk.Button(topframe, command=self.__opendir, text='选择')
        gcombobox = ttk.Combobox(topframe, values=items, textvariable=self.keyvar)
        # -- 绑定事件
        gentry.bind('<Return>', func=self.__refresh)
        #gcombobox.bind('<ComboboxSelected>', func=self.__refresh) # 绑定 <ComboboxSelected> 事件
        # -- 放置位置
        glabel.grid(row=0, column=0, sticky=tk.W)
        gentry.grid(row=0, column=1)
        gbutton.grid(row=0, column=2)
        gcombobox.grid(row=0, column=3)
        
        # 内容区域（三个部件）
        # -- 前两个滚动条一个竖直一个水平
        self.oderLabel = tk.Label(leftframe, text='订单列表',width=20)
        self.textbox = tk.Text(leftframe,width=20)
        self.searchbutton=tk.Button(leftframe,text='查询',command= self.searchcallback )
        
        # -- 放置位置
        self.oderLabel.grid(row=0,column=0,sticky=tk.N)
        self.textbox.grid(row=1, column=0, sticky=tk.NS)
        self.searchbutton.grid(row=2,sticky=tk.W+tk.E+tk.S)
                
        rightbar = tk.Scrollbar(contentframe, orient=tk.VERTICAL)
        bottombar = tk.Scrollbar(contentframe, orient=tk.HORIZONTAL)
        self.treeview = ttk.Treeview(contentframe,yscrollcommand=rightbar.set,show="headings", xscrollcommand=bottombar.set,columns=("a","b","c","d"))
        self.treeview.column('0', width=20, anchor='center')
        self.treeview.column('a', width=20, anchor='center')
        self.treeview.column('b', width=20, anchor='center')
        self.treeview.column('c', width=20, anchor='center')
        self.treeview.column('d', width=20, anchor='center')
        self.treeview.heading('0', text='#')
        self.treeview.heading('a', text='订单单号')
        self.treeview.heading('b', text='承运公司')
        self.treeview.heading('c', text='运单状态')
        self.treeview.heading('d', text='跟踪信息')

        # -- 放置位置
        rightbar.pack(side =tk.RIGHT, fill=tk.Y)
        bottombar.pack(side=tk.BOTTOM, fill=tk.X)

        #mydata = k100_find_order('zhongtong',75124545932031)
        #self.treeview.insert('', 1, values=(mydata['nu'], GetComName(mydata['com']),GetStateText(int(mydata['state'])),dataframe2str(mydata['data'])))
        self.treeview.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)

        # -- 设置命令
        rightbar.config(command=self.textbox.yview)
        bottombar.config(command=self.textbox.xview)
        

        
    def __opendir(self):
        '''打开文件夹的逻辑'''
        self.textbox.delete('1.0', tk.END) # 先删除所有
        
        self.dirname = filedialog.askdirectory() # 打开文件夹对话框
        self.entryvar.set(self.dirname) # 设置变量entryvar，等同于设置部件Entry
        
        if not self.dirname:
            messagebox.showwarning('警告', message='未选择文件夹！')  # 弹出消息提示框
        
        self.dirlist = os.listdir(self.entryvar.get())
        for eachdir in self.dirlist:
            self.textbox.insert(tk.END, eachdir+'\r\n')
            
        self.textbox.update()
        
        
    def __refresh(self, event=None):
        '''更新的逻辑'''
        self.textbox.delete('1.0', tk.END) # 先删除所有
        
        self.dirlist = os.listdir(self.entryvar.get())
        for eachdir in self.dirlist:
            self.textbox.insert(tk.END, eachdir+'\r\n')
            
        self.textbox.update()
        
        
    def addmenu(self, Menu):
        '''添加菜单'''
        Menu(self)
        
        
        
class MyMenu():
    '''菜单类'''
    
    def __init__(self, root):
        '''初始化菜单'''
        self.menubar = tk.Menu(root) # 创建菜单栏
        
        # 创建“文件”下拉菜单
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="打开", command=self.file_open)
        filemenu.add_command(label="新建", command=self.file_new)
        filemenu.add_command(label="保存", command=self.file_save)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=root.quit)
        
        # 创建“编辑”下拉菜单
        editmenu = tk.Menu(self.menubar, tearoff=0)
        editmenu.add_command(label="剪切", command=self.edit_cut)
        editmenu.add_command(label="复制", command=self.edit_copy)
        editmenu.add_command(label="粘贴", command=self.edit_paste)
        
        # 创建“帮助”下拉菜单
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="关于", command=self.help_about)
        
        # 将前面三个菜单加到菜单栏
        self.menubar.add_cascade(label="文件", menu=filemenu)
        self.menubar.add_cascade(label="编辑", menu=editmenu)
        self.menubar.add_cascade(label="帮助", menu=helpmenu)
        
        # 最后再将菜单栏整个加到窗口 root
        root.config(menu=self.menubar)
        
    def file_open(self):
        messagebox.showinfo('打开', '文件-打开！')  # 消息提示框
        pass
        
    def file_new(self):
        messagebox.showinfo('新建', '文件-新建！')  # 消息提示框
        pass
        
    def file_save(self):
        messagebox.showinfo('保存', '文件-保存！')  # 消息提示框
        pass
        
    def edit_cut(self):
        messagebox.showinfo('剪切', '编辑-剪切！')  # 消息提示框
        pass
        
    def edit_copy(self):
        messagebox.showinfo('复制', '编辑-复制！')  # 消息提示框
        pass
        
    def edit_paste(self):
        messagebox.showinfo('粘贴', '编辑-粘贴！')  # 消息提示框
        pass
        
    def help_about(self):
        messagebox.showinfo('关于', '作者：巴龙 \n verion 0.1 \n 感谢GUTT使用！ \n kai.yang@foxmail.com ')  # 弹出消息提示框
        
    
    
if __name__ == '__main__':
    # 实例化Application
    app = Application()
    
    # 添加菜单:
    app.addmenu(MyMenu)
    
    # 主消息循环:
    app.mainloop()
