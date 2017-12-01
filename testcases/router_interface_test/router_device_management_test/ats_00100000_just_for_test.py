# -*- coding: utf-8 -*-
import os
import sys
import re
import time
import datetime
import json
import random

from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


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

        return self.case_pass()


        common_para_dict = {
            "family_id": 4044,
            "user_id": 4043,
            "room_id": 1
        }

        # msg check
        template = {
            "content": {
                "code": 0,
                "method": " dm_add_device ",
                "msg": "success",
                "msg_tag": "no_need",
                "req_id": "no_need",

        	},
            u"name": u"宫勋",
            "encry": "no_need",
            "uuid": "no_need",
        }
        if self.json_compare(template, '{"1":"宫勋"}'):
            pass
        else:
            return self.case_fail("msg check failed!")
        return self.case_pass()


        self.dict_items_compare(msg_on, msg_down)
        return self.case_pass()


        cmds = ['select * from table_user_list;', 'select * from table_family_list;']
        result = self.get_router_db_info(cmds)
        self.LOG.debug(self.convert_to_dictstr(result[1]))
        msg_on = getledMsg(family_id=result[1]['id'], user_id=result[1]['user_id'], device_category_id=1)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg_on) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            self.LOG.debug(self.convert_to_dictstr(data))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        if self.json_items_compare(template, data):
            pass
        else:
            return self.case_fail("msg check failed!")
        return self.case_pass()



if __name__ == '__main__':
    Test().test()
