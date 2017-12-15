# -*- coding: utf-8 -*-

"""
msg for room homepage management
"""
import re
import sys
import json
import time


class API_room_homepage_management():
    def __init__(self):
        pass

    @staticmethod
    def build_msg_set_shortcut_sort(common_para_dict, shortcut_list):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
            	"method": "dm_sort_shortcut",
            	"timestamp": 1490229730,
            	"req_id": 123,
            	"params": {
            		"family_id": common_para_dict["family_id"],
            		"room_id": common_para_dict["room_id"],
            		"user_id": common_para_dict["user_id"],
            		"list": shortcut_list,
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_shortcut_list(common_para_dict, ):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_get_shortcut_list",
                "timestamp": 1498111457196,
                "req_id": 178237278,
                "params": {
            		"family_id": common_para_dict["family_id"],
            		"room_id": common_para_dict["room_id"],
            		"user_id": common_para_dict["user_id"],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_add_shortcut_sort(common_para_dict, device_category_id, name, order, mode='off', attribute=None):
        if not attribute:
            attribute = {
                "speed": "high"
            }

        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_add_shortcut",
                "req_id": 178237278,
                "timestamp": 1498111457196,
                "params": {
            		"family_id": common_para_dict["family_id"],
            		"room_id": common_para_dict["room_id"],
            		"user_id": common_para_dict["user_id"],
                    "name": name,
                    "device_uuid": common_para_dict["device_uuid"],
                    "device_category_id": device_category_id,
                    "order": order,
                    "mode": mode,
                    "attribute": attribute
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_del_shortcut_sort(common_para_dict, shortcut_id):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_del_shortcut",
                "req_id": 178237278,
                "timestamp": 1494916080598,
                "params": {
            		"family_id": common_para_dict["family_id"],
            		"room_id": common_para_dict["room_id"],
            		"user_id": common_para_dict["user_id"],
                    "shortcut_id": shortcut_id
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_get_shortcut_filter(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_get_shortcut_filter",
                "req_id": 178237278,
                "timestamp": 1498111457196,
                "params": {
            		"family_id": common_para_dict["family_id"],
            		"user_id": common_para_dict["user_id"],
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_update_main_switch_shortcut(common_para_dict, device_list):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
                "method": "dm_update_shortcut",
                "req_id": 178237278,
                "timestamp": 1498111457196,
                "params": {
            		"family_id": common_para_dict["family_id"],
                    "user_id": common_para_dict["user_id"],
            		"room_id": common_para_dict["room_id"],
                    "content": device_list
                }
            }
        }
        return msg

    @staticmethod
    def build_msg_main_switch_offon(common_para_dict, offon):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
            	"method": "dm_set_total_control",
            	"req_id": 178237278,
            	"timestamp": 1498111457196,
            	"params": {
            		"family_id": common_para_dict["family_id"],
            		"room_id": common_para_dict["room_id"],
            		"user_id": common_para_dict["user_id"],
            		"mode": "on",
            		"data": [{
            			"method": "dm_set_zigbee_bulb",
            			"req_id": 178237278,
            			"timestamp": 123456789,
            			"nodeid": "bulb.main.switch",
            			"params": {
            				"cmd": "setOnoff",
            				"device_uuid": common_para_dict["device_uuid"],
            				"attribute": {
            					"mode": offon
            				}
            			}
            		}]
        	    }
            }
        }
        return msg

    @staticmethod
    def build_msg_all_led_offon(common_para_dict, offon):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
            	"method": "dm_set_light_control",
            	"req_id": 178237278,
            	"timestamp": 1498111457196,
            	"params": {
            		"family_id": common_para_dict["family_id"],
            		"room_id": common_para_dict["room_id"],
            		"user_id": common_para_dict["user_id"],
            		"mode": "on",
            		"level": 75,
            		"data": [{
            			"method": "dm_set_zigbee_bulb",
            			"req_id": 178237278,
            			"timestamp": 123456789,
            			"nodeid": "bulb.main.switch",
            			"params": {
            				"cmd": "setOnoff",
            				"device_uuid": common_para_dict["device_uuid"],
            				"attribute": {
            					"mode": offon
            				}
            			}
            		}]
	            }
            }
        }
        return msg

    @staticmethod
    def build_msg_if_shortcut_is_set(common_para_dict):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
            	"method": "dm_get_shortcut_mode",
            	"req_id": 178237278,
            	"timestamp": 1498111457196,
            	"params": {
            		"family_id": common_para_dict["family_id"],
            		"room_id": common_para_dict["room_id"],
            	}
            }
        }
        return msg

    @staticmethod
    def build_msg_set_shortcut(common_para_dict, mode):
        msg = {
            "uuid": "111",
            "encry": "false",
            "content": {
            	"method": "dm_set_shortcut_mode",
            	"req_id": 178237278,
            	"timestamp": 1498111457196,
            	"params": {
            		"family_id": common_para_dict["family_id"],
            		"room_id": common_para_dict["room_id"],
            		"mode": mode
            	}
            }
        }
        return msg
