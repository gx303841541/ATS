# -*- coding: utf-8 -*-
import os, sys, re, time
import datetime
import json
import threading
import random
import socket
import telnetlib

sys.path.append(os.path.abspath('.'))
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        return main()

#添加设备消息
def getAddMsg(category):
        num=random.randint(100, 9999999)
        msg_on = '{"uuid": "111","encry": "false","content": {"method": "dm_add_device","timestamp": 1494916080598,"req_id": '+str(num)+',"params": {"device_category_id": '+str(category)+',"family_id": 1,"room_id": 1,"user_id": 1012}}}\n'
        print msg_on
        global req_id
        req_id=str(num)
        return str(msg_on)




#写入日志
def WriteToFile(filename, data):
	# filename: Full path to file
	# data: data to be written to the szFile
	f = file(filename, 'a')
	f.write(data)
	f.close()
	
	
hoststr="192.168.10.1"
port=5100
sck=None
#发送消息
def sendMsg(msg):
        try:
                global sck
                if sck is None:
                        #global sck
                        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sck.connect((hoststr, port))
                sck.sendall(msg)
        except Exception,e:
                #global sck
                sck=None
                exc="-----请检查与路由器之间的连接是否正常-----"+ str(Exception) + ":"+ str(e)
                print exc
                WriteToFile('Log_Delay.txt',exc)

#发送并写入日志                
def msgSend(msg):
    sendMsg(msg)
    sendtime=datetime.datetime.now()
    print str(sendtime)+"   sended the Add Device message  \r\n"
    WriteToFile('Log_Device.txt',str(sendtime) + "   sended message  " + "\r\n")

        
        
#接收消息
def loopRece():
        while(True):
                if sck is not None:
                        try:
                                #print "111111111"
                                data = sck.recv(1024)
                                print data
                                on_message(data)
                        except Exception,e:
                                pass
                else:
                        time.sleep(1)
                        print "connection invalid"
#开始发送
def startRece():
    th = threading.Thread(target=loopRece)
    th.setDaemon(True)
    th.start()



def main():
        
        
        global sendtime
        sendtime=datetime.datetime.now()
        return quickConfig()
        


uuid=''
sendtime=''
req_id=''
deviceuuid=None
ispass=None
def on_message(message):
    print "json"+message
    strjson=json.loads(message)
    strjson=strjson['content']
    if (strjson.has_key('msg')):
            if str(strjson['msg'])=='success':
                    if (strjson.has_key('method')):
                            method=str(strjson['method'])                    
                            if method=='dm_add_device':
                                    result=strjson['result']
                                    uuid=str(result['device_uuid'])
                                    print strjson
                                    recetime=datetime.datetime.now()
                                    print 'sendtime: '+str(recetime)
                                    print "入网成功，获取uuid为: "+uuid +'\n'
                                    print str(recetime)+"   received the message :  "+str(recetime)
                                    WriteToFile('Log_Device.txt',str(recetime) + "uuid is: "+ uuid+ str(recetime)+ ",the Sub Device has been added successfully " +"\r\n")
                                    global deviceuuid
                                    deviceuuid=uuid
                                    global ispass
                                    ispass="ok"
                                    
Host = '192.168.10.1' 
finish = ':/#'
tn=None
#执行命令
def execmd(comm):
        #print comm
        
        global tn
        if tn is None:
            tn = telnetlib.Telnet(Host)
            tn.open(Host)
            time.sleep(3)
            rd=tn.read_very_eager()
        if comm is not None:
            comm=comm.encode('ascii')
            x=tn.write(comm +'\n')
            print "exe comd"
            time.sleep(5)
        print "read rd"
        rd=tn.read_very_eager()
        return rd
    
#检查打印日志是否包含"quickconfig send complete"    
def quickConfig():
    try:
        execmd("kill -9 $(pidof wifi_mgr)")
        print execmd("wifi_mgr ath02 -d")
        msgSend(getAddMsg(1))
        time.sleep(3)
        result= execmd(None)
        print "result1:"+result
        if result.find("quickconfig send complete")==-1:
            return 1
        time.sleep(60)
        execmd(None)
        time.sleep(6)
        result=execmd(None)
        print "result2:"+result
        if result.find("quickconfig send complete")!=-1:
            return 1
        return 0
  
    except Exception,e:
        print str(e)
        return 1
    

    
                               
main()
