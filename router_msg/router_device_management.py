# -*- coding: utf-8 -*-

"""common methods
by Kobe Gong 2017-11-27
use:
    methods in class CommMethod can be used by all the testcases
"""
import re
import sys
import json
import time


class API_device_management():
    def __init__(self):
        pass

    @staticmethod
    def build_msg_get_device_list_by_room(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {

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
    def build_msg_get_device_info(common_para_dict, device_id, device_uuid):
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
            		"device_id": device_id,
                    "device_uuid": device_uuid,
            		"user_id": common_para_dict["user_id"]
            	}
            }
        }
        return msg

    @staticmethod
    def build_msg_get_device_list_by_type(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {


            }
        }
        return msg

    @staticmethod
    def build_msg_get_device_list_by_family(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {


            }
        }
        return msg

    @staticmethod
    def build_msg_modify_device_name(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {


            }
        }
        return msg

    @staticmethod
    def build_msg_transfer_device_to_another_room(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {


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


            }
        }
        return msg

    @staticmethod
    def build_msg_get_product_list(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {


            }
        }
        return msg
