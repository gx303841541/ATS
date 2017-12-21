# -*- coding: utf-8 -*-

"""
msg for device control
"""
import re
import sys
import json
import time


class API_device_control():
    def __init__(self):
        pass

    @staticmethod
    def build_msg_led_switch(common_para_dict, on_off):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_set",
                "req_id": 456,
                "timestamp": 123456789,
                "nodeid": "bulb.main.switch",
                "params":{
            		"user_id": common_para_dict["user_id"],
                    "device_uuid": common_para_dict["device_uuid"],
                    "attribute":{
                        "switch": on_off
                    }
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_led_light_control(common_para_dict, level):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
            	"method": "dm_set",
            	"req_id": 178237278,
            	"timestamp": 123456789,
            	"nodeid": "bulb.main.level",
            	"params": {
            		"user_id": common_para_dict["user_id"],
                    "device_uuid": common_para_dict["device_uuid"],
            		"attribute": {
            			"level": level,
                        "transition_time": 10,
                        "need_confirm": 'false'
            		}
            	}
            }
        }
        return msg

    @staticmethod
    def build_msg_led_colour_control(common_para_dict, rgb):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
            	"method": "dm_set",
            	"req_id": 178237278,
            	"timestamp": 123456789,
            	"nodeid": "bulb.main.rgb",
            	"params": {
            		"user_id": common_para_dict["user_id"],
                    "family_id": common_para_dict["family_id"],
                    "device_uuid": common_para_dict["device_uuid"],
            		"attribute": {
                        "r": rgb['r'],
                        "g": rgb['g'],
                        "b": rgb['b'],
                        "transition_time": 2,
                        "need_confirm": True
            		}
            	}
            }
        }
        return msg

    @staticmethod
    def build_msg_led_temperature_control(common_para_dict, temperature):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
            	"method": "dm_set",
            	"req_id": 178237278,
            	"timestamp": 123456789,
            	"nodeid": "bulb.main.temperature",
            	"params": {
            		"user_id": common_para_dict["user_id"],
                    "device_uuid": common_para_dict["device_uuid"],
            		"attribute": {
                        "temperature": temperature,
                        "transition_time": 10,
                        "need_confirm": 'false'
            		}
            	}
            }
        }
        return msg

    @staticmethod
    def build_msg_led_hue_control(common_para_dict, hue, saturation):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
            	"method": "dm_set",
            	"req_id": 178237278,
            	"timestamp": 123456789,
            	"nodeid": "bulb.main.hue",
            	"params": {
            		"user_id": common_para_dict["user_id"],
                    "device_uuid": common_para_dict["device_uuid"],
            		"attribute": {
                        "hue": hue,
                        "saturation": saturation,
                        "transition_time": 10,
                        "need_confirm": 'false'
            		}
            	}
            }
        }
        return msg

    @staticmethod
    def build_msg_subscribe():
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "subscribe",
                "req_id": 178237278,
                "timestamp": 123456789,
                "params": {
                    "mode": "on",
                    "subject": "dm_report_wan_speed",
                }
            }
        }
        return msg
