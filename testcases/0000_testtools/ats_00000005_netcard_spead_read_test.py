#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, re, time
sys.path.append(os.path.abspath('.'))
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods

@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):
    def run(self):
        netcard_Name = raw_input("请输入网卡名字，默认为wire:".decode('utf-8').encode(sys.getfilesystemencoding()))
        for counter in range(1, 1000 + 1):
            self.win_network.win_interface_disabled(netcard_Name)
            time.sleep(10)
            self.win_network.win_interface_enabled(netcard_Name)
            time.sleep(10)
            spead = self.win_network.win_interface_spead_get()
            self.LOG.info('\n' + spead)
            time.sleep(3)
