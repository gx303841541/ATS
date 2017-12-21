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
        result11 = self.get_router_db_info(['select * from TABLE_DEVICE_SHORTCUTS where room_id = 1 and id = 1;'])
        result12 = self.get_router_db_info(['select * from TABLE_DEVICE_SHORTCUTS where room_id = 1 and id = 2;'])

        # build msg
        shortcut_list = [
            {
                "shortcut_id": 1,
                "order": result12[1]['device_order']
            },
            {
                "shortcut_id": 2,
                "order": result11[1]['device_order']
            }
        ]

        msg = API_room_homepage_management.build_msg_set_shortcut_sort(common_para_dict, shortcut_list=shortcut_list)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_sort_shortcut', 'result'], except_keyword_list=['mdp_msg'])
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
                "method": "dm_sort_shortcut",
                "result": {
                    "user_id": common_para_dict["user_id"],
                    "room_id": common_para_dict["room_id"],
                    "family_id": common_para_dict["family_id"],
                    "list" : [
                        {
                            'shortcut_id': 1,
                            'order': result12[1]['device_order']
                        },
                        {
                            'shortcut_id': 2,
                            'order': result11[1]['device_order']
                        }
                    ]
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
        result21 = self.get_router_db_info(['select * from TABLE_DEVICE_SHORTCUTS where room_id = 1 and id = 1;'])
        result22 = self.get_router_db_info(['select * from TABLE_DEVICE_SHORTCUTS where room_id = 1 and id = 2;'])
        if result11[1]['device_order'] == result22[1]['device_order'] and result12[1]['device_order'] == result21[1]['device_order']:
            # build msg
            shortcut_list = [
                {
                    "shortcut_id": 1,
                    "order": 1
                },
                {
                    "shortcut_id": 2,
                    "order": 2
                }
            ]
            msg = API_room_homepage_management.build_msg_set_shortcut_sort(common_para_dict, shortcut_list=shortcut_list)
            # send msg to router
            if self.socket_send_to_router(json.dumps(msg) + '\n'):
                pass
            else:
                return self.case_fail("Send msg to router failed!")
        else:
            return self.case_fail("DB check add shortcut fail!")
        return self.case_pass()


if __name__ == '__main__':
    Test().test()
