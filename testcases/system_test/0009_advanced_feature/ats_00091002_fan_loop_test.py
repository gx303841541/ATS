#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
通过串口循环控制风扇转速，肉眼观察是否正确
'''

import os, sys, re, time
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):

        if self.serial.open() == 0:
            speed = 0
            interval = 100
            #interval = raw_input("请输入风速变化间隔（单位ms）: ".decode('utf-8').encode(sys.getfilesystemencoding()))
            try:
                for i in range(int(5 * 60 / (int(interval) / 1000.0) + 1)):
                    if speed > 100:
                        speed = 0
                    self.LOG.info("Set fan speed: %s" % (speed))
                    self.serial.write("fan_ctl -s %s" % (int(speed) % 100))
                    time.sleep(int(interval) / 1000.0)
                    speed += 1
                return 0
            except:
                self.serial.close()
                return 0
        else:
            self.LOG.error("serial connect fail, please check serial connection!")
            return 1
