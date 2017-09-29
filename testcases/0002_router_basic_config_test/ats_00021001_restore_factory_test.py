#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
模拟APP配置 路由器硬件恢复出厂设置, 检测配置状态是否为0
'''

import os, sys, re, time
sys.path.append(os.path.abspath('.'))
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        '''
        if self.serial.open() == 0:
            self.serial.write('firstboot -y')
            time.sleep(2)
            self.serial.write('reboot')
            self.serial.close()
        else:
            self.LOG.error("serial connect fail, please check serial connection!")
            return 1
        '''         

        raw_input("请按住路由器恢复出厂设置按键5s, 然后按任意键继续".decode('utf-8').encode(sys.getfilesystemencoding()))
        time.sleep(10)

        ack = self.http.isRouterSetupDone()
        if ack['result']['status'] == 0:
            self.LOG.debug(repr(ack))
            return 0 

        else:
            self.LOG.error('result->status not 0: ' + repr(ack))
            return 1