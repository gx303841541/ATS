#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, re
sys.path.append(os.path.abspath('.'))
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        self.ssh.connect()

        r = self.ssh.send('iwconfig')

        if re.match():
            self.LOG.debug("iwconfig check pass: " + r)
            return 0

        else:
            self.LOG.error("iwconfig check faied: " + r) 
            return 1
