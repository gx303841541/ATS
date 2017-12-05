#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""rest api
2017-9-20
"""

import requests
from collections import OrderedDict
import json, ast
import random
import datetime
import sys


class Http():
    def __init__(self, router_url='http://192.168.10.1/cgi-bin/test1', logger=None):
        self.router_url = router_url

    #路由器当前上网方式
    def getCurrentWanConfig(self):
        num=random.randint(100, 9999999)
        msg_on = {
            "method": "getCurrentWanConfig",
            "req_id": '+str(num)+',
            "timestamp": 1498111457196,
            "params": {}
        }
        return self.httpsend(json.dumps(msg_on))

    #路由器密码设置
    def setRouterPassword(self):
        num=random.randint(100, 9999999)
        msg_on = {
            "method": "setRouterPassword",
            "req_id": '+str(num)+',
            "timestamp": 1498111457196,
            "params": {
                "password": 123123,
            }
        }
        return self.httpsend(json.dumps(msg_on))

    #路由器密码验证
    def verifyRouterPassword(self):
        num=random.randint(100, 9999999)
        msg_on = {
            "method": "verifyRouterPassword",
            "req_id": '+str(num)+',
            "timestamp": 1498111457196,
            "params": {
                "password": 123123,
            }
        }
        return self.httpsend(json.dumps(msg_on))

    #路由器默认上网方式
    def getDefaultWanConfig(self):
        num=random.randint(100, 9999999)
        msg_on = {
            "method": "getDefaultWanConfig",
            "req_id": '+str(num)+',
            "timestamp": 1498111457196,
            "params": {}
        }
        return self.httpsend(json.dumps(msg_on))

    #路由器配置DHCP
    def setDHCPConfig(self):
        num=random.randint(100, 9999999)
        msg_on = {
            "method": "setDHCPConfig",
            "req_id": '+str(num)+',
            "timestamp": 1498111457196,
            "params": {
                "primary_dns":"foo",
                "second_dns":"foo",
            }
        }
        return self.httpsend(json.dumps(msg_on))

    #路由器配置pppoe
    def setADSLConfig(self):
        num=random.randint(100, 9999999)
        msg_on = {
            "method": "setADSLConfig",
            "req_id": '+str(num)+',
            "timestamp": 1498111457196,
            "params": {
                "user":"foo",
                "password":"secret"
            }
        }
        return self.httpsend(json.dumps(msg_on))

    #路由器配置静态上网方式
    def setStaticWanConfig(self):
        num=random.randint(100, 9999999)
        msg_on = {
            "method": "setStaticWanConfig",
            "req_id": '+str(num)+',
            "timestamp": 1498111457196,
            "params": {
                "ip":"foo",
                "mask":"foo",
                "gateway":"foo",
                "primary_dns":"foo",
                "second_dns":"foo",
            }
        }
        return self.httpsend(json.dumps(msg_on))


    #路由器是否已经配置接口
    def isRouterSetupDone(self):
        num=random.randint(100, 9999999)
        msg_on = {
            "method": "isRouterSetupDone",
            "req_id": '+str(num)+',
            "timestamp": 1498111457196,
            "params": {}
        }
        return self.httpsend(json.dumps(msg_on))

    #设置路由器SSID和密码
    def setSSIDConfig(self, ssid='FOO', password='87654321'):
        num=random.randint(100, 9999999)
        msg_on = {
            "method": "setSSIDConfig",
            "req_id": '+str(num)+',
            "timestamp": 1498111457196,
            "params": {
                "enable":1,
                "SSID": "FOO",
                "password":"123123",
                "hide":0
            }
        }
        msg_on["params"]['SSID'] = ssid
        msg_on["params"]["password"] = password
        return self.httpsend(json.dumps(msg_on))

    #设置路由器SSID和密码
    def setSSIDConfig_5G(self, ssid='FOO', password='87654321'):
        num=random.randint(100, 9999999)
        msg_on = {
            "method": "setSSIDConfig_5G",
            "req_id": '+str(num)+',
            "timestamp": 1498111457196,
            "params": {
                "enable":1,
                "SSID": "FOO",
                "password":"87654321",
                "hide":0
            }
        }
        msg_on["params"]['SSID'] = ssid
        msg_on["params"]["password"] = password
        return self.httpsend(json.dumps(msg_on))

    #查询路由器类型
    def isValidRouter(self):
        num=random.randint(100, 9999999)
        msg_on = {
            "method": "isValidRouter",
            "req_id": '+str(num)+',
            "timestamp": 1498111457196,
            "params": {}
        }
        return self.httpsend(json.dumps(msg_on))


    def send(self, msg_on={}):
        return self.httpsend(json.dumps(msg_on))

    #发送http消息
    def httpsend(self, jsonstr):
        headers = {}
        req = requests.post(self.router_url, headers=headers, data=jsonstr)
        if req:
            return json.loads(req.text, encoding="gbk")
        else:
            print('Timeout!')


if __name__ == '__main__':
    a = Http()
    msg_on = {
        "method": "getCurrentWanConfig",
        "timestamp": 1490229730,
        "req_id": 123,
        "params": {
            "family_id": 1,
            "user_id": 123
        }
    }

    s = a.send(msg_on)
    if s:
        print repr(s)
    else:
        print ('Fuck')
