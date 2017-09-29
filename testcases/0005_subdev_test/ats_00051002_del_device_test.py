# -*- coding: utf-8 -*-
import os, sys, re, time
import datetime
import json
import threading
import random
import socket

sys.path.append(os.path.abspath('.'))
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        return main()

        

def getDelMsg(uuid):
        num=random.randint(100, 9999999)
        msg_on = '{"uuid": "111","encry": "false","content": {"method": "dm_del_device","timestamp": 1494916080598,"req_id": '+str(num)+',"params": {"family_id": 1,"device_uuid": "'+str(uuid)+'","user_id": 1012}}}\n'
        print msg_on
        global req_id
        req_id=str(num)
        return str(msg_on)


def WriteToFile(filename, data):
	# filename: Full path to file
	# data: data to be written to the szFile
	f = file(filename, 'a')
	f.write(data)
	f.close()
	
	
hoststr="192.168.10.1"
port=5100
sck=None
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
                
def msgSend(msg):
    sendMsg(msg)
    sendtime=datetime.datetime.now()
    print str(sendtime)+"   sended the Del Device message  \r\n"
    WriteToFile('Log_Device.txt',str(sendtime) + "   sended message  " + "\r\n")

        
        

def loopRece():
        while(True):
                if sck is not None:
                        try:
                                data = sck.recv(1024)
                                on_message(data)
                        except Exception,e:
                                pass
                else:
                        global sck
                        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sck.connect((hoststr, port))
                        print "connection invalid"

def startRece():
    th = threading.Thread(target=loopRece)
    th.setDaemon(True)
    th.start()


deviceuuid1='050000000100000188597201008d1500'
deviceuuid2='xxxx'
def main():
        global sendtime
        sendtime=datetime.datetime.now()
        startRece()
        time.sleep(2)
        msgSend(getDelMsg(deviceuuid1))
        time.sleep(20)
        msgSend(getDelMsg(deviceuuid2))
        time.sleep(20)
        if ispass is not None:
            return 0
        else:
            return 1

uuid=''
sendtime=''
req_id=''
ispass=None
def on_message(message):
    strjson=json.loads(message)
    strjson=strjson['content']
    if (strjson.has_key('msg')):
            if str(strjson['msg'])=='success':
                    if (strjson.has_key('method')):
                            method=str(strjson['method'])                    
                            if method=='dm_del_device':
                                    print strjson
                                    recetime=datetime.datetime.now()
                                    print 'sendtime: '+str(recetime)
                                    print "退网成功"
                                    global ispass
                                    ispass="ok"
                                    print str(recetime)+"   received the message :  "+str(recetime)
                                    WriteToFile('Log_Device.txt',str(recetime) + "  the Sub Device has been deleted successfully " +"\r\n")
                                    
                           
#main()
