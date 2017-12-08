# -*- coding: utf-8 -*-
import os
import sys
import re
import time
import datetime
import json
import random
import Queue

from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods
import connections.my_socket as my_socket

@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        self.serial.open()
        self.serial.send("kill -9 $(pidof wifi_mgr)")
        self.serial.send("wifi_mgr ath02 -d")

        msg_on = getAddMsg(1)
        queue_in, queue_out = Queue.Queue(), Queue.Queue()
        client = my_socket.MyClient(('192.168.10.1', 5100), self.LOG, queue_in, queue_out, debug=True)
        client.connect()
        self.LOG.debug(msg_on)
        queue_out.put(msg_on)
        client.send_once()
        time.sleep(3)
        result = self.serial.readall()
        self.LOG.debug("result1:" + result)
        if result.find("quickconfig send complete") == -1:
            return self.case_fail('not find: "quickconfig send complete" in [%s]' % (result))
        time.sleep(60)
        self.serial.readall()
        time.sleep(6)
        result = self.serial.readall()
        self.serial.send('\x03')
        self.LOG.debug("result2:" + result)
        if result.find("quickconfig send complete") != -1:
            return self.case_fail('find again: "quickconfig send complete" in [%s]' % (result))
        return self.case_pass()


# 添加设备消息
def getAddMsg(category):
    msg_on = {
        "uuid": "111",
        "encry": "false",
        "content": {
            "method": "dm_add_device",
            "timestamp": 1494916080598,
            "req_id": '',
            "params": {
                "device_category_id": '',
                "family_id": 1,
                "room_id": 1,
                "user_id": 1012
            }
        }
    }
    num = random.randint(100, 9999999)
    msg_on['content']['req_id'] = 123456
    msg_on['content']['params']['device_category_id'] = category
    return json.dumps(msg_on) + '\n'
