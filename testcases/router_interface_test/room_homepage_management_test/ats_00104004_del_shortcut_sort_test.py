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
from router_msg.router_device_management import API_device_management
from router_msg.room_hoompage_management import API_room_homepage_management

@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):
    def run(self):
        # 数据库查询
        common_para_dict = {
            "family_id": self.common_para_dict["family_id"],
            "user_id": self.common_para_dict["user_id"],
            "room_id": 1
        }
        result = self.get_router_db_info(['select * from TABLE_WIFI_DEVICE;'])
        if result and 'device_uuid' in result[1]:
            common_para_dict['device_uuid'] = result[1]['device_uuid']
        else:
            # add WIFI device
            common_para_dict['device_uuid'] = self.add_wifi_device(device_category_id=1, room_id=1)
            if common_para_dict['device_uuid']:
                pass
            else:
                return self.case_fail()
        result = self.get_router_db_info(['delete from TABLE_DEVICE_SHORTCUTS where id > 12;'])

        # build add shortcut msg
        msg = API_room_homepage_management.build_msg_add_shortcut_sort(common_para_dict, device_category_id=1, name=u"空调-风速", order=3, mode='on', attribute={"speed": "high"})

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_add_shortcut', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")
        shortcut_id = json.loads(dst_package[0])['content']['result']['shortcut_id']

        # build msg
        msg = API_room_homepage_management.build_msg_del_shortcut_sort(common_para_dict, shortcut_id=shortcut_id)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_del_shortcut', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
                "code": 0,
                "msg": "success",
                "req_id": "no_need",
                "msg_tag": "no_need",
                "timestamp": "no_need",
                "method": "dm_del_shortcut",
                "result": {
                    "shortcut_id": shortcut_id,
                    "user_id": common_para_dict["user_id"],
                    "room_id": common_para_dict["room_id"],
                    "family_id": common_para_dict["family_id"],
                }
            },
            "encry": "no_need",
            "uuid": "no_need",
        }
        if self.json_compare(template, dst_package[0]):
            pass
        else:
            return self.case_fail("msg check failed!")

        # DB check
        result = self.get_router_db_info(['select * from TABLE_DEVICE_SHORTCUTS where room_id = 1 and device_order = 3;'])
        if 'id' in result[1]:
            self.LOG.warn(str(result))
            return self.case_fail("DB check add shortcut fail!")
        return self.case_pass()

if __name__ == '__main__':
    Test().test()
