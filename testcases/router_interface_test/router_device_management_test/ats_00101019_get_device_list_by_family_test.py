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
        }
        result = self.get_router_db_info(['select * from TABLE_WIFI_DEVICE;'])
        if result and 'device_uuid' in result[1]:
            pass
        else:
            # add WIFI device
            if self.add_wifi_device(device_category_id=1, room_id=1):
                pass
            else:
                return self.case_fail()

        result = self.get_router_db_info(['select * from TABLE_ZIGBEE_DEVICE;'])
        if result and 'device_uuid' in result[1]:
            pass
        else:
            # add zigbee device
            if self.add_wifi_device(device_category_id=5, room_id=1):
                pass
            else:
                return self.case_fail()

        # build msg
        msg = API_device_management.build_msg_get_device_type_by_family(common_para_dict)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_get_family_dev_type_list', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
            	"code": 0,
            	"msg": "success",
            	"req_id": "no_need",
            	#"msg_tag": "no_need",
            	"timestamp": "no_need",
            	"method": "dm_get_family_dev_type_list",
            	"result": {
            		"family_id": common_para_dict['family_id'],
                    "user_id": common_para_dict['user_id'],
            		"list": [1, 5, 11]
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
