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

from collections import defaultdict

from APIs.common_APIs import protocol_data_printB


# 消息分发类
class PProcess():
    def __init__(self, conn_dict, logger=None):
        self.conn_dict = conn_dict
        self.LOG = logger

    # 处理来自各实体的消息
    def run_forever(self):
        while True:
            for gay in self.conn_dict:
                if self.conn_dict[gay].queue_in.empty():
                    continue
                else:
                    ori_data = self.conn_dict[gay].left_data + \
                        self.conn_dict[gay].queue_in.get()
                    while len(ori_data) < self.conn_dict[gay].min_length:
                        ori_data += self.conn_dict[gay].queue_in.get()

                    data_list, self.conn_dict[gay].left_data = self.protocol_data_wash(self.conn_dict[gay], ori_data)
                    if data_list:
                        for request_data in data_list:
                            response_data = self.protocol_handler(self.conn_dict[gay], request_data)
                            if response_data == 'No_need_send':
                                pass
                            elif response_data:
                                self.conn_dict[gay].queue_out.put(response_data)
                            else:
                                self.LOG.error(protocol_data_printB(request_data, title='%s: got invalid data:' % (self.conn_dict[gay].name)))
                    else:
                        continue
            # time.sleep(0.1)

    # 处理来包
    def protocol_handler(self, gay, data):
        return gay.protocol_handler(data)

    # 数据清洗
    def protocol_data_wash(self, gay, msg):
        return gay.protocol_data_wash(msg)


if __name__ == '__main__':
    p = PProcess(None)
