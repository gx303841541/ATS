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
        common_para_dict = {
            "family_id": self.common_para_dict["family_id"],
            "user_id": self.common_para_dict["user_id"],
            "room_id": 1
        }

        # delete all zigbee device
        if self.delete_all_zigbee_devices():
            pass
        else:
            return self.case_fail()

        # build msg
        add_device_msg = API_device_management.build_msg_add_device(common_para_dict, device_category_id=5)
        cancel_add_device_msg = API_device_management.build_msg_cancel_add_device(common_para_dict, device_category_id=5)

        # send msg to router
        if self.socket_send_to_router(json.dumps(add_device_msg) + '\n') and self.socket_send_to_router(json.dumps(cancel_add_device_msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_add_device_abort', 'result'], except_keyword_list=['mdp_msg'])
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
            	"msg_tag": "no_need",
            	"timestamp": "no_need",
            	"method": "dm_add_device_abort",
            	"result": {
            		"user_id": common_para_dict['user_id'],
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
