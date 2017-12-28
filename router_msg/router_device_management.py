# -*- coding: utf-8 -*-

"""
msg for devece management
"""
import json
import re
import sys
import time


class API_device_management():
    def __init__(self):
        pass

    @staticmethod
    def build_msg_get_device_list_by_room(common_para_dict, device_category_id=0, size=10, begin=0):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_get_devices_by_room",
                "req_id": 123,
                "timestamp": 123121211,
                "params": {
                    "family_id": common_para_dict["family_id"],
                    "room_id": common_para_dict["room_id"],
                    "device_category_id": device_category_id,
                    "user_id": common_para_dict["user_id"],
                    "page": {
                        "size": size,
                        "begin": begin
                    }
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_add_device(common_para_dict, device_category_id):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_add_device",
                "timestamp": 1490229730,
                "req_id": 123,
                "params": {
                    "device_category_id": device_category_id,
                    "family_id": common_para_dict["family_id"],
                    "room_id": common_para_dict["room_id"],
                    "user_id": common_para_dict["user_id"]
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_cancel_add_device(common_para_dict, device_category_id):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_add_device_abort",
                "req_id": 124,
                "timestamp": 123456789,
                "params": {
                    "device_category_id": device_category_id,
                    "family_id": common_para_dict["family_id"],
                    "room_id": common_para_dict["room_id"],
                    "user_id": common_para_dict["user_id"]
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_delete_device(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_del_device",
                "req_id": 123,
                "timestamp": 123456789,
                "params": {
                    "family_id": common_para_dict["family_id"],
                    "device_uuid": common_para_dict["device_uuid"],
                    "user_id": common_para_dict["user_id"]
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_device_info(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_get_device_info",
                "timestamp": 1490229730,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict["family_id"],
                    "router_id": common_para_dict["router_id"],
                    "device_id": common_para_dict["device_id"],
                    "device_uuid": common_para_dict["device_uuid"],
                    "user_id": common_para_dict["user_id"]
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_device_list_by_family(common_para_dict, device_category_id=0, size=10, begin=0):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_get_devices_by_family",
                "req_id": 123,
                "timestamp": 123121211,
                "params": {
                    "family_id": common_para_dict["family_id"],
                    "device_category_id": device_category_id,
                    "user_id": common_para_dict["user_id"],
                    "page": {
                        "size": size,
                        "begin": begin
                    }
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_modify_device_name(common_para_dict, device_name):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_update_device",
                "timestamp": 1490229730,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict["family_id"],
                    "device_uuid": common_para_dict["device_uuid"],
                    "room_id": common_para_dict["room_id"],
                    "name": device_name,
                    "user_id": common_para_dict["user_id"],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_transfer_device_to_another_room(common_para_dict, device_uuid_list, dst_room_id):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_move_devices",
                "timestamp": 1490229730,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict["family_id"],
                    "device_uuid": device_uuid_list,
                    "room_id": dst_room_id,
                    "user_id": common_para_dict["user_id"],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_device_type(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_get_dev_type_list",
                "timestamp": 1490229730,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict["family_id"],
                    "user_id": common_para_dict["user_id"],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_device_type_by_family(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_get_family_dev_type_list",
                "req_id": 123,
                "timestamp": 123121211,
                "params": {
                    "family_id": common_para_dict["family_id"],
                    "user_id": common_para_dict["user_id"],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_product_list(common_para_dict, brand, dev_type, number=10, status=None):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_get_dev_product_list",
                "timestamp": 1490229730,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict["family_id"],
                    "user_id": common_para_dict["user_id"],
                    "brand": brand,
                    "type": dev_type,
                    "time": 1511424694,
                    "number": number
                }
            }
        }
        if status:
            msg["content"]["params"]["status"] = status
        return msg

    @staticmethod
    def build_msg_get_attribute_list_by_type(common_para_dict, type_id):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_get_dev_key_property",
                "timestamp": 1490229730,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict["family_id"],
                    "user_id": common_para_dict["user_id"],
                    "type_id": type_id,
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_attribute_list_by_ID(common_para_dict, product_id):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_get_product_key_property",
                "timestamp": 1490229730,
                "req_id": 123,
                "params": {
                    "family_id": common_para_dict["family_id"],
                    "user_id": common_para_dict["user_id"],
                    "product_id": product_id,
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_login_router(phone, password):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "um_login_pwd",
                "timestamp": 12345667,
                "req_id": 123,
                "params": {
                    "phone": phone,
                    "pwd": password,
                    "os_type": "Android",
                    "app_version": "v0.5",
                    "os_version": "android4.3",
                    "hardware_version": "Huawei"
                }
            }
        }
        return msg
