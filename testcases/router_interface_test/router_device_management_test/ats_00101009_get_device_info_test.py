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
        cmds = ['select * from TABLE_ZIGBEE_DEVICE;']
        result = self.get_router_db_info(cmds)
        self.LOG.debug(self.convert_to_dictstr(result[1]))

        common_para_dict = {
            "family_id": self.common_para_dict["family_id"],
            "user_id": self.common_para_dict["user_id"],
            "router_id": self.common_para_dict["router_id"],
            "room_id": 1
        }

        if result[1].get('device_uuid', None):
            device_id, device_uuid = int(result[1]['id']), result[1]['device_uuid']
        else:
            # build msg and send msg to router
            msg = API_device_management.build_msg_add_device(common_para_dict, device_category_id=5)
            if self.socket_send_to_router(json.dumps(msg) + '\n'):
                self.robot.led_access_net()
                self.mysleep(20)
            else:
                return self.case_fail("Send msg to router failed!")

            cmds = ['select * from TABLE_ZIGBEE_DEVICE;']
            result = self.router_db_info(cmds)
            self.LOG.debug(self.convert_to_dictstr(result[1]))
            if result[1].get('device_uuid', None):
                device_id, device_uuid = int(result[1]['id']), result[1]['device_uuid']
            else:
                return self.case_fail("device add failed!")

        # build msg
        msg = API_device_management.build_msg_get_device_info(common_para_dict, device_id=device_id, device_uuid=device_uuid)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_get_device_info', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
            	"method": "dm_get_device_info",
            	"timestamp": "no_need",
            	"req_id": "no_need",
            	"msg_tag": "no_need",
            	"code": 0,
            	"msg": "success",
            	"result": {
            		"device_id": device_id,
            		"device_uuid": device_uuid,
            		"family_id": common_para_dict['family_id'],
                    "user_id": common_para_dict['user_id'],
            		"room_id": common_para_dict['room_id'],
            		"device_category_id": 5,
            		"created_at": "no_need",
            		"updated_at": "no_need",
            		u"device_name": u"佛照射灯",
            		"default_device_name": "no_need",
            		"attribute":{
                        "b": "no_need",
                        "connectivity": "online",
                        "g": "no_need",
                        "hue": "no_need",
                        "level": "no_need",
                        "mode": "on",
                        "r": "no_need",
                        "saturation": "no_need",
                        "temperature": "no_need"
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
