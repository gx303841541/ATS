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
            dst_package = self.get_package_by_keyword(data, ['dm_get_dev_type_list', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
                "code": 0,
                "method": "dm_get_dev_type_list",
                "msg": "success",
                "msg_tag": "",
                "req_id": 123,
                "result": {
                    "list": [
                        {
                            "created_at": "no_need",
                            "type_id": 1,
                            "name": u"空调",
                            "order": 1,
                            "updated_at": "no_need"
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 2,
                            "name": u"窗帘",
                            "order": 2,
                            "updated_at": "no_need"
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 3,
                            "name": u"电视",
                            "order": 3,
                            "updated_at": "no_need"
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 4,
                            "name": u"电饭煲",
                            "order": 4,
                            "updated_at": "no_need"
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 5,
                            "name": u"灯",
                            "order": 5,
                            "updated_at": "no_need"
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 6,
                            "name": u"电子秤",
                            "order": 6,
                            "updated_at": "no_need"
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 7,
                            "name": u"摄像头",
                            "order": 7,
                            "updated_at": "no_need"
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 8,
                            "name": u"智能开关",
                            "order": 8,
                            "updated_at": "no_need"
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 9,
                            "name": u"空气质量检测仪",
                            "order": 9,
                            "updated_at": "no_need"
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 10,
                            "name": u"温湿度计",
                            "order": 10,
                            "updated_at": "no_need"
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 11,
                            "name": u"路由器",
                            "order": 11,
                            "updated_at": "no_need"
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 12,
                            "name": u"门窗传感器",
                            "order": 12,
                            "updated_at": "no_need"
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 13,
                            "name": u"人体传感器",
                            "order": 13,
                            "updated_at": "no_need",
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 14,
                            "name": u"可视对讲",
                            "order": 14,
                            "updated_at": "no_need",
                        },
                        {
                            "created_at": "no_need",
                            "type_id": 15,
                            "name": u"智能音箱",
                            "order": 15,
                            "updated_at": "no_need",
                        }
                    ]
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
