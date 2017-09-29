#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, re, time
sys.path.append(os.path.abspath('.'))
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):

        ack = self.http.setSSIDConfig_5G()
        print(repr(ack))
        return 0


        self.telnet.connect()

        for i in range(10):
            wifi0 = self.telnet.send("cat /sys/class/net/wifi0/thermal/temp")
            self.LOG.debug(wifi0)
            temperature0 = re.findall(r'^(\d+)\s*$', wifi0, re.M)
            if temperature0:
                self.LOG.debug("wifi0: %s" % temperature0[0])
                if int(temperature0[0]) < 80:
                    pass
                else:
                    self.LOG.error("wifi0 temperature too high: [%s]" % temperature0[0])
                    return 1
            else:
                self.LOG.error("wifi0 read fail![%s]" % wifi0) 
                return 1


            wifi1 = self.telnet.send("cat /sys/class/net/wifi1/thermal/temp")
            self.LOG.debug(wifi1)
            temperature1 = re.findall(r'^(\d+)\s*$', wifi1, re.M)
            if temperature1:
                self.LOG.debug("wifi1: %s" % temperature1[0])
                if int(temperature1[0]) < 80:
                    pass
                else:
                    self.LOG.error("wifi1 temperature too high: [%s]" % temperature1[0])
                    return 1
            else:
                self.LOG.error("wifi1 read fail![%s]" % wifi1) 
                return 1

            time.sleep(1)
        return 0