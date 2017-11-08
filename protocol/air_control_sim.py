#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""air sim protocol handle
by Kobe Gong. 2017-9-13
"""

import os
import logging
import datetime
import re
import sys
import time
import struct
import Queue
from abc import ABCMeta, abstractmethod
import binascii
import json

from collections import defaultdict

from APIs.common_APIs import crc, protocol_data_printB

class AirControl():
    def __init__(self, queue_in, queue_out, logger=None):
        self.msgst = defaultdict(lambda: {})

        self.queue_in = queue_in
        self.queue_out = queue_out
        self.left_data = ''
        self.min_length = 10
        self.name = 'AirControl'
        self.LOG = logger

    def protocol_handler(self, msg):
        self.LOG.yinfo('recv: ' + str(msg))
        json_msg=json.loads(msg)
        if ((not 'content' in json_msg)
            or (not 'req_id' in json_msg['content'])
            or (json_msg['content']['method'] == 'mdp_msg')):
            return 'No_need_send'

        rece_time = datetime.datetime.now()
        time_diff = (rece_time - self.msgst[json_msg['content']['req_id']]['send_time'])
        self.msgst[json_msg['content']['req_id']]['delaytime'] = time_diff.seconds * 1000.0 + (time_diff.microseconds / 1000.0)


        if(self.msgst[json_msg['content']['req_id']]['delaytime'] >= 1000):
            self.LOG.error("msg intervavl for %s is too long: %s\n" % (json_msg['content']['req_id'], self.msgst[json_msg['content']['req_id']]['delaytime']))
        else:
            self.LOG.warn('msg intervavl for %s is %f\n' % (json_msg['content']['req_id'], self.msgst[json_msg['content']['req_id']]['delaytime']))
            return 'No_need_send'

    def protocol_data_wash(self, data):
        data_list = []
        left_data = ''

        if data.endswith('\n'):
            data_list = data.strip().split('\n')
        elif re.search(r'\n', data, re.S):
            data_list = data.split('\n')
            left_data = data_list[-1]
            data_list = data_list[:-1]

        else:
            left_data = data

        if len(data_list) > 1 or left_data:
            self.LOG.warn('packet splicing')
        return data_list, left_data
