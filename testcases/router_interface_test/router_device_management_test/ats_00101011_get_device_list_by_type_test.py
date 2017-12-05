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
        # 数据库查询
        common_para_dict = {
            "family_id": self.common_para_dict["family_id"],
            "user_id": self.common_para_dict["user_id"],
            "router_id": self.common_para_dict["router_id"],
        }
        for room_id in [2, 3]:
            cmds = {
                2: 'select * from TABLE_WIFI_DEVICE;',
                3: 'select * from TABLE_ZIGBEE_DEVICE;'
            }

            device_category_ids = {
                2: 1,
                3: 5
            }
            access_net = {
                2: self.wifi.wifi_access_net,
                3: self.robot.led_access_net
            }
            result = self.get_router_db_info([cmds[room_id]])
            common_para_dict = {
                "family_id": self.common_para_dict["family_id"],
                "user_id": self.common_para_dict["user_id"],
                "router_id": self.common_para_dict["router_id"],
                "room_id": room_id
            }

            if result and 'device_uuid' in result[1]:
                pass
            else:
                # add device
                # build msg
                msg = API_device_management.build_msg_add_device(common_para_dict, device_category_id=device_category_ids[room_id])

                # send msg to router
                if self.socket_send_to_router(json.dumps(msg) + '\n'):
                    access_net[room_id]()
                    def add_success():
                        ret = self.socket_recv_from_router(timeout=1)
                        if self.get_package_by_keyword(ret, ['dm_add_device', 'success'], except_keyword_list=['mdp_msg']):
                            return 1
                        else:
                            return 0
                    if self.mysleep(65, feedback=add_success):
                        self.LOG.info('Add device already success!')
                else:
                    return self.case_fail("Send msg to router failed!")

        # build msg
        msg = API_device_management.build_msg_get_device_list_by_family(common_para_dict, device_category_id=1)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_get_devices_by_family', 'success'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
            	"method": "dm_get_devices_by_family",
            	"req_id": "no_need",
            	"timestamp": "no_need",
            	"msg": "success",
            	"code": 0,
            	"result": {
                    "user_id": common_para_dict['user_id'],
            		"list": [{
            			"device_id": "no_need",
            			"device_uuid": "no_need",
            			"family_id": common_para_dict['family_id'],
            			"room_id": "no_need",
            			"device_category_id": 1,
            			u"device_name": u"柜式空调",
            			"default_device_name": "no_need",
            			"attribute":{
                            "connectivity": "online"
                        },
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
            return self.case_fail("msg check failed!")
        return self.case_pass()


if __name__ == '__main__':
    Test().test()
