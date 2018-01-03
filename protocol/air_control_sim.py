#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""air sim protocol handle
by Kobe Gong. 2017-9-13
"""

import binascii
import datetime
import json
import logging
import os
import Queue
import re
import struct
import sys
import threading
import time
from abc import ABCMeta, abstractmethod
from collections import defaultdict

import APIs.common_APIs as common_APIs
import connections.my_socket as my_socket
from APIs.common_APIs import crc, protocol_data_printB
from protocol.protocol_process import communication_base


class AirControl(communication_base):
    state_lock = threading.Lock()

    def __init__(self, addr, logger):
        self.queue_in = Queue.Queue()
        self.queue_out = Queue.Queue()
        super(AirControl, self).__init__(self.queue_in, self.queue_out,
                                         logger=logger, left_data='', min_length=10)
        self.addr = addr
        self.name = 'AirControl'
        self.connection = my_socket.MyClient(
            addr, logger, debug=True, printB=False)
        self.state = 'close'

        # state data:
        self.msgst = defaultdict(lambda: {})

    def protocol_handler(self, msg):
        self.LOG.yinfo('recv: ' + str(msg))
        json_msg = json.loads(msg)
        if ((not 'content' in json_msg)
            or (not 'req_id' in json_msg['content'])
            or (json_msg['content']['method'] == 'um_login_pwd')
            or (json_msg['content']['method'] == 'mdp_msg')
                or not (json_msg['content']['req_id']) in self.msgst):
            return 'No_need_send'

        rece_time = datetime.datetime.now()
        time_diff = (
            rece_time - self.msgst[json_msg['content']['req_id']]['send_time'])
        self.msgst[json_msg['content']['req_id']]['delaytime'] = time_diff.seconds * \
            1000.0 + (time_diff.microseconds / 1000.0)

        if(self.msgst[json_msg['content']['req_id']]['delaytime'] >= 1000):
            self.LOG.error("msg intervavl for %s is too long: %s\n" % (
                json_msg['content']['req_id'], self.msgst[json_msg['content']['req_id']]['delaytime']))
            return 'No_need_send'
        else:
            self.LOG.warn('msg intervavl for %s is %f\n' % (
                json_msg['content']['req_id'], self.msgst[json_msg['content']['req_id']]['delaytime']))
            return 'No_need_send'

    def protocol_data_washer(self, data):
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
            pass
            # self.LOG.warn('packet splicing')
        return data_list, left_data

    @common_APIs.need_add_lock(state_lock)
    def connection_setup(self):
        self.LOG.warn('Try to connect %s...' % str(self.addr))
        if self.connection.get_connected():
            self.LOG.info('Connection already setup!')
            return True
        elif self.connection.connect():
            self.set_connection_state(True)
            self.LOG.info('Setup connection success!')
            return True
        else:
            self.LOG.warn("Can't connect %s!" % str(self.addr))
            self.LOG.error('Setup connection failed!')
            return False

    def connection_close(self):
        if self.connection.close():
            self.connection.set_connected(False)
            self.set_connection_state(False)
        else:
            self.LOG.error('Close connection failed!')

    def send_data(self, data):
        return self.connection.send_once(data)

    def recv_data(self):
        datas = self.connection.recv_once()
        return datas
