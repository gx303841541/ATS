#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, logging, datetime, re, sys, time, struct
from abc import ABCMeta, abstractmethod
import binascii
import crcmod.predefined

class Air():
    def __init__(self, ):
        #当前温度 1word
        self._TEMP = b'\x00\x1C'

        #设定温度 1word
        self._STEMP = b'\x00\x00'

        #设定湿度和当前湿度
        #高字节，设定湿度Humidity：范围：30%-90%(1E-5A)
        #低字节，当前湿度HUM：湿度值范围：1-100%(00-64)
        self._HUMSD = b'\x00\x00'

        #空气质量加外环温1word
        #空气质量(1 byte )+ 外环温(1 byte)
        self._HHON = b'\x00\x00'

        #功率1word
        self._MMON = b'\x00\x00'

        #PM2.5 1word
        self._HHOFF = b'\x00\x00'

        #预留
        self._MMOFF = b'\x00\x00'

        #模式 1word 0000 ~ 0004
        self._MODE = B'\x00\x00'

        #风速 1word 0000 ~ 0003
        self._WIND = b'\x00\x00'

        #立体送风 1word
        #SOLIDH0:表示字SOLIDH的第0位，为“0”时，表示无“上下摆风”
        #                           为“1”时，表示有“上下摆风”
        #SOLIDH1:表示字SOLIDH的第1位，为“0”时，表示无“左右摆风”
        #                           为“1”时，表示有“左右摆风”
        self._SOLLDH = b'\x00\x00'

        #字A：WORDA ( 1 word )
        self._WORDA = b'\x00\x00'

        #字B：WORDB( 1 word ) 
        self._WORDB = b'\x00\x00'

    def TEMP_set(self, word):
        if self.bit_get(word, 15):
            self.WORDA_set_bit(5)
        else:
            self.WORDA_clear_bit(5)
        self._STEMP = word


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

    def WIND_set(self, word):
        if word in [b'\x00\x00', b'\x00\x01', b'\x00\x02', b'\x00\x03']:
            self._WIND = word
        else:
            pass

    def MODE_set(self, word):
        if word in [b'\x00\x00', b'\x00\x01', b'\x00\x02', b'\x00\x03', b'\x00\x04']:
            self._MODE = word
        else:
            pass

    def HUMSD_set(self, word):
        self._HUMSD = word

    def WORDA_set_bit(self, bit):
        self._WORDA = self.bit_set(self._WORDA, bit)

    def WORDA_clear_bit(self, bit):
        self._WORDA = self.bit_clear(self._WORDA, bit)       

    def WORDB_set_bit(self, bit):
        self._WORDB = self.bit_set(self._WORDB, bit)

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

    def msg_build(self):
        data = (self._TEMP + self._HHON + self._MMON + self._HHOFF + self._MMOFF 
                + self._MODE + self._WIND + self._SOLLDH + self._WORDA + self._WORDB + self._HUMSD + self._STEMP)
        #固定两位 ff ff
        answer = b'\xFF\xFF'
        #数据长度
        answer += struct.pack('B', len(data) + 10)
        #固定格式
        answer += b'\x00\x00\x00\x00\x00\x01'
        #固定字节02
        answer += b'\x02'
        #控制字
        answer += '\x6D\x01'
        #数据
        answer += data
        #CRC
        answer += crc(answer[2:])
        return answer



