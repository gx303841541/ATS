# -*- coding: utf-8 -*-

"""common methods
by Ann 2017-11-28
use:
	methods in class CommMethod can be used by all the testcases
"""
import json
import re
import sys
import time


class API_router_management():
    def __init__(self):
        pass

    @staticmethod
    def build_msg_app_login_info(common_para_dict, client_uuid="123"):
        '''
        :param common_para_dict:
        :param device_name: name of dev
        :return:
        '''

        method = 'um_login_pwd'

        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": method,
                "timestamp": 12345667,
                "req_id": common_para_dict['req_id'],
                "params": {
                    "phone": common_para_dict['phone'],
                    "pwd": common_para_dict['pwd'],
                    "os_type": "Android",
                    "app_version": "v0.5",
                    "os_version": "android4.3",
                    "hardware_version": "Huawei",
                }
            }
        }

        return msg

    @staticmethod
    def build_msg_bind_router(common_para_dict, client_uuid="123"):
        method = 'dm_bind_router'
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": method,
                "req_id": common_para_dict['req_id'],
                "timestamp": 1511230237309,
                "params": {
                    "family_id": common_para_dict['family_id'],
                    "family_name": common_para_dict['family_name'],
                    "token": common_para_dict['token'],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_unbind_router(common_para_dict, client_uuid="123"):
        method = "dm_unbind_router"
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": method,
                "req_id": common_para_dict['req_id'],
                "timestamp": 1511230237309,
                "params": {
                    "phone": common_para_dict['phone'],
                    "family_id": common_para_dict['family_id'],
                    "clear_data": 0,
                }
            }
        }
        return msg
