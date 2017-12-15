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
        	"room_id": '',
    		"user_id": self.common_para_dict["user_id"],
            "shortcut_id": '',
        }
        result = self.get_router_db_info(['select * from TABLE_ZIGBEE_DEVICE where device_type_id = 5;'])
        if result and 'device_uuid' in result[1]:
            common_para_dict['device_uuid'] = result[1]['device_uuid']
            common_para_dict['room_id'] = int(result[1]['room_id'])
            common_para_dict['name'] = result[1]['device_name']
        else:
            # add device
            common_para_dict['device_uuid'] = self.add_zigbee_device(device_category_id=5, room_id=1)
            if common_para_dict['device_uuid']:
                result = self.get_router_db_info(['select * from TABLE_ZIGBEE_DEVICE;'])
                common_para_dict['device_uuid'] = result[1]['device_uuid']
                common_para_dict['room_id'] = int(result[1]['room_id'])
                common_para_dict['name'] = result[1]['device_name']
            else:
                return self.case_fail()

        result = self.get_router_db_info(['select * from TABLE_DEVICE_SHORTCUTS where id = 1;'])
        if 'name' in result[1] and result[1]['name'] == u'总开关':
            pass
        else:
            result = self.get_router_db_info(['select * from TABLE_DEVICE_SHORTCUTS where id = 2;'])
        common_para_dict['shortcut_id'] = result[1]['device_order']

        # build msg
        device_list = [
            {
                "device_uuid": common_para_dict['device_uuid'],
                "device_category_id": 5,
                #"device_name": common_para_dict['name'].encode('utf-8'),
                "device_name": 123,
            },
        ]
        msg = API_room_homepage_management.build_msg_update_main_switch_shortcut(common_para_dict, device_list=device_list)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg, ensure_ascii=False, encoding='utf-8') + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router(timeout=10)
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_update_shortcut', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {

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
