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
import APIs.common_APIs as common_APIs
from router_msg.router_device_management import API_device_management
from router_msg.device_control import API_device_control


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):
    def run(self):
        # 数据库查询
        result = self.get_router_db_info(['select * from TABLE_ZIGBEE_DEVICE;'])
        common_para_dict = {
            "family_id": self.common_para_dict["family_id"],
            "user_id": self.common_para_dict["user_id"],
            "router_id": self.common_para_dict["router_id"],
            "room_id": 1
        }

        if result and 'device_uuid' in result[1]:
            common_para_dict['device_uuid'] = result[1]['device_uuid']
        else:
            # add zigbee device
            common_para_dict['device_uuid'] = self.add_zigbee_device(device_category_id=5, room_id=1)
            if common_para_dict['device_uuid']:
                pass
            else:
                return self.case_fail()

        # build msg
        level = random.randint(0, 256)
        msg = API_device_control.build_msg_led_light_control(common_para_dict, level=level)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            time.sleep(5)
        else:
            return self.case_fail("Send msg to router failed!")

        # DB check
        result = self.get_router_db_info(['select * from TABLE_ZIGBEE_DEVICE where device_uuid = "%s";' % common_para_dict["device_uuid"]])
        if 'device_uuid' in result[1]:
            if not re.search(r'"level":%d' % (level), result[1]['attribute']):
                return self.case_fail("Led ligth control fail!")
        else:
            return self.case_fail("DB check fail!")
        return self.case_pass()


if __name__ == '__main__':
    Test().test()
