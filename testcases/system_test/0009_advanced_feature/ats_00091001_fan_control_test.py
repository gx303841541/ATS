#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
通过串口控制风扇转速，肉眼观察是否正确
'''

import os, sys, re, time
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):

        if self.serial.open() == 0:
            speed = raw_input("请输入风扇速度：(1-99): ".decode('utf-8').encode(sys.getfilesystemencoding()))
            while speed.strip():
                self.serial.write("fan_ctl -s %s" % (int(speed) % 100))
                time.sleep(1)
                speed = raw_input("请输入风扇速度：(1-99): ".decode('utf-8').encode(sys.getfilesystemencoding()))

            self.serial.close()
            return 0
        else:
            self.LOG.error("serial connect fail, please check serial connection!")
            return 1
