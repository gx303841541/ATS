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
        common_para_dict1 = {
            "family_id": self.common_para_dict["family_id"],
            "user_id": self.common_para_dict["user_id"],
            "room_id": 2
        }

        if result and 'device_uuid' in result[1] and int(result[1]['room_id']) == 2:
            common_para_dict1['device_uuid'] = result[1]['device_uuid']
            common_para_dict1['room_id'] = int(result[1]['room_id'])
        elif result and 'device_uuid' in result[1]:
            # change room for WIFI device
            # build msg
            common_para_dict1['device_uuid'] = result[1]['device_uuid']
            msg = API_device_management.build_msg_transfer_device_to_another_room(common_para_dict1, device_uuid_list=[common_para_dict1['device_uuid']], dst_room_id=2)

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
                    common_para_dict1['device_uuid'] = result[1]['device_uuid']
                    common_para_dict1['room_id'] = int(result[1]['room_id'])
                    device_name = result[1]['device_name']
                else:
                    return self.case_fail("Change room failed!")
            else:
                return self.case_fail("Send msg to router failed!")
        else:
            # add WIFI device
            common_para_dict['device_uuid'] = self.add_wifi_device(device_category_id=1, room_id=2)
            if common_para_dict['device_uuid']:
                result = self.get_router_db_info(['select * from TABLE_WIFI_DEVICE;'])
                common_para_dict['device_id'] = int(result[1]['id'])
                common_para_dict['room_id'] = int(result[1]['room_id'])
                device_name = result[1]['device_name']
            else:
                return self.case_fail()

        result = self.get_router_db_info(['select * from TABLE_ZIGBEE_DEVICE;'])
        common_para_dict2 = {
            "family_id": self.common_para_dict["family_id"],
            "user_id": self.common_para_dict["user_id"],
            "room_id": 3
        }

        if result and 'device_uuid' in result[1] and int(result[1]['room_id']) == 3:
            common_para_dict2['device_uuid'] = result[1]['device_uuid']
            common_para_dict2['room_id'] = int(result[1]['room_id'])
        elif result and 'device_uuid' in result[1]:
            # change room for zigbee device
            # build msg
            common_para_dict2['device_uuid'] = result[1]['device_uuid']
            msg = API_device_management.build_msg_transfer_device_to_another_room(common_para_dict2, device_uuid_list=[common_para_dict2['device_uuid']], dst_room_id=3)

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
                    result = self.get_router_db_info(['select * from TABLE_ZIGBEE_DEVICE;'])
                    common_para_dict2['device_uuid'] = result[1]['device_uuid']
                    common_para_dict2['room_id'] = int(result[1]['room_id'])
                    device_name = result[1]['device_name']
                else:
                    return self.case_fail("Change room failed!")
            else:
                return self.case_fail("Send msg to router failed!")
        else:
            # add zigbee device
            # build msg
            common_para_dict['device_uuid'] = self.add_zigbee_device(device_category_id=5, room_id=3)
            if common_para_dict['device_uuid']:
                result = self.get_router_db_info(['select * from TABLE_ZIGBEE_DEVICE;'])
                common_para_dict['device_id'] = int(result[1]['id'])
                common_para_dict['room_id'] = int(result[1]['room_id'])
                device_name = result[1]['device_name']
            else:
                return self.case_fail()

        # build msg
        msg = API_device_management.build_msg_transfer_device_to_another_room(common_para_dict1, device_uuid_list=[common_para_dict1['device_uuid'], common_para_dict2['device_uuid']], dst_room_id=1)

        # send msg to router
        if self.socket_send_to_router(json.dumps(msg) + '\n'):
            pass
        else:
            return self.case_fail("Send msg to router failed!")

        # recv msg from router
        data = self.socket_recv_from_router()
        if data:
            dst_package = self.get_package_by_keyword(data, ['dm_move_devices', 'result'], except_keyword_list=['mdp_msg'])
            for msg in dst_package:
                self.LOG.warn(self.convert_to_dictstr(msg))
            self.LOG.debug(self.convert_to_dictstr(dst_package[0]))
        else:
            return self.case_fail("timeout, server no response!")

        # msg check
        template = {
            "content": {
            	"method": "dm_move_devices",
            	"timestamp": "no_need",
            	"req_id": "no_need",
            	"msg_tag": "no_need",
            	"code": 0,
            	"msg": "success",
            	"result": {
            		"list": [{
                            "family_id": "no_need",
                            "attribute": "no_need",
                            "bussiness_user_id": "no_need",
                            "create_at": "no_need",
                            "device_category_id": "no_need",
                            "device_id": "no_need",
                            "device_name": "no_need",
                            "device_uuid": "no_need",
                            "room_id": 1,
                            "update_at": "no_need",
                            "user_id": "no_need",
                        },
                        {
                            "family_id": "no_need",
                            "attribute": "no_need",
                            "bussiness_user_id": "no_need",
                            "create_at": "no_need",
                            "device_category_id": "no_need",
                            "device_id": "no_need",
                            "device_name": "no_need",
                            "device_uuid": "no_need",
                            "room_id": 1,
                            "update_at": "no_need",
                            "user_id": "no_need",
                        },
                        {
                            "family_id": "no_need",
                            "attribute": "no_need",
                            "bussiness_user_id": "no_need",
                            "create_at": "no_need",
                            "device_category_id": "no_need",
                            "device_id": "no_need",
                            "device_name": "no_need",
                            "device_uuid": "no_need",
                            "room_id": 1,
                            "update_at": "no_need",
                            "user_id": "no_need",
                        }
                    ]
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
