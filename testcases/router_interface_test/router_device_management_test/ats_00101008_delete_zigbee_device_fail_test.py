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
        result2 = self.get_router_db_info(cmds)
        common_para_dict = {
            "family_id": 123,
            "user_id": self.common_para_dict["user_id"],
            "device_uuid": '123',
        }

        # build msg
        msg = API_device_management.build_msg_delete_device(common_para_dict)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router(timeout=5)
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_del_device', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
            	"method": "dm_del_device",
            	"req_id": 'no_need',
            	"timestamp": 'no_need',
            	"msg": "family id not exist",
            	"code": 'no_need',
            	"result": {
                    "user_id": self.common_para_dict["user_id"],
                    "device_uuid": '123',
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
