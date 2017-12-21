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
        msg = API_device_control.build_msg_led_switch(common_para_dict, on_off=random.choice(['off', 'on']))

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router(timeout=5)
        if data:
            dst_package = self.get_package_by_keyword(data, ['mdp_msg', 'report'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
        	"uuid": "no_need",
        	"encry": "no_need",
        	"content": {
        		"method": "mdp_msg",
        		"timestamp": "no_need",
        		"req_id": "no_need",
        		"params": {
        			"msg_type": "no_need",
        			"target_id": "no_need",
        			"content": {
        				"method": "dr_report_dev_status",
        				"result": {
        					"timestamp": "no_need",
        					"status_modified_at": "no_need",
        					"family_id": "no_need",
                            "device_id": "no_need",
                            "device_uuid": "no_need",
                            "device_category_id": "no_need",
                            "updated_at": "no_need",
        					"attribute": {
        						"temperature": "no_need",
        						"r": "no_need",
        						"g": "no_need",
        						"b": "no_need",
        						"switch_status": "no_need",
        						"level": "no_need",
                                "connectivity": "no_need",
                                "hue": "no_need",
                                "saturation": "no_need",
        					}
        				}
        			}
        		}
        	}
        }

        if self.json_compare(template, dst_package[0]):
            pass
        else:
            return self.case_fail("msg check failed!")
        return self.case_pass()


if __name__ == '__main__':
    Test().test()
