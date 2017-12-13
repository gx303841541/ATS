#encoding=utf-8
"""
by Ann 2017-11-29
msg for air conditioner control
"""
import re
import sys
import json
import time

class API_air_control():
    def __init__(self):
        pass

    @staticmethod
    def build_msg_air_mode_set(common_para_dict, value, client_uuid="123"):
        '''
        :param common_para_dict:
        :param client_uuid: APP client uuid
        :return:
        '''

        method = 'dm_set'

        msg = {
            "uuid": client_uuid,
            "encry": "false",
            "content": {
                "method": method,
                "timestamp": 12345667,
                "req_id": common_para_dict['req_id'],
                "token": "",
                "nodeid": "airconditioner.main.mode",
                "params": {
                    "device_uuid": common_para_dict['wifi_uuid'],
                    "attribute": {
                        "mode": value,
                    }
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_air_switch(common_para_dict, switch):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_set",
                "req_id": 178237278,
                "nodeid": "airconditioner.main.switch",
                "params": {
                    "device_uuid": common_para_dict["device_uuid"],
                    "attribute": {
                        "switch": switch
                    }
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_wind_up_down(common_para_dict, switch):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_set",
                "req_id": 178237278,
                "nodeid": "airconditioner.main.wind_up_down",
                "params": {
                    "device_uuid": common_para_dict["device_uuid"],
                    "user_id": common_para_dict["user_id"],
                    "attribute": {
                        "wind_up_down": switch
                    }
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_wind_left_right(common_para_dict, switch):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_set",
                "req_id": 178237278,
                "nodeid": "airconditioner.main.wind_left_right",
                "params": {
                    "device_uuid": common_para_dict["device_uuid"],
                    "user_id": common_para_dict["user_id"],
                    "attribute": {
                        "wind_left_right": switch
                    }
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_all_attribute(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_get",
                "req_id": 178237278,
                "nodeid": "airconditioner.main.all_properties",
                "params": {
                    "device_uuid": common_para_dict["device_uuid"],
                }
            }
        }
        return msg
