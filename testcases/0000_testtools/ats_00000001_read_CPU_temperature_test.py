#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, re, time
sys.path.append(os.path.abspath('.'))
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods

@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):

        self.ssh.connect()
        count = raw_input("请输入循环读取次数，默认为1000次:".decode('utf-8').encode(sys.getfilesystemencoding()))
        if count and re.match(r'^\d$', count, re.S):
            self.LOG.debug('read times is: %s' % (count))
            count = int(count)
        else:
            self.LOG.debug('read times is: %s' % (count))
            count = 1000

        for i in range(count):
            self.LOG.info('max read times is: %s, now is %s' % (count, i + 1))
            wifi0 = self.ssh.send("cat /sys/class/net/wifi0/thermal/temp")
            #self.LOG.debug(wifi0)
            temperature0 = re.findall(r'^(\d+)\s*$', wifi0, re.M)
            if temperature0:
                self.LOG.debug("wifi0: %s" % temperature0[0])
                if int(temperature0[0]) < 80:
                    pass
                else:
                    self.LOG.error("wifi0 temperature too high: [%s]" % temperature0[0])
            else:
                self.LOG.error("wifi0 read fail![%s]" % wifi0)
                return 1


            wifi1 = self.ssh.send("cat /sys/class/net/wifi1/thermal/temp")
            #self.LOG.debug(wifi1)
            temperature1 = re.findall(r'^(\d+)\s*$', wifi1, re.M)
            if temperature1:
                self.LOG.debug("wifi1: %s" % temperature1[0])
                if int(temperature1[0]) < 80:
                    pass
                else:
                    self.LOG.error("wifi1 temperature too high: [%s]" % temperature1[0])
            else:
                self.LOG.error("wifi1 read fail![%s]" % wifi1)
                return 1
            
            if i + 1 == count:
                continue
            else:
                time.sleep(120)
        return 0
