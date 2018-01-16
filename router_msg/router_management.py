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
    def build_msg_bind_router(common_para_dict, token, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'dm_bind_router',
                "req_id": 123,
                "timestamp": 1511230237309,
                "params": {
                    "family_id": common_para_dict['family_id'],
                    "family_name": common_para_dict['family_name'],
                    "token": token,
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_unbind_verify(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": "um_verify_user",
                "req_id": 123,
                "timestamp": 1511230237309,
                "params": {
                    "phone": common_para_dict['phone'],
                    "password": common_para_dict['pwd'],
                    "family_id": common_para_dict['family_id'],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_unbind_router(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": "dm_unbind_router",
                "req_id": 123,
                "timestamp": 1511230237309,
                "params": {
                    "phone": common_para_dict['phone'],
                    "family_id": common_para_dict['family_id'],
                    "clear_data": 0,
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_password_login(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'um_login_pwd',
                "timestamp": 12345667,
                "req_id": 123,
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
    def build_msg_logout_router(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'acc_logout',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_sync_pwd(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'um_sync_pwd',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "token": common_para_dict['token'],
                    "os_type": "Android"
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_token_login(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'um_auth',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "user_id": common_para_dict['user_id'],
                    "token": common_para_dict['token'],
                    "os_type": "Android",
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_verify_router(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'um_auth',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "user_id": common_para_dict['user_id'],
                    "token": common_para_dict['token'],
                    "os_type": "Android",
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_uuid_check(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'dm_verify_router',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "uuid": common_para_dict['device_uuid'],
                    "code": common_para_dict['code'],
                    "os_type": "Android",
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_add_mem_cloud_syn(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'um_auth',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict['family_id'],
                    "token": common_para_dict['token'],
                    "os_type": "Android",
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_remove_mem_cloud_syn(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'fm_remove_member',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict['family_id'],
                    "target_user_id": common_para_dict['target_user_id'],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_user_profile(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'um_get_user_profile',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "user_id": common_para_dict['user_id'],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_family_info(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'fm_get_family_info',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict['family_id'],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_member_list(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'fm_get_member_list',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict['family_id'],
                    "user_id": common_para_dict['user_id'],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_member_rights(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'fm_get_member_rights',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict['family_id'],
                    "user_id": common_para_dict['user_id'],
                    "target_user_id": common_para_dict['target_user_id'],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_member_rights_list(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'fm_get_member_rights_list',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict['family_id'],
                    "user_id": common_para_dict['user_id'],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_cloud_info(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'fm_get_cloud_info',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict['family_id'],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_set_cloud_info(common_para_dict, client_uuid="123"):
        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": 'fm_set_cloud_info',
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict['family_id'],
                    "cloud_server": common_para_dict['cloud_server'],
                    "lb_server": common_para_dict['lb_server'],
                }
            }
        }
        return msg
