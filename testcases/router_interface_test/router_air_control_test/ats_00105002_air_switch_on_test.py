# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import re
import sys
import time

import APIs.common_APIs as common_APIs
import APIs.common_methods as common_methods
from APIs.common_APIs import register_caseid
from router_msg.air_control import API_air_control
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
                device_category_id=1, room_id=2)
            if common_para_dict['device_uuid']:
                pass
            else:
                return self.case_fail()

        # build msg
        login_msg = API_air_control.build_msg_air_switch(
            common_para_dict, 'on')

        # send msg to router
        if self.socket_send_to_router(json.dumps(login_msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router(timeout=5)
        if data:
            dst_package = self.get_package_by_keyword(
                data, ['dm_set', 'success'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
                "method": "dm_set",
                "req_id": "no_need",
                "timestamp": "no_need",
                "msg": "success",
                "code": 0,
                "result": {
                    "device_uuid": common_para_dict['device_uuid'],
                    "user_id": -1
                },
            },
            "encry": "no_need",
            "uuid": "no_need",
        }
        if self.json_compare(template, dst_package[0]):
            pass
        else:
            return self.case_fail("msg check failed!")
        return self.case_pass()


if __name__ == '__main__':
    Test().test()
