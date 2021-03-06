# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import re
import sys
import time

import APIs.common_methods as common_methods
from APIs.common_APIs import register_caseid
from router_msg.room_hoompage_management import API_room_homepage_management
from router_msg.router_device_management import API_device_management


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):
    def run(self):
        # 数据库查询
        result = self.get_router_db_info(['select * from TABLE_WIFI_DEVICE;'])
        common_para_dict = {
            "family_id": self.common_para_dict["family_id"],
            "user_id": self.common_para_dict["user_id"],
            "room_id": 1
        }
        if result and 'device_uuid' in result[1]:
            common_para_dict['device_uuid'] = result[1]['device_uuid']
        else:
            # add WIFI device
            common_para_dict['device_uuid'] = self.add_wifi_device(
                device_category_id=1, room_id=1)
            if common_para_dict['device_uuid']:
                pass
            else:
                return self.case_fail()
        result = self.get_router_db_info(
            ['delete from TABLE_DEVICE_SHORTCUTS where id > 12;'])

        # build msg
        msg = API_room_homepage_management.build_msg_add_shortcut_sort(
            common_para_dict, device_category_id=1, name=u"空调", order=3, mode='on', attribute={"speed": "high"})

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(
                data, ['dm_add_shortcut', 'result'], except_keyword_list=['mdp_msg'])
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
                "method": "dm_add_shortcut",
                "result": {
                    "shortcut_id": 13,
                    "user_id": common_para_dict["user_id"],
                    "room_id": common_para_dict["room_id"],
                    "family_id": common_para_dict["family_id"],
                    "name": u"空调-风速",
                    "device_category_id": 1,
                    "order": 3,
                    "content": [
                        {
                            "device_uuid": common_para_dict["device_uuid"],
                            "attribute": "no_need",
                        },
                    ],
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
        result = self.get_router_db_info(
            ['select *  from TABLE_DEVICE_SHORTCUTS where room_id = 1 and device_order = 3;'])
        if 'id' in result[1]:
            return self.case_fail("DB check add shortcut fail!")
        return self.case_pass()


if __name__ == '__main__':
    Test().test()
