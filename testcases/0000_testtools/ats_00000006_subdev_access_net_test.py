#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
sys.path.append(os.path.abspath('.'))
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods

import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish
import datetime
import json
import threading
import time
import random

import serial
import time


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        return main()


class relay():
    def __init__(self):
        pass

    def relay(self, com, mes):
        connected = False
        ser = serial.Serial(com, 9600)
        print str(ser)
        while not connected:
            serin = ser.read()
            connected = True
        ser.write(mes)
        ret = ser.read()
        ser.close()
        return ret


# category,智能灯为5，wifi模块为1
category = 5

# 子设备的uuid
deviceuuid = 'C85B765CAF52'

# 升级包的地址
packageurl = "http://192.168.10.1/BH-MW100-ota-v0.3.0-201708091533.bin"


def getAddMsg(category):
    num = random.randint(100, 9999999)
    msg_on = '{"method": "addDevice","req_id": ' + \
        str(num) + ',"params": {"category": ' + str(category) + '}}'
    print msg_on
    global req_id
    req_id = str(num)
    return str(msg_on)


def getDelMsg(uuid):
    num = random.randint(100, 9999999)
    msg_on = '{"method": "removeDevice","req_id": ' + \
        str(num) + ',"params": {"device_uuid": "' + uuid + '"}}'
    print msg_on
    global req_id
    req_id = str(num)
    return str(msg_on)


def getUpgradeMsg(uuid):
    num = random.randint(100, 9999999)
    msg_on = '{"method": "ota","req_id": ' + \
        str(num) + ',"nodeid":"","params": {"device_uuid": "' + \
        uuid + '","attr": {"url": "' + packageurl + '"}}}'
    print msg_on
    req_id = str(num)
    return str(msg_on)


uuid = ''
th = ''


def on_message(client, userdata, message):
    global uuid
    dtime = str(datetime.datetime.now())
    print dtime
    strjson = json.loads(message.payload)
    if (not strjson.has_key('req_id')):
        return
    if (strjson.has_key('req_id')):
        result = strjson['result']
        uuid = str(result['device_uuid'])

        if str(strjson['req_id']) == req_id:
            recetime = datetime.datetime.now()
            delaytime = recetime - sendtime
            print "入网成功，获取uuid为: " + uuid
            # print str(strjson)
            print str(recetime) + "   received the message, delay time is:  " + str(delaytime)
            WriteToFile('Log_Device.txt', str(recetime) + "uuid is: " +
                        uuid + ", delay time is:  " + str(delaytime) + "\r\n")
            client.disconnect()
            global deviceuuid
            deviceuuid = uuid
            #global deviceuuid
            main()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # 连接完成之后订阅主题
    client.subscribe("HD_IOT/router/publish")


def WriteToFile(filename, data):
    # filename: Full path to file
    # data: data to be written to the szFile
    f = file(filename, 'a')
    f.write(data)
    f.close()


def loopSend(client, category):
    i = 0
    while(i < 1):
        client.publish("HD_IOT/app/control", getAddMsg(category))
        global sendtime
        sendtime = datetime.datetime.now()
        print str(sendtime) + "   sended the Add Device message  \r\n"
        WriteToFile('Log_Device.txt', str(sendtime) +
                    "   sended the Add Device message  " + "\r\n")
        time.sleep(2)
        i = i + 1

# 发送入网消息


def sendAddMsg(client, category):
    client.publish("HD_IOT/app/control", getAddMsg(category))
    global sendtime
    sendtime = datetime.datetime.now()
    print str(sendtime) + "   sended the Add Device message  \r\n"
    WriteToFile('Log_Device.txt', str(sendtime) +
                "   sended the Add Device message  " + "\r\n")
    # main()

# 发送离网消息


def sendDelMsg(client, uuid):
    client.publish("HD_IOT/app/control", getDelMsg(uuid))
    global sendtime
    sendtime = datetime.datetime.now()
    print str(sendtime) + "   sended the Del Device message  \r\n"
    WriteToFile('Log_Device.txt', str(sendtime) +
                "   sended the Del Device message  " + "\r\n")
    # main()


def startSend(client):

    th = threading.Thread(target=loopSend, args=(client, category,))
    th.setDaemon(True)
    th.start()


def loopRece(client):
    client.loop_forever()


def startRece(client):
    th = threading.Thread(target=loopRece, args=(client,))
    th.setDaemon(True)
    th.start()


# wifi模块升级代码
def sendUpgradeMsg(client, uuid):
    client.publish("HD_IOT/app/control", getUpgradeMsg(uuid))
    global sendtime
    sendtime = datetime.datetime.now()
    print str(sendtime) + "   sended the Upgrade Device message  \r\n"
    WriteToFile('Log_Device.txt', str(sendtime) +
                "   sended the Upgrade Device message  " + "\r\n")


def main():
    # 初始化继电器
    # connrelay=relay()
    # 控制arduino打开继电器开关，O为打开，C为关闭
    # connrelay.relay('COM5','O')
    client = mqtt.Client()
    while True:
        a = raw_input(
            "请选择测试类型 \n1.入网（并获取uuid）\n2.入网\n3.退网\n4.入/退网循环\n5.WIFI模块升级\n请输入：".decode('utf-8').encode('gbk'))
        print a
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect("192.168.10.1", 1883, 60)
        if(a == '1'):
            startSend(client)
            startRece(client)
        elif(a == '2'):
            sendAddMsg(client, category)
        elif(a == '3'):
            sendDelMsg(client, deviceuuid)

        elif(a == '4'):
            i = 0
            while(i < 200):
                # 发送添加设备MQTT消息
                sendAddMsg(client, category)
                # 休眠15秒(可配置)，等待设备入网
                time.sleep(15)
                # 发送删除设备MQTT消息
                sendDelMsg(client, deviceuuid)
                # 关闭并打开继电器1次，'O'为打开，如果已经打开，则为关闭后重新打开（此操作为了智能灯重新发送入网信号）
                # connrelay.relay('COM5','O')
                i = i + 1

        elif(a == '5'):
            sendUpgradeMsg(client, deviceuuid)
        else:
            print "输入错误，请重新输入".decode('utf-8').encode('gbk')
