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

@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):
    def run(self):
        error_flag = 0
        common_para_dict = {
            "family_id": self.common_para_dict["family_id"],
            "user_id": self.common_para_dict["user_id"],
            "room_id": 1
        }

        # delete all device
        if self.delete_all_wifi_devices() and self.delete_all_zigbee_devices():
            pass
        else:
            return self.case_fail()

        # add devices
        if self.add_wifi_device(device_category_id=1, room_id=2) and self.add_zigbee_device(device_category_id=5, room_id=3):
            pass
        else:
            return self.case_fail()

        # build msg
        common_para_dict['room_id'] = 2
        msg = API_device_management.build_msg_get_device_list_by_room(common_para_dict)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_get_devices_by_room', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
            	"method": "dm_get_devices_by_room",
            	"req_id": "no_need",
            	"timestamp": "no_need",
            	"msg": "success",
            	"code": 0,
            	"result": {
                    "user_id": common_para_dict['user_id'],
                    "family_id": common_para_dict['family_id'],
            		"list": [{
            			"device_id": "no_need",
            			"device_uuid": "no_need",
            			"family_id": common_para_dict['family_id'],
            			"room_id": common_para_dict['room_id'],
            			"device_category_id": 1,
            			u"device_name": u"柜式空调",
            			"default_device_name": "no_need",
            			"attribute":"no_need",
            			"created_at": "no_need",
            			"updated_at": "no_need",
            		}],
            		"more": 0
            	}
        	},
            "encry": "no_need",
            "uuid": "no_need",
        }
        if self.json_compare(template, dst_package[0]):
            pass
        else:
            error_flag = 1

        # build msg
        common_para_dict['room_id'] = 3
        msg = API_device_management.build_msg_get_device_list_by_room(common_para_dict)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_get_devices_by_room', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
            	"method": "dm_get_devices_by_room",
            	"req_id": "no_need",
            	"timestamp": "no_need",
            	"msg": "success",
            	"code": 0,
            	"result": {
                    "user_id": common_para_dict['user_id'],
                    "family_id": common_para_dict['family_id'],
            		"list": [{
            			"device_id": "no_need",
            			"device_uuid": "no_need",
            			"family_id": common_para_dict['family_id'],
            			"room_id": common_para_dict['room_id'],
            			"device_category_id": 5,
            			"device_name": "no_need",
            			"default_device_name": "no_need",
            			"attribute":"no_need",
            			"created_at": "no_need",
            			"updated_at": "no_need",
            		}],
            		"more": 0
            	}
        	},
            "encry": "no_need",
            "uuid": "no_need",
        }
        if self.json_compare(template, dst_package[0]):
            pass
        else:
            error_flag = 1

        if error_flag:
            return self.case_fail("msg check failed!")
        else:
            return self.case_pass()


if __name__ == '__main__':
    Test().test()
