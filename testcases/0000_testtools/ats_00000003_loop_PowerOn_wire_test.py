#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, re, time
sys.path.append(os.path.abspath('.'))
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods

@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):
    def run(self):
        self.serial.open()
        result = 0

        for i in range(1000):
            self.LOG.info('waiting for power on times: %s' % (i + 1))
            while not self.waitforstart(timeout=5):
                pass
            time.sleep(70)

            ret = self.win_network.win_ping_check(localip=self.win_network.win_wifi_get_wire_service_ipv4(), remoteip=self.config_file.get("network", "host"))
            if ret == 'pass':
                self.LOG.debug('ping check passed on times: %s' % (i + 1))
            else:
                self.LOG.error('ping check failed on times: %s' % (i + 1))
                result = 1

        return result


    def waitforstart(self, timeout=60 * 10):
        promptString = "Starting kernel"
        self.serial.timeout_set(timeout)
        return self.serial.read_until(promptString)
