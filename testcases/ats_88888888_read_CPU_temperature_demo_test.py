#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import time
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods
import connections.my_socket as my_socket


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        self.case_pass('let us go!')
        server = my_socket.MyServer(('', 8888), self.LOG, debug=True)
        server.run_forever()
        #time.sleep(1000)
        return self.case_pass()

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
                    return self.case_fail(
                        "wifi0 temperature too high: [%s]" % temperature0[0])
            else:
                return self.case_fail("wifi0 read fail![%s]" % wifi0)

            wifi1 = self.telnet.send("cat /sys/class/net/wifi1/thermal/temp")
            self.LOG.debug(wifi1)
            temperature1 = re.findall(r'^(\d+)\s*$', wifi1, re.M)
            if temperature1:
                self.LOG.debug("wifi1: %s" % temperature1[0])
                if int(temperature1[0]) < 80:
                    pass
                else:
                    return self.case_fail(
                        "wifi1 temperature too high: [%s]" % temperature1[0])
            else:
                return self.case_fail("wifi1 read fail![%s]" % wifi1)

            time.sleep(1)
        self.case_pass()
