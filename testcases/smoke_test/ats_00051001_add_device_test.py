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


def getAddMsg(category):
        num=random.randint(100, 9999999)
        msg_on = '{"uuid": "111","encry": "false","content": {"method": "dm_add_device","timestamp": 1494916080598,"req_id": '+str(num)+',"params": {"device_category_id": '+str(category)+',"family_id": 1,"room_id": 1,"user_id": 1012}}}\n'
        print msg_on
        global req_id
        req_id=str(num)
        return str(msg_on)

def getOnOffMsg(uuid,ops):
        num=random.randint(100, 9999999)
        ops=str(ops)
        msg_onoff='{"uuid": "111","encry": "false","content": {"method":"dm_set_zigbee_bulb","req_id":'+str(num)+',"timestamp":123456789,\
"params":{"cmd":"setOnoff","device_uuid":"'+uuid+'","attribute":{"mode":"'+ops+'"}}}}\n'
        return msg_onoff

def getOnAirConMsg(uuid,ops):
        num=random.randint(100, 9999999)
        ops=str(ops)
        msg_result='{"uuid": "111","encry": "false","content": {"method":"dm_set","req_id":'+str(num)+',\
"nodeid": "airconditioner.main.switch","params":{"device_uuid":"'+uuid+'","attribute":{"switch":"'+ops+'"}}}}\n'
        return msg_result
        




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
    print str(sendtime)+"   sended the Add Device message  \r\n"
    WriteToFile('Log_Device.txt',str(sendtime) + "   sended message  " + "\r\n")

        
        

def loopRece():
        while(True):
                if sck is not None:
                        try:
                                print "111111111"
                                data = sck.recv(1024)
                                print data
                                on_message(data)
                        except Exception,e:
                                pass
                else:
                        time.sleep(1)
                        print "connection invalid"

def startRece():
    th = threading.Thread(target=loopRece)
    th.setDaemon(True)
    th.start()



def main():
        global sendtime
        sendtime=datetime.datetime.now()
        #startRece()
        time.sleep(1)
        msgSend(getAddMsg(5))
        startRece()
        time.sleep(30)
        if deviceuuid is None:
            return 1
        msgSend(getOnOffMsg(deviceuuid,"off"))
        time.sleep(10)
        msgSend(getOnOffMsg(deviceuuid,"on"))
        time.sleep(10)
        msgSend(getAddMsg(1))
        time.sleep(20)
        msgSend(getOnAirConMsg(deviceuuid,"off"))
        time.sleep(10)
        msgSend(getOnAirConMsg(deviceuuid,"on"))
        if ispass is not None:
            return 0
        else:
            return 1

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
                                    
                           
#main()
