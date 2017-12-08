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

from APIs.common_APIs import crc, protocol_data_printB
from connections.my_serial import MySerial

# 空调模拟器
class Air():
    def __init__(self, port=None, baudrate=9600, logger=None):
        self.port = port
        self.serial = MySerial(port, baudrate, logger)
        self.queue_in = Queue.Queue()
        self.queue_out = Queue.Queue()

        self.msg_statistics = defaultdict(int)
        self.state = 'close'
        self.logger = logger
        self.left_data = ''

        # 当前温度 1word
        self._TEMP = b'\x00\x1C'

        # 设定温度 1word
        self._STEMP = b'\x00\x00'

        # 设定湿度和当前湿度
        # 高字节，设定湿度Humidity：范围：30%-90%(1E-5A)
        # 低字节，当前湿度HUM：湿度值范围：1-100%(00-64)
        self._HUMSD = b'\x00\x00'

        # 空气质量加外环温1word
        # 空气质量(1 byte )+ 外环温(1 byte)
        self._HHON = b'\x00\x00'

        # 功率1word
        self._MMON = b'\x00\x00'

        # PM2.5 1word
        self._HHOFF = b'\x00\x00'

        # 预留
        self._MMOFF = b'\x00\x00'

        # 模式 1word 0000 ~ 0004
        self._MODE = B'\x00\x00'

        # 风速 1word 0000 ~ 0003
        self._WIND = b'\x00\x00'

        # 立体送风 1word
        # SOLIDH0:表示字SOLIDH的第0位，为“0”时，表示无“上下摆风”
        #                           为“1”时，表示有“上下摆风”
        # SOLIDH1:表示字SOLIDH的第1位，为“0”时，表示无“左右摆风”
        #                           为“1”时，表示有“左右摆风”
        self._SOLLDH = b'\x00\x00'

        # 字A：WORDA ( 1 word )
        self._WORDA = b'\x00\x00'

        # 字B：WORDB( 1 word )
        self._WORDB = b'\x00\x00'
        self.logger = logger

    # 存储空调设置温度
    def TEMP_set(self, word, ifprint=0):
        if self.bit_get(word, 15):
            if ifprint:
                temp1 = struct.unpack('BB', word)
                temp2 = temp1[0] * 256 + temp1[1] + 16 + 0.5
                self.logger.debug("设定温度".decode(
                    'utf-8').encode(sys.getfilesystemencoding()) + ': %0.1f' % (temp2))
            self.WORDA_set_bit(5)
        else:
            if ifprint:
                temp1 = struct.unpack('BB', word)
                temp2 = temp1[0] * 256 + temp1[1] + 16
                self.logger.debug("设定温度".decode(
                    'utf-8').encode(sys.getfilesystemencoding()) + ': %d' % (temp2))
            self.WORDA_clear_bit(5)
        self._STEMP = word
        self._TEMP = word

    # 存储空调送风设置，UD_data：上下送风标志， LR_data：左右送风标志
    def SOLLDH_set(self, UD_data=None, LR_data=None):
        if UD_data:
            if self.bit_get(UD_data, 0):
                self._SOLLDH = self.bit_set(self._SOLLDH, 0)
            else:
                self._SOLLDH = self.bit_set(self._SOLLDH, 0)

        if LR_data:
            if self.bit_get(LR_data, 0):
                self._SOLLDH = self.bit_set(self._SOLLDH, 1)
            else:
                self._SOLLDH = self.bit_set(self._SOLLDH, 1)

    # 存储空调风速设置
    def WIND_set(self, word, ifprint=0):
        if word in [b'\x00\x00', b'\x00\x01', b'\x00\x02', b'\x00\x03']:
            self._WIND = word
            if ifprint:
                if word == b'\x00\x00':
                    self.logger.debug("风速高风".decode(
                        'utf-8').encode(sys.getfilesystemencoding()))
                elif word == b'\x00\x01':
                    self.logger.debug("风速中风".decode(
                        'utf-8').encode(sys.getfilesystemencoding()))
                elif word == b'\x00\x02':
                    self.logger.debug("风速低风".decode(
                        'utf-8').encode(sys.getfilesystemencoding()))
                else:
                    self.logger.debug("风速自动".decode(
                        'utf-8').encode(sys.getfilesystemencoding()))
        else:
            self.logger.error("风速设置异常".decode(
                'utf-8').encode(sys.getfilesystemencoding()))

    # 存储空调模式设置
    def MODE_set(self, word, ifprint=0):
        if word in [b'\x00\x00', b'\x00\x01', b'\x00\x02', b'\x00\x03', b'\x00\x04']:
            self._MODE = word
            if ifprint:
                if word == b'\x00\x00':
                    self.logger.debug("自动模式".decode(
                        'utf-8').encode(sys.getfilesystemencoding()))
                elif word == b'\x00\x01':
                    self.logger.debug("制冷模式".decode(
                        'utf-8').encode(sys.getfilesystemencoding()))
                elif word == b'\x00\x02':
                    self.logger.debug("制热模式".decode(
                        'utf-8').encode(sys.getfilesystemencoding()))
                elif word == b'\x00\x03':
                    self.logger.debug("送风模式".decode(
                        'utf-8').encode(sys.getfilesystemencoding()))
                else:
                    self.logger.debug("除湿模式".decode(
                        'utf-8').encode(sys.getfilesystemencoding()))
        else:
            self.logger.error("模式设置异常".decode(
                'utf-8').encode(sys.getfilesystemencoding()))

    # 存储空调湿度设置
    def HUMSD_set(self, word, ifprint=0):
        self._HUMSD = word
        if ifprint:
            temp1 = struct.unpack('BB', word)
            temp2 = temp1[0] * 256 + temp1[1]
            self.logger.debug("除湿湿度".decode(
                'utf-8').encode(sys.getfilesystemencoding()) + ': %0.1f' % (temp2))

    # 设置WORDA的某位
    def WORDA_set_bit(self, bit):
        self._WORDA = self.bit_set(self._WORDA, bit)

    # 清除WORDA的某位
    def WORDA_clear_bit(self, bit):
        self._WORDA = self.bit_clear(self._WORDA, bit)

    # 设置WORDB的某位
    def WORDB_set_bit(self, bit):
        self._WORDB = self.bit_set(self._WORDB, bit)

    # 清除WORDB的某位
    def WORDB_clear_bit(self, bit):
        self._WORDB = self.bit_clear(self._WORDB, bit)

    def bit_set(self, word, bit):
        temp1 = struct.unpack('BB', word)
        temp2 = temp1[0] * 256 + temp1[1]
        temp2 = temp2 | (1 << bit)
        return struct.pack('BB', temp2 >> 8, temp2 % 256)

    def bit_get(self, word, bit):
        temp1 = struct.unpack('BB', word)
        temp2 = temp1[0] * 256 + temp1[1]
        temp2 = temp2 & (1 << bit)
        return temp2

    def bit_clear(self, word, bit):
        temp1 = struct.unpack('BB', word)
        temp2 = temp1[0] * 256 + temp1[1]
        temp2 = temp2 & ~(1 << bit)
        return struct.pack('BB', temp2 >> 8, temp2 % 256)

    # 生成空调返回给模块的消息
    def msg_build(self):
        data = (self._TEMP + self._HHON + self._MMON + self._HHOFF + self._MMOFF
                + self._MODE + self._WIND + self._SOLLDH + self._WORDA + self._WORDB + self._HUMSD + self._STEMP)
        # 固定两位 ff ff
        answer = b'\xFF\xFF'
        # 数据长度
        answer += struct.pack('B', len(data) + 10)
        # 固定格式
        answer += b'\x00\x00\x00\x00\x00\x01'
        # 固定字节02
        answer += b'\x02'
        # 控制字
        answer += '\x6D\x01'
        # 数据
        answer += data
        # CRC
        answer += crc(answer[2:])
        return answer

    def run_forever(self):
        while True:
            if self.serial.is_open():
                # self.queue_in.put(b'\xff\xff\x0a\x00\x00\x00\x00\x00\x00\x01\x4d\x01\x59')
                pass
            else:
                self.logger.debug(self.port + ' try to open...')
                if self.serial.open():
                    self.set_state('open')

                    debug = 0
                    if debug:
                        self.queue_in.put(
                            b'\xFF\xFF\x0c\x00\x00\x00\x00\x00\x01\x01\x4d\x24\x00\x01\x80')
                        self.queue_in.put(
                            b'\xff\xff\x0c\x00\x00\x00\x00\x00\x00\x01\x5d\x01\x00')
                        if self.port == 'COM7':
                            self.queue_in.put(
                                b'\x0c\x77\xff\xff\x0a\x00\x00\x00\x00\x00\x00\x01\x4d\x01\x59')
                        else:
                            self.queue_in.put(
                                b'\x0d\x78\xff\xff\x0a\x00\x00\x00\x00\x00\x00\x01\x4d\x01\x59')
                        self.queue_in.put(
                            b'\xff\xff\x0a\x00\x00\x00\x00\x00\x00\x01\x4d\x01\x59')
                        debug = 0

                else:
                    self.logger.warn(self.port + " can't open!")
                    time.sleep(30)
                    continue

            # receive data from module
            if self.serial.readable():
                datas = ''
                data = self.serial.readall()
                while data:
                    datas += data
                    data = self.serial.readall()

                if datas:
                    self.queue_in.put(datas)
                    self.logger.info(protocol_data_printB(
                        datas, title=self.port + " recv data:"))
                else:
                    #self.logger.debug('No data receive...')
                    pass
            else:
                self.set_state('close')
                self.logger.error('%s can not read, close it!' % (self.port))
                self.serial.close()

            # send data to module
            if self.queue_out.empty():
                #self.logger.debug('No data need send')
                pass
            else:
                while not self.queue_out.empty():
                    data = self.queue_out.get()
                    self.logger.yinfo(protocol_data_printB(
                        data, title=self.port + " send data:"))
                    self.serial.write(data)

            # time.sleep(1)

    def get_state(self):
        return self.state

    def set_state(self, new_state):
        self.state = new_state

    def update_msg_statistics(self, data):
        self.msg_statistics[data] += 1

    def get_msg_msg_statistics(self):
        return self.msg_statistics


