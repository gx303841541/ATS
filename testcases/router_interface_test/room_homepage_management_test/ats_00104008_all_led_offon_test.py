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
        	"room_id": 1,
    		"user_id": self.common_para_dict["user_id"],
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

        # build msg
        msg = API_room_homepage_management.build_msg_all_led_offon(common_para_dict, offon='off')

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_set_light_control', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
                "method": "dm_set_light_control",
                "req_id": "no_need",
                "timestamp": "no_need",
                "msg": "success",
                "code": 0,
            	"result": {
                    "family_id": common_para_dict['family_id'],
            		"user_id": common_para_dict['user_id']
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
        result = self.get_router_db_info(['select * from TABLE_ZIGBEE_DEVICE where device_uuid = "%s";' % common_para_dict["device_uuid"]])
        if 'device_uuid' in result[1]:
            if not re.search(r'switch_status":"off"', result[1]['attribute']):
                return self.case_fail("Led off fail!")
        else:
            return self.case_fail("DB check fail!")

        # build msg
        msg = API_room_homepage_management.build_msg_all_led_offon(common_para_dict, offon='on')

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_set_light_control', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
                "method": "dm_set_light_control",
                "req_id": "no_need",
                "timestamp": "no_need",
                "msg": "success",
                "code": 0,
            	"result": {
                    "family_id": common_para_dict['family_id'],
            		"user_id": common_para_dict['user_id']
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
        result = self.get_router_db_info(['select * from TABLE_ZIGBEE_DEVICE where device_uuid = "%s";' % common_para_dict["device_uuid"]])
        if 'device_uuid' in result[1]:
            if not re.search(r'switch_status":"on"', result[1]['attribute']):
                return self.case_fail("Led on fail!")
        else:
            return self.case_fail("DB check fail!")

        return self.case_pass()


if __name__ == '__main__':
    Test().test()