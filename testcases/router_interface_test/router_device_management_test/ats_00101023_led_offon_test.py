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
            # add WIFI device
            # build msg
            msg = API_device_management.build_msg_add_device(common_para_dict, device_category_id=5)

            # send msg to router
            if self.socket_send_to_router(json.dumps(msg) + '\n'):
                self.robot.led_access_net()
                def add_success():
                    ret = self.socket_recv_from_router(timeout=1)
                    if self.get_package_by_keyword(ret, ['dm_add_device', 'success'], except_keyword_list=['mdp_msg']):
                        return 1
                    else:
                        return 0
                if self.mysleep(65, feedback=add_success):
                    self.LOG.info('Add device already success!')
                    result = self.get_router_db_info(['select * from TABLE_ZIGBEE_DEVICE;'])
                    common_para_dict['device_uuid'] = result[1]['device_uuid']
                else:
                    return self.case_fail("Add device already fail!")
            else:
                return self.case_fail("Send msg to router failed!")

        # build msg
        login_msg = API_device_management.build_msg_login_router(self.common_para_dict["phone"], common_APIs.get_md5(self.config_file.get("app", "login_pwd")))

        # send msg to router
        if self.socket_send_to_router(json.dumps(login_msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['um_login_pwd', 'success'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # build msg
        msg = API_device_management.build_msg_led_control(common_para_dict, on_off=random.choice(['off', 'on']))

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
            "content": {
            	"uuid": "111",
            	"encry": "false",
            	"content": {
            		"method": "mdp_msg",
            		"timestamp": "no_need",
            		"req_id": "no_need",
            		"params": {
            			"msg_type": "R2F",
            			"target_id": "no_need",
            			"content": {
            				"method": "report",
            				"result": {
            					"device_uuid": common_para_dict['device_uuid'],
            					"attribute": {
            						"temperature": "no_need",
            						"r": "no_need",
            						"g": "no_need",
            						"b": "no_need",
            						"mode": "no_need",
            						"level": "no_need",
            					}
            				}
            			}
            		}
            	}
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
