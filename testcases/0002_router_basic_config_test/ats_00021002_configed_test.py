#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
模拟APP配置 路由器设置SSH密码, 检测配置状态是否为1
'''

import os, sys, re, time
sys.path.append(os.path.abspath('.'))
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):

        if self.serial.open() == 0:
            self.serial.write('echo -e "admin\nadmin" | passwd root')
        else:
            self.LOG.error("serial connect fail, please check serial connection!")
            return 1
        


        ack = self.http.isRouterSetupDone()
        if ack['result']['status'] == 1:
            self.LOG.debug(repr(ack))
            return 0 

        else:
            self.LOG.error('result->status not 1: ' + repr(ack))
            return 1