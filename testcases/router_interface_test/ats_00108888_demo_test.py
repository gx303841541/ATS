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
        cmds = ['select * from table_user_list;',
                'select * from table_family_list;']
        result = self.router_db_info(cmds)
        self.LOG.debug(self.convert_to_dictstr(result[1]))
        common_para_dict = {
            "family_id": result[1]['id'],
            "user_id": result[1]['user_id'],
        }

        # build msg
        msg = API_device_management.build_msg_get_device_type(common_para_dict)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            self.LOG.debug(self.convert_to_dictstr(data))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            u"name": u"空调",
            u"order": 1,
        }
        if self.json_items_compare(template, data):
            pass
        else:
            return self.case_fail("msg check failed!")
        return self.case_pass()


if __name__ == '__main__':
    Test().test()
