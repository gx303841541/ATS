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
        result = self.get_router_db_info(['select * from TABLE_WIFI_DEVICE;'])
        common_para_dict = {
            "family_id": self.common_para_dict["family_id"],
            "user_id": self.common_para_dict["user_id"],
            "room_id": 1
        }

        if result and 'device_uuid' in result[1] and int(result[1]['room_id']) == 1:
            common_para_dict['device_uuid'] = result[1]['device_uuid']
            common_para_dict['room_id'] = int(result[1]['room_id'])
            device_name = result[1]['device_name']
        elif result and 'device_uuid' in result[1]:
            # change room for WIFI device
            # build msg
            common_para_dict['device_uuid'] = result[1]['device_uuid']
            device_name = result[1]['device_name']
            msg = API_device_management.build_msg_transfer_device_to_another_room(common_para_dict, device_uuid_list=[common_para_dict['device_uuid']], dst_room_id=1)

            # send msg to router
            if self.socket_send_to_router(json.dumps(msg) + '\n'):
                def wait_success():
                    ret = self.socket_recv_from_router(timeout=1)
                    if self.get_package_by_keyword(ret, ['dm_move_devices', 'success'], except_keyword_list=['mdp_msg']):
                        return 1
                    else:
                        return 0
                if self.mysleep(65, feedback=wait_success):
                    self.LOG.info('Change room success!')
                    result = self.get_router_db_info(['select * from TABLE_WIFI_DEVICE;'])
                    common_para_dict['device_uuid'] = result[1]['device_uuid']
                    common_para_dict['room_id'] = int(result[1]['room_id'])
                    device_name = result[1]['device_name']
                else:
                    return self.case_fail("Change room failed!")
            else:
                return self.case_fail("Send msg to router failed!")
        else:
            # add WIFI device
            # build msg
            msg = API_device_management.build_msg_add_device(common_para_dict, device_category_id=1)

            # send msg to router
            if self.socket_send_to_router(json.dumps(msg) + '\n'):
                self.wifi.wifi_access_net()
                def add_success():
                    ret = self.socket_recv_from_router(timeout=1)
                    if self.get_package_by_keyword(ret, ['dm_add_device', 'success'], except_keyword_list=['mdp_msg']):
                        return 1
                    else:
                        return 0
                if self.mysleep(65, feedback=add_success):
                    self.LOG.info('Add device already success!')
                    result = self.get_router_db_info(['select * from TABLE_WIFI_DEVICE;'])
                    common_para_dict['device_uuid'] = result[1]['device_uuid']
                    common_para_dict['room_id'] = int(result[1]['room_id'])
                    device_name = result[1]['device_name']
            else:
                return self.case_fail("Send msg to router failed!")

        # build msg
        new_name = str('路由器')
        msg = API_device_management.build_msg_modify_device_name(common_para_dict, device_name=new_name)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_update_device', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
            	"method": "dm_update_device",
            	"req_id": "no_need",
            	"timestamp": "no_need",
            	"msg": u"设备名称已存在，请重新修改",
            	"code": "no_need",
            	"result": {
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
