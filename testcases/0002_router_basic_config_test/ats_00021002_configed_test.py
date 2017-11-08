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
            return self.case_fail("serial connect fail, please check serial connection!")

        ack = self.http.isRouterSetupDone()
        if ack['result']['status'] == 1:
            return self.case_pass(repr(ack))

        else:
            return self.case_fail('result->status not 1: ' + repr(ack))
