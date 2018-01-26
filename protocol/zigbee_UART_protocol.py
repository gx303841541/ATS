#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""zigbee UART protocol
by Kobe Gong. 2018-1-26
"""

import binascii
import datetime
import logging
import os
import re
import struct
import sys
import threading
import time
from collections import defaultdict

import APIs.common_APIs as common_APIs
from APIs.common_APIs import (bit_clear, bit_get, bit_set, crc16,
                              protocol_data_printB)
from connections.my_serial import MySerial
from protocol.protocol_process import communication_base

try:
    import queue as Queue
except:
    import Queue

coding = sys.getfilesystemencoding()


class ZIGBEE(communication_base):
    status_lock = threading.Lock()

    def __init__(self, port, logger, time_delay=0):
        self.port = port
        self.LOG = logger
        super(ZIGBEE, self).__init__(queue_in=Queue.Queue(),
                                     queue_out=Queue.Queue(), logger=logger, left_data='', min_length=18)
        self.connection = MySerial(port, 9600, logger)
        self.devices = defaultdict(str)
        self.state = 'close'
        self.time_delay = time_delay
        self.heartbeat_interval = 3
        self.heartbeat_data = 'root'

        # status data:
        self.head = b'\x55\xaa'
        self.dst_addr = b''

    def add_device(self, factory, addr, logger):
        if addr in self.devices:
            self.LOG.error("addr: %s already exist!" % (addr))
            return False
        else:
            self.devices[addr] = factory(logger=logger)
            self.devices[addr].run_forever()
            return True

    def msg_build(self, datas):
        if len(datas) < 6:
            return 'No_need_send'
        tmp_msg = datas['control'] + datas['seq'] + self.dst_addr + \
            datas['addr'] + datas['cmd'] + datas['reserve'] + datas['data']

        rsp_msg = self.head
        rsp_msg += struct.pack('B', len(tmp_msg) + 2)
        rsp_msg += tmp_msg
        rsp_msg += crc16(rsp_msg)
        return rsp_msg

    def protocol_data_washer(self, data):
        msg_list = []
        left_data = ''

        while data[0:2] != b'\x55\xaa' and len(data) >= self.min_length:
            self.LOG.warn('give up dirty data: %02x' % ord(data[0]))
            data = data[1:]

        if len(data) < self.min_length:
            left_data = data
        else:
            length = struct.unpack('>B', data[2])[0]
            if length <= len(data[2:]):
                msg_list.append(data[0:2 + length])
                data = data[2 + length:]
                if data:
                    msg_list_tmp, left_data_tmp = self.protocol_data_washer(
                        data)
                    msg_list += msg_list_tmp
                    left_data += left_data_tmp
            elif length > 0:
                left_data = data
            else:
                for s in data[:3]:
                    self.LOG.warn('give up dirty data: %02x' % ord(s))
                left_data = data[3:]

        return msg_list, left_data

    def protocol_handler(self, msg):
        if msg[0:2] == b'\x55\xaa':
            length = struct.unpack('B', msg[2:2 + 1])[0]
            control = msg[3:3 + 1]
            seq = msg[4:4 + 1]
            dst_addr = msg[5:5 + 3]
            src_addr = msg[8:8 + 3]
            self.dst_addr = src_addr
            cmd = msg[11:11 + 5]
            self.LOG.warn(protocol_data_printB(
                data=msg[11:11 + 5], title='cmd:'))
            if dst_addr in self.devices:
                pass
            else:
                self.LOG.warn(protocol_data_printB(
                    data=dst_addr, title='Unknow addr: '))
                return 'No_need_send'

            have_reserve_flag = bit_get(control, 3)
            if have_reserve_flag:
                reserve_length = struct.unpack('B', msg[16:16 + 1])[0]
                data_length = length - reserve_length - 15
                reserve_data = msg[16:16 + reserve_length]
            else:
                reserve_length = 0
                data_length = length - 15
                reserve_data = b''
            data = msg[-2 - data_length:-2]
            self.LOG.warn(protocol_data_printB(
                data=msg[16 + reserve_length:16 + reserve_length + data_length], title='data:'))

            datas = {
                'control': control,
                'seq': seq,
                'addr': dst_addr,
                'cmd': cmd,
                'reserve': reserve_data,
                'data': data,
            }
            self.LOG.info("recv msg: " + self.convert_to_dictstr(datas))
            time.sleep(self.time_delay / 1000.0)
            rsp_datas = self.devices[dst_addr].protocol_handler(datas)
            rsp_msg = ''
            if rsp_datas:
                if isinstance(rsp_datas, list):
                    for rsp in rsp_datas:
                        rsp_msg += self.msg_build(rsp)
                else:
                    rsp_msg = self.msg_build(rsp_datas)
            else:
                rsp_msg = 'No_need_send'
            return rsp_msg

        else:
            self.LOG.warn('Unknow msg: %s!' % (msg))
            return "No_need_send"

    @common_APIs.need_add_lock(status_lock)
    def connection_setup(self):
        self.LOG.warn('Try to open port %s...' % (self.port))
        if self.connection.is_open():
            self.LOG.info('Connection already setup!')
            return True
        elif self.connection.open():
            self.set_connection_state('online')
            self.LOG.info('Setup connection success!')
            return True
        else:
            self.LOG.warn(self.port + " can't open!")
            self.LOG.error('Setup connection failed!')
            return False

    def connection_close(self):
        if self.connection.close():
            self.connection = None
            self.set_connection_state('offline')
        else:
            self.LOG.error('Close connection failed!')

    def send_data(self, data):
        self.LOG.yinfo(protocol_data_printB(
            data, title=self.port + " send data:"))
        return self.connection.write(data)

    def recv_data(self):
        datas = self.connection.readall()
        if datas:
            self.LOG.info(protocol_data_printB(
                datas, title=self.port + " recv data:"))
        return datas


if __name__ == '__main__':
    print(protocol_data_printB(msg, title='see see'))
