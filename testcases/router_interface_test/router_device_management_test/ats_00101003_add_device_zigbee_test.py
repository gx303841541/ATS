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
        devices = self.get_router_db_info_dict(['select * from TABLE_ZIGBEE_DEVICE;'])
        common_para_dict = {
            "family_id": self.common_para_dict["family_id"],
            "user_id": self.common_para_dict["user_id"],
            "room_id": 1
        }

        # delete ZIGBEE device
        for item in devices:
            common_para_dict["device_uuid"] = item['device_uuid']

            # build msg
            msg = API_device_management.build_msg_delete_device(common_para_dict)

            # send msg to router
            if self.socket_send_to_router(json.dumps(msg) + '\n'):
                def del_success():
                    ret = self.socket_recv_from_router(timeout=1)
                    if self.get_package_by_keyword(ret, ['dm_del_device', 'success'], except_keyword_list=['mdp_msg']):
                        return 1
                    else:
                        return 0
                if self.mysleep(65, feedback=del_success):
                    self.LOG.info('Delete device already success!')
            else:
                return self.case_fail("Send msg to router failed!")

        # build msg
        msg = API_device_management.build_msg_add_device(common_para_dict, device_category_id=5)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            self.robot.led_access_net()
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router(timeout=20)
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_add_device', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
                "code": 0,
                "method": "dm_add_device",
                "msg": "success",
                "msg_tag": "no_need",
                "req_id": "no_need",
                "result": {
            	   "attribute": {
                        "b": "no_need",
                        "connectivity": "online",
                        "g": "no_need",
                        "hue": "no_need",
                        "level": "no_need",
                        "mode": "on",
                        "r": "no_need",
                        "saturation": "no_need",
                        "temperature": "no_need",
            	    },
                	"bussiness_user_id": 0,
                	"create_at":"no_need",
                	"device_category_id": 5,
                	"device_id": "no_need",
                	"device_name": "no_need",
                	"device_uuid": "no_need",
                	"family_id": common_para_dict['family_id'],
                    "room_id": common_para_dict['room_id'],
                	u"room_name": u"客厅",
                	"update_at":"no_need",
                	"user_id": common_para_dict['user_id'],
                },
                "timestamp": "no_need",
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
