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
{
    "uuid":"00fbfca7bf0000000000000001021717",
    "encry":"false",
    "content":{
        "method":"dm_get_dev_type_list",
        "req_id":178237278 ,
        "timestamp":1509987887,
        "msg":"success",
        "msg_tag":"",
        "code":0,
        "result":{
            "list":[
                {
                    "id":1,
                    "name":"空调",
                    "order":1,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":2,
                    "name":"窗帘",
                    "order":2,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":3,
                    "name":"电视",
                    "order":3,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":4,
                    "name":"电饭煲",
                    "order":4,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":5,
                    "name":"灯",
                    "order":5,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":6,
                    "name":"电子秤",
                    "order":6,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":7,
                    "name":"摄像头",
                    "order":7,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":8,
                    "name":"智能开关",
                    "order":8,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":9,
                    "name":"空气质量检测仪",
                    "order":9,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":10,
                    "name":"温湿度计",
                    "order":10,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":11,
                    "name":"路由器",
                    "order":11,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":12,
                    "name":"门窗传感器",
                    "order":12,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":13,
                    "name":"人体传感器",
                    "order":13,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":14,
                    "name":"可视对讲",
                    "order":14,
                    "created_at":1491376907,
                    "updated_at":1491376907
                },

                {
                    "id":15,
                    "name":"智能音箱",
                    "order":15,
                    "created_at":1491376907,
                    "updated_at":1491376907
                }
            ]
        }
    }
}
'''


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
        queue_in, queue_out = Queue.Queue(), Queue.Queue()
        client = my_socket.MyClient(
            ('192.168.10.1', 5100), self.LOG, queue_in, queue_out, debug=False, printB=True)
        client.connect()

        while client.is_connected() == False:
            self.LOG.info('wait to connect to socket server...')
            time.sleep(1)

        cmds = ['select * from table_user_list;', 'select * from table_family_list;']
        result = self.router_db_info(cmds)
        cmds = ['select * from TABLE_DEVICE_CATEGORY;']
        result2 = self.router_db_info(cmds, mode_line=False)

        msg_on = getledMsg(family_id=result[1]['id'], user_id=result[1]['user_id'], device_category_id=re.search(r'(\d+)\|灯', result2[0]).group(1))
        queue_out.put(msg_on)
        client.send_once()
        data = ''
        tmp = client.recv_once(timeout=10)
        while tmp:
            data += tmp
            tmp = client.recv_once(timeout=10)

        if data:
            self.LOG.debug(data.decode('utf-8').encode(sys.getfilesystemencoding()))
            response = json.loads(data)
            if response['content']['msg'] == 'success':
                pass
            else:
                return self.case_fail("灯品类查询失败！".decode('utf-8').encode(sys.getfilesystemencoding()))
        else:
            return self.case_fail("timeout, server no response!")

        msg_on = getledMsg(family_id=result[1]['id'], user_id=result[1]['user_id'], device_category_id=re.search(r'(\d+)\|空调', result2[0]).group(1))
        queue_out.put(msg_on)
        client.send_once()
        data = ''
        tmp = client.recv_once(timeout=10)
        while tmp:
            data += tmp
            tmp = client.recv_once(timeout=10)

        if data:
            self.LOG.debug(data.decode('utf-8').encode(sys.getfilesystemencoding()))
            response = json.loads(data)
            if response['content']['msg'] == 'success':
                pass
            else:
                return self.case_fail("空调品类查询失败！".decode('utf-8').encode(sys.getfilesystemencoding()))
        else:
            return self.case_fail("timeout, server no response!")



        msg_on = getledMsg(family_id=result[1]['id'], user_id=result[1]['user_id'], device_category_id=re.search(r'(\d+)\|窗帘', result2[0]).group(1))
        queue_out.put(msg_on)
        client.send_once()
        data = ''
        tmp = client.recv_once(timeout=10)
        while tmp:
            data += tmp
            tmp = client.recv_once(timeout=10)

        if data:
            self.LOG.debug(data.decode('utf-8').encode(sys.getfilesystemencoding()))
            response = json.loads(data)
            if response['content']['msg'] == 'success':
                pass
            else:
                return self.case_fail("窗帘品类查询失败！".decode('utf-8').encode(sys.getfilesystemencoding()))
        else:
            return self.case_fail("timeout, server no response!")


        msg_on = getledMsg(family_id=result[1]['id'], user_id=result[1]['user_id'], device_category_id=re.search(r'(\d+)\|电视', result2[0]).group(1))
        queue_out.put(msg_on)
        client.send_once()
        data = ''
        tmp = client.recv_once(timeout=10)
        while tmp:
            data += tmp
            tmp = client.recv_once(timeout=10)

        if data:
            self.LOG.debug(data.decode('utf-8').encode(sys.getfilesystemencoding()))
            response = json.loads(data)
            if response['content']['msg'] == 'success':
                pass
            else:
                return self.case_fail("电视品类查询失败！".decode('utf-8').encode(sys.getfilesystemencoding()))
        else:
            return self.case_fail("timeout, server no response!")


        msg_on = getledMsg(family_id=result[1]['id'], user_id=result[1]['user_id'], device_category_id=re.search(r'(\d+)\|路由器', result2[0]).group(1))
        queue_out.put(msg_on)
        client.send_once()
        data = ''
        tmp = client.recv_once(timeout=10)
        while tmp:
            data += tmp
            tmp = client.recv_once(timeout=10)

        if data:
            self.LOG.debug(data.decode('utf-8').encode(sys.getfilesystemencoding()))
            response = json.loads(data)
            if response['content']['msg'] == 'success':
                pass
            else:
                return self.case_fail("路由器品类查询失败！".decode('utf-8').encode(sys.getfilesystemencoding()))
        else:
            return self.case_fail("timeout, server no response!")

        return self.case_pass()


# 获取品类列表
def getMsg(family_id, user_id):
    msg_on = {
        "uuid": "111",
        "encry": "false",
        "content": {
            "method": "dm_get_dev_type_list",
            "req_id": 178237278,
            "timestamp": 1498111457196,
            "params": {
                "family_id": 1,
                "user_id": 123

            }
        }
    }
    msg_on['content']['params']['family_id'] = family_id
    msg_on['content']['params']['user_id'] = user_id
    return json.dumps(msg_on) + '\n'


# 获取品类列表
def getledMsg(family_id, user_id, device_category_id=0):
    msg_on = {
        "uuid": "111",
        "encry": "false",
        "content": {
            "method": "dm_get_devices_by_family",
            "req_id": 178237278,
            "timestamp": 1498111457196,
            "params": {
                "family_id": 1,
                "device_category_id": 14,
                "user_id": 123,
        		"page": {
        			"size": 10,
        			"begin": 0
        		}
            }
        }
    }
    msg_on['content']['params']['family_id'] = family_id
    msg_on['content']['params']['device_category_id'] = device_category_id
    msg_on['content']['params']['user_id'] = user_id
    return json.dumps(msg_on) + '\n'


def md5(strtext):
        m2 = hashlib.md5()
        m2.update(strtext)
        return str(m2.hexdigest())

def getMsgLogin():
    pwd="12345678"
    phone="18676680731"
    md5str=md5(pwd)
    msg_login = '{"uuid": "111","encry": "false","content": {"method": "um_login_pwd","timestamp": 12345667,"req_id": 123,"params": {"phone": "'+phone+'","pwd":"'+md5str+'","os_type": "Android","app_version":"v0.5",\
"os_version":"android4.3","hardware_version":"Huawei"}}}\n'
    return str(msg_login)
