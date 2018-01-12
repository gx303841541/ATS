#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
by Kobe Gong 2018-1-10
use:
    interface test
"""

import ConfigParser
import datetime
import json
import logging
import os
import random
import re
import sys
import time

from basic.log_tool import MyLogger

info = {
    "family_id": "===self.common_para_dict['family_id']===",
    "user_id": "===self.common_para_dict['user_id']===",
    "family_name": "===self.common_para_dict['family_name']===",
    "phone": "===self.common_para_dict['phone']===",
    "device_uuid": "===self.common_para_dict['device_uuid']===",
    "router_id": "===self.common_para_dict['router_id']===",
    "token": "===self.common_para_dict['token']===",
}


class DIY():

    suite1 = {
        'init': [],
        'case1': {
            'setup': [],
            'request': {
                "content": {
                    "params": {
                        "attribute": {
                            "switch": "on"
                        },
                        "device_uuid": "000c773c210100000000999999"
                    },
                    "method": "dm_set",
                    "req_id": 178237278,
                    "nodeid": "airconditioner.main.switch"
                },
                "encry": "false",
                "uuid": "111"
            },
            'waittime': 0,
            'expect_response': {"encry": "false", "method": "dm_set", },
            'db_check': {'table_name': {}},
            'teardown': [],
        },


        'case2': {
            'setup': [],
            'request': {
                "content": {
                    "params": {
                        "attribute": {
                            "switch": "on"
                        },
                        "device_uuid": "000c773c210100000000999999"
                    },
                    "method": "dm_set",
                    "req_id": 178237278,
                    "nodeid": "airconditioner.main.switch"
                },
                "encry": "false",
                "uuid": "111"
            },
            'waittime': 0,
            'expect_response': {"encry": "false", "method": "dm_set", },
            'db_check': {'table_name': {}},
            'teardown': [],
        },
    }

    suite2 = {
        'init': [],
        'case1': {
            'setup': [],
            'request': {
                "content": {
                    "params": {
                        "attribute": {
                            "switch": "off"
                        },
                        "device_uuid": "000c773c210100000000999999"
                    },
                    "method": "dm_set",
                    "req_id": info['family_id'],
                    "nodeid": "airconditioner.main.switch"
                },
                "encry": "False",
                "uuid": "111"
            },
            'waittime': 5,
            'expect_response': {
                "encry": "false",
                "method": "dm_set",
            },
            'db_check': {
                'TABLE_WIFI_DEVICE': [
                    '"switchStatus":"off"',
                    '"speed":"low"',
                ],
            },
            'teardown': ['LOG.warn("Good boy!")'],
        },


        'case2': {
            'setup': [],
            'request': {
                "content": {
                    "params": {
                        "attribute": {
                            "switch": "on"
                        },
                        "device_uuid": "000c773c210100000000999999"
                    },
                    "method": "dm_set",
                    "req_id": 178237278,
                    "nodeid": "airconditioner.main.switch"
                },
                "encry": "false",
                "uuid": "111"
            },
            'waittime': 5,
            'expect_response': {"encry": "false", "method": "dm_set", },
            'db_check': {},
            'teardown': [],
        },
    }
