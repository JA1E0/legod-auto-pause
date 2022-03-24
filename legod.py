

###############
# @Author: 6yy66yy
# @Date: 2021-07-26 16:44:05
# @LastEditors: 6yy66yy
# @LastEditTime: 2022-03-24 15:51:26
# @FilePath: \legod-auto-pause\legod.py
# @Description: 雷神加速器时长自动暂停，暂停程序，可以独立运行。
###############
from concurrent.futures import ThreadPoolExecutor
import requests
import json
import os
import configparser
# from hyper.contrib import HTTP20Adapter
import win32com.client
import time
import traceback
import logging
import hashlib #md5 加密
from win10toast import ToastNotifier #消息提醒
toaster = ToastNotifier()

logging.basicConfig(filename='log.log')
def genearteMD5(str):
    # 创建md5对象
    hl = hashlib.md5()

    # Tips
    # 此处必须声明encode
    # 否则报错为：hl.update(str)    Unicode-objects must be encoded before hashing
    hl.update(str.encode(encoding='utf-8'))
    return hl.hexdigest()
url='https://webapi.leigod.com/api/user/pause'
header = {
        # ':authority': 'webapi.nn.com',
        # ':method':'POST',
        # ':path':'/api/user/pause',
        # ':scheme': 'https',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36 Edg/88.0.705.53',
        'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
        'Connection':"keep-alive",
        'Accept': "application/json, text/javascript, */*; q=0.01",
        'Accept-Encoding': "gzip, deflate, br",
        'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        'DNT': "1",
        'Referer': 'https://www.legod.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site'
                }

def login(uname,password):
    if(uname=="" or password==""):
        return False
    token=""
    body={
        'username':uname,
        'password':genearteMD5(password),
        'user_type':'0',
        'src_channel':'guanwang',
        'country_code':86,
        'lang':'zh_CN',
        'region_code':1,
        'account_token':'null'}
    r = requests.post("https://webapi.leigod.com/api/auth/login",data=body,headers = header)
    msg=json.loads(r.text)
    if(msg['code']==0):
        token=msg['data']['login_info']['account_token']
        return token
    else:
        print(msg['msg'])
        return False

def check_exsit(process_name):
    ls=process_name.split(',')
    WMI = win32com.client.GetObject('winmgmts:')
    for i in ls:
        processCodeCov = WMI.ExecQuery('select * from Win32_Process where Name like "%{}%"'.format(i+'.exe'))
        if len(processCodeCov) > 0:
            return '检测到{}'.format(i)
    return False

def pause(sflag=False):
    global conf
    payload={
        "account_token":conf.get("config","account_token"),
        "lang":"zh_CN"}
    # sessions=requests.session()
    # sessions.mount('https://webapi.nn.com', HTTP20Adapter())
    # r =sessions.post(url,data=payload,headers = header)
    i=0
    token=''
    if(sflag):
        stopp=True
    while(i<3):
        if(uname=="" or password=="" and conf.get("config","account_token") == ""):
            toaster.show_toast("没填用户名密码或者是token无效","请填写后重启工具via 自动暂停工具v1.2",icon_path=r"legod.ico",duration=3,threaded=True)#多线程不会引起程序关闭，注意ico地址要这样写才不会报错
            break
        r = requests.post(url,data=payload,headers = header)
        if r.status_code==403:
            try:
                token = login(uname,password)
            except:
                print("未知错误，可能是请求频繁或者是网址更新")
                toaster.show_toast("未知错误，可能是请求频繁或者是网址更新","via 自动暂停工具v1.2",icon_path=r"legod.ico",duration=3,threaded=True)
            continue
        msg=json.loads(r.text)
        if(msg['code']!=400006):
            print(msg['msg'])
            toaster.show_toast(msg['msg'],"via 自动暂停工具v1.2",icon_path=None,duration=5,threaded=True)
            return True
        else:
            token = login(uname,password)
            if token:
                conf.set('config','account_token',token)
                conf.write(open(configPath,'w',encoding='utf_8'))
                print("原token失效,已写入新的token")
                payload['account_token']=token
def load(first=False):
        # 当前文件路径
    proDir = os.path.split(os.path.realpath(__file__))[0]
    global appname,sec,uname,password,update,account_token,configPath,lepath,conf
    # 在当前文件路径下查找.ini文件
    configPath = os.path.join(proDir, "config.ini")
    conf = configparser.ConfigParser()
    
    # 读取.ini文件
    conf.read(configPath,encoding='UTF-8-sig')
    
    # get()函数读取section里的参数值
    
    appname = conf.get('config','games')
    sec = int(conf.get('config','looptime'))
    uname=conf.get("config","uname")
    password=conf.get("config","password")
    update=int(conf.get("config","update"))
    lepath=conf.get("config","path")
    if first:
        print('''
                ***************************************************\n
                *                                                 *\n
                *                                                 *\n
                *              雷神加速器自动暂停工具v1.2         *\n
                *                     正在运行                     *\n
                *                    作者：6yy66yy                 *\n
                *                                                 *\n
                ***************************************************\n
                ''')
        print("目前检测游戏列表:{}".format(appname))
    
    # account_token=login(uname,password)
    account_token = conf.get("config","account_token")
    return conf

def detection(conn1):
    sw=1
    while 1==1:
        game=check_exsit(appname)
        if(game):
            if(sw==1):
                print(game)
                sw=0
        elif(sw==0):
            for i in range(1,sec):
                game=check_exsit(appname)
                time.sleep(1)
            if game is False:
                try:
                    pause()
                except:
                    s = traceback.format_exc()
                    logging.error(s)
            sw=1
        time.sleep(update)
        if(conn1.poll()):
            break
def detection():
    sw=1
    while 1==1:
        game=check_exsit(appname)
        if(game):
            if(sw==1):
                print(game)
                sw=0
        elif(sw==0):
            for i in range(1,sec):
                game=check_exsit(appname)
                time.sleep(1)
            if game is False:
                try:
                    pause()
                except:
                    s = traceback.format_exc()
                    logging.error(s)
            sw=1
        time.sleep(update)
global appname,sec,uname,password,update,account_token,configPath,lepath,conf,stopp
stopp=False
conf=load(first=True)
if __name__ == '__main__': 
    detection()
    
    

