# -*- coding: utf-8 -*-
import os
import sys
import re
import time
import datetime
import json
import random
import Queue
import hashlib
import winpexpect

from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods
import my_socket.my_socket as my_socket


'''
1|空调|1|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
2|窗帘|2|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
3|电视|3|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
4|电饭煲|4|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
5|灯|5|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
6|电子秤|6|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
7|摄像头|7|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
8|智能开关|8|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
9|空气质量检测仪|9|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
10|温湿度计|10|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
11|路由器|11|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
12|门窗传感器|12|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
13|人体传感器|13|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
14|可视对讲|14|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47
15|智能音箱|15|1491376907|2017-04-05 15:21:47|1491376907|2017-04-05 15:21:47'''


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):
    def run(self):
        client = my_socket.MyClient(
            ('192.168.10.1', 5100), self.LOG, Queue.Queue(), Queue.Queue(), debug=True, printB=False)
        client.connect()

        while client.is_connected() == False:
            self.LOG.info('wait to connect to socket server...')
            time.sleep(1)

        cmds = ['select * from table_user_list;', 'select * from table_family_list;']
        result = self.router_db_info(cmds)

        msg_on = getledMsg(family_id=result[1]['id'], user_id=result[1]['user_id'], device_category_id=1)
        client.send_once(msg_on)
        data = ''
        tmp = client.recv_once(timeout=5)
        while tmp:
            data += tmp
            tmp = client.recv_once(timeout=5)

        if data:
            self.LOG.debug(self.convert_to_dictstr(data))
        else:
            return self.case_fail("timeout, server no response!")

        return self.case_pass()


# 获取品类列表
def getledMsg(family_id, user_id, device_category_id=0):
    msg_on = {
        "uuid": "111",
        "encry": "false",
        "content": {


        	"method": " dm_set_shortcut_mode ",
        	"req_id": 178237278,
        	"timestamp": 1498111457196,
        	"params": {
        		"family_id": 1001,
        		"room_id": 2,
        		"mode": "on"
        	}



        }
    }
    msg_on['content']['params']['family_id'] = family_id
    #msg_on['content']['params']['device_category_id'] = device_category_id
    #msg_on['content']['params']['user_id'] = user_id
    return json.dumps(msg_on) + '\n'
