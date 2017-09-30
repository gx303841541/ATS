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
        self.logger = logger

    # 处理来自各实体的消息
    def run_forever(self):
        while True:
            for gay in self.conn_dict:
                if self.conn_dict[gay].queue_in.empty():
                    continue
                else:
                    ori_data = self.conn_dict[gay].left_data + \
                        self.conn_dict[gay].queue_in.get()
                    while len(ori_data) < self.conn_dict[gay].mix_length:
                        ori_data += self.conn_dict[gay].queue_in.get()

                    data_list, left_data = self.protocol_data_wash(ori_data, self.conn_dict[gay])
                    self.conn_dict[gay].left_data = left_data
                    if data_list:
                        for request_data in data_list:
                            response_data = self.protocol_handler(
                                request_data, self.conn_dict[gay])
                            if response_data:
                                self.conn_dict[gay].queue_out.put(response_data)
                            else:
                                self.logger.error(protocol_data_printB(ori_data, title='%s: got invalid data:' % (self.conn_dict[gay].name, request_data)))
                    else:
                        continue
            # time.sleep(0.1)

    # 构建回包
    def protocol_build(self, gay):
        return gay.msg_build()

    # 处理来包
    def protocol_handler(self, data, gay):
        return gay.protocol_handler(data)

    # 数据清洗
    def protocol_data_wash(self, msg, gay):
        return gay.protocol_data_wash(msg)


if __name__ == '__main__':
    p = PProcess(None)
    msg = p.protocol_build()
    print(protocol_data_printB(msg, title='see see'))