# 调度类，处理来自各个串口的消息
class Protocol_proc():
    def __init__(self, coms_list, logger=None):
        self.coms_list = coms_list
        self.logger = logger

    # 处理来自各个串口的消息
    def run_forever(self):
        while True:
            for com in self.coms_list:
                if self.coms_list[com].queue_in.empty():
                    continue
                else:
                    ori_data = self.coms_list[com].left_data + \
                        self.coms_list[com].queue_in.get()
                    while len(ori_data) < 13:
                        ori_data += self.coms_list[com].queue_in.get()

                    data_list, left_data = self.protocol_data_wash(ori_data)
                    self.coms_list[com].left_data = left_data
                    if data_list:
                        for request_data in data_list:
                            response_data = self.protocol_handler(
                                request_data, self.coms_list[com])
                            if response_data:
                                self.coms_list[com].queue_out.put(
                                    response_data)
                                self.coms_list[com].update_msg_statistics(
                                    ''.join('%02x' % (i) for i in struct.unpack('BB', request_data[10:12])))
                            else:
                                pass
                                #self.logger.error(protocol_data_printB(ori_data, title='%s: invalid data:' % (self.coms_list[com].port, request_data)))
                    else:
                        #self.logger.error(protocol_data_printB(ori_data, title='%s: invalid data:' % (self.coms_list[com].port)))
                        continue
            # time.sleep(0.1)

    # 构建返回给wifi模块的消息
    def protocol_build(self, air):
        return air.msg_build()

    # 根据来自wifi模块的消息更新空调模拟器的数据记录
    def protocol_handler(self, data, air):
        # 查询
        if data[10:12] == b'\x4d\x01':
            self.logger.debug("查询命令".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            # too much such msg, ignore it
            return self.protocol_build(air)
            pass

        # 开机
        elif data[10:12] == b'\x4d\x02':
            self.logger.debug("开机".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_set_bit(0)
            return self.protocol_build(air)

        # 关机
        elif data[10:12] == b'\x4d\x03':
            self.logger.debug("关机".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_clear_bit(0)
            return self.protocol_build(air)

        # 电加热 无
        elif data[10:12] == b'\x4d\x04':
            self.logger.debug("电加热 无".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_clear_bit(1)
            return self.protocol_build(air)

        # 电加热 有
        elif data[10:12] == b'\x4d\x05':
            self.logger.debug("电加热 有".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_set_bit(1)
            return self.protocol_build(air)

        # 健康 无
        elif data[10:12] == b'\x4d\x08':
            self.logger.debug("健康 无".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_clear_bit(3)
            return self.protocol_build(air)

        # 健康 有
        elif data[10:12] == b'\x4d\x09':
            self.logger.debug("健康 有".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_set_bit(3)
            return self.protocol_build(air)

        # 设定温度
        elif data[10:12] == b'\x5d\x01':
            air.TEMP_set(data[12:14], ifprint=1)
            return self.protocol_build(air)

        # 电子锁 无
        elif data[10:12] == b'\x4d\x18':
            self.logger.debug("电子锁 无".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_clear_bit(15)
            return self.protocol_build(air)

        # 电子锁 有
        elif data[10:12] == b'\x4d\x19':
            self.logger.debug("电子锁 有".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_set_bit(15)
            return self.protocol_build(air)

        # 换新风 无
        elif data[10:12] == b'\x4d\x1e':
            self.logger.debug("换新风 无".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDB_clear_bit(0)
            return self.protocol_build(air)

        # 换新风 有
        elif data[10:12] == b'\x4d\x1f':
            self.logger.debug("换新风 有".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDB_set_bit(0)
            return self.protocol_build(air)

        # 加湿 无
        elif data[10:12] == b'\x4d\x1c':
            self.logger.debug("加湿 无".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_clear_bit(6)
            return self.protocol_build(air)

        # 加湿 有
        elif data[10:12] == b'\x4d\x1d':
            self.logger.debug("加湿 有".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_set_bit(6)
            return self.protocol_build(air)

        # 上下摆风
        elif data[10:12] == b'\x4d\x22':
            if data[12:14] == b'\x00\x01':
                self.logger.debug("上下摆风 有".decode(
                    'utf-8').encode(sys.getfilesystemencoding()))
            else:
                self.logger.debug("上下摆风 无".decode(
                    'utf-8').encode(sys.getfilesystemencoding()))
            air.SOLLDH_set(UD_data=data[12:14])
            return self.protocol_build(air)

        # 左右摆风
        elif data[10:12] == b'\x4d\x23':
            if data[12:14] == b'\x00\x01':
                self.logger.debug("左右摆风 有".decode(
                    'utf-8').encode(sys.getfilesystemencoding()))
            else:
                self.logger.debug("左右摆风 无".decode(
                    'utf-8').encode(sys.getfilesystemencoding()))
            air.SOLLDH_set(LR_data=data[12:14])
            return self.protocol_build(air)

        # 上下左右摆风
        elif data[10:12] == b'\x4d\x24':
            if data[12:14] == b'\x00\x01':
                self.logger.debug("全摆风 有".decode(
                    'utf-8').encode(sys.getfilesystemencoding()))
            else:
                self.logger.debug("全摆风 无".decode(
                    'utf-8').encode(sys.getfilesystemencoding()))
            air.SOLLDH_set(UD_data=data[12:14], LR_data=data[12:14])
            return self.protocol_build(air)

        # 自清洁 无
        # elif data[10:12] == b'\x4d\x1c':
        #    self.logger.debug("自清洁 无".decode('utf-8').encode(sys.getfilesystemencoding()))
        #    air.WORDA_clear_bit(6)
        #    return self.protocol_build(air)

        # 自清洁 有
        elif data[10:12] == b'\x4d\x26':
            self.logger.debug("自清洁 有".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_set_bit(2)
            return self.protocol_build(air)

        # 感人功能 无
        elif data[10:12] == b'\x4d\x28':
            self.logger.debug("感人功能 无".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_clear_bit(12)
            return self.protocol_build(air)

        # 感人功能 有
        elif data[10:12] == b'\x4d\x27':
            self.logger.debug("感人功能 有".decode(
                'utf-8').encode(sys.getfilesystemencoding()))
            air.WORDA_set_bit(12)
            return self.protocol_build(air)

        # 风速
        elif data[10:12] == b'\x5d\x07':
            air.WIND_set(data[12:14], ifprint=1)
            return self.protocol_build(air)

        # 模式
        elif data[10:12] == b'\x5d\x08':
            air.MODE_set(data[12:14], ifprint=1)
            return self.protocol_build(air)

        # 健康除湿湿度
        elif data[10:12] == b'\x4d\x0d':
            air.HUMSD_set(data[12:14], ifprint=1)
            return self.protocol_build(air)

        # 组控制命令
        # TODO， 模块暂时不支持

        # others
        else:
            self.logger.error(protocol_data_printB(
                data, title='%s: invalid data:'))
            return self.protocol_build(air)

    # 数据清洗， 清除掉可能混杂在串口中的未知数据
    def protocol_data_wash(self, msg):
        data_list = []
        left_data = ''

        while msg[0] != b'\xff' and len(msg) >= 13:
            self.logger.debug('give up dirty data: %02x' % ord(msg[0]))
            msg = msg[1:]

        if len(msg) < 13:
            left_data = msg
        else:
            if msg[0] == b'\xff' and msg[1] == b'\xff':
                length = struct.unpack('>B', msg[2])[0]
                # min length is 10
                if length >= 10 and length <= len(msg[3:]):
                    #data_list.append(struct.unpack('%ds' % (length), msg[3:])[0])
                    data_list.append(msg[0:3 + length])
                    msg = msg[3 + length:]
                    if msg:
                        data_list_tmp, left_data_tmp = self.protocol_data_wash(
                            msg)
                        data_list += data_list_tmp
                        left_data += left_data_tmp
                elif length >= 10:
                    left_data = msg
                else:
                    for s in msg[:3]:
                        self.logger.debug('give up dirty data: %02x' % ord(s))
                    left_data = msg[3:]

        return data_list, left_data


if __name__ == '__main__':
    p = Protocol_proc(None)
    msg = p.protocol_build()
    print(protocol_data_printB(msg, title='see see'))