class Protocol_proc():
    def __init__(self, coms_list, logger=None):
        self.coms_list = coms_list
        self.logger = logger
        self.air = Air()

    def run_forever(self):
        while True:
            for com in self.coms_list:
                if self.coms_list[com].queue_in.empty():
                    continue
                else:
                    ori_data = self.coms_list[com].queue_in.get()
                    while len(ori_data) < 13:
                        ori_data += self.coms_list[com].queue_in.get()

                    data_list = self.protocol_data_wash(ori_data)
                    if data_list:
                        for request_data in data_list:                
                            response_data = self.protocol_handler(request_data)
                            if response_data:
                                self.coms_list[com].queue_out.put(response_data)
                                self.coms_list[com].update_msg_statistics(''.join('%02x' % (i) for i in struct.unpack('BB', request_data[10:12])))
                            else:
                                pass
                                #self.logger.error(protocol_data_printB(ori_data, title='%s: invalid data:' % (self.coms_list[com].port, request_data)))
                    else:
                        self.logger.error(protocol_data_printB(ori_data, title='%s: invalid data:' % (self.coms_list[com].port)))
                        continue
            #time.sleep(0.1) 

    def protocol_build(self):
        return self.air.msg_build()

    def protocol_handler(self, data):
        #查询
        if data[10:12] == b'\x4d\x01':
            #too much such msg, ignore it
            return self.protocol_build()
            pass

        #开机
        elif data[10:12] == b'\x4d\x02':
            self.air.WORDA_set_bit(0)
            return self.protocol_build()

        #关机
        elif data[10:12] == b'\x4d\x03':
            self.air.WORDA_clear_bit(0)
            return self.protocol_build()

        #电加热 无
        elif data[10:12] == b'\x4d\x04':
            self.air.WORDA_clear_bit(1)
            return self.protocol_build()

        #电加热 有
        elif data[10:12] == b'\x4d\x05':
            self.air.WORDA_set_bit(1)
            return self.protocol_build()

        #健康 无
        elif data[10:12] == b'\x4d\x08':
            self.air.WORDA_clear_bit(3)
            return self.protocol_build()

        #健康 有
        elif data[10:12] == b'\x4d\x09':
            self.air.WORDA_set_bit(3)
            return self.protocol_build()

        #设定温度
        elif data[10:12] == b'\x5d\x01':
            self.air.TEMP_set(data[12:14])
            return self.protocol_build()

        #电子锁 无
        elif data[10:12] == b'\x4d\x18':
            self.air.WORDA_clear_bit(15)
            return self.protocol_build()

        #电子锁 有
        elif data[10:12] == b'\x4d\x19':
            self.air.WORDA_set_bit(15)
            return self.protocol_build()

        #换新风 无
        elif data[10:12] == b'\x4d\x1e':
            self.air.WORDB_clear_bit(0)
            return self.protocol_build()

        #换新风 有
        elif data[10:12] == b'\x4d\x1f':
            self.air.WORDB_set_bit(0)
            return self.protocol_build()

        #加湿 无
        elif data[10:12] == b'\x4d\x1c':
            self.air.WORDA_clear_bit(6)
            return self.protocol_build()

        #加湿 有
        elif data[10:12] == b'\x4d\x1d':
            self.air.WORDA_set_bit(6)
            return self.protocol_build()

        #上下摆风
        elif data[10:12] == b'\x4d\x22':
            self.air.SOLLDH_set(UD_data=data[12:14])
            return self.protocol_build()

        #左右摆风
        elif data[10:12] == b'\x4d\x23':
            self.air.SOLLDH_set(LR_data=data[12:14])
            return self.protocol_build()

        #上下摆风
        elif data[10:12] == b'\x4d\x24':
            self.air.SOLLDH_set(UD_data=data[12:14], LR_data=data[12:14])
            return self.protocol_build()

        #自清洁 无
        #elif data[10:12] == b'\x4d\x1c':
        #    self.air.WORDA_clear_bit(6)
        #    return self.protocol_build()

        #自清洁 有
        elif data[10:12] == b'\x4d\x26':
            self.air.WORDA_set_bit(2)
            return self.protocol_build()

        #感人功能 无
        elif data[10:12] == b'\x4d\x28':
            self.air.WORDA_clear_bit(12)
            return self.protocol_build()

        #感人功能 有
        elif data[10:12] == b'\x4d\x27':
            self.air.WORDA_set_bit(12)
            return self.protocol_build()

        #风速
        elif data[10:12] == b'\x5d\x07':
            self.air.WIND_set(data[12:14])
            return self.protocol_build()

        #模式
        elif data[10:12] == b'\x5d\x08':
            self.air.MODE_set(data[12:14])
            return self.protocol_build()

        #健康除湿湿度
        elif data[10:12] == b'\x4d\x0d':
            self.air.HUMSD_set(data[12:14])
            return self.protocol_build()

        #组控制命令
        #TODO， 模块暂时不支持

        #others
        else:
            self.logger.error(protocol_data_printB(data, title='%s: invalid data:'))
            return self.protocol_build()

    def protocol_data_wash(self, msg):
        data_list = []

        while msg[0] != b'\xff' and len(msg) >= 13:
            self.logger.debug('give up dirty data: %02x' % ord(msg[0]))
            msg = msg[1:]

        if len(msg) < 13:
            pass
        else:
            if msg[0] == b'\xff' and msg[1] == b'\xff':
                length = struct.unpack('>B', msg[2])[0]
                #min length is 10
                if length >= 10:
                    #data_list.append(struct.unpack('%ds' % (length), msg[3:])[0])
                    data_list.append(msg[0:3 + length])
                    msg = msg[3 + length:]
                    if msg:
                        data_list += self.protocol_data_wash(msg)

                else:
                    pass

        return data_list


def protocol_data_printB(data, title=''):
    datas = re.findall(r'([\x00-\xff])', data, re.M)
    ret = title + ' %s bytes:' % (len(datas)) + '\n\t\t'
    counter = 0
    for item in datas:
        ret += '{:02x}'.format(ord(item)) + ' '
        counter += 1
        if counter == 10:
            ret += ' ' + '\n\t\t'
            counter -= 10
            
    return ret


def crc(s):
    result = 0
    for i in range(len(s)):
        result += struct.unpack('B', s[i])[0]

    result %= 0xff
    return struct.pack('B', result)


if __name__ == '__main__':
    p = Protocol_proc(None)
    msg = p.protocol_build()
    print(protocol_data_printB(msg, title='see see'))