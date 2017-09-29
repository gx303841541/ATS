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
        result = 0

        while (True):

            for num in range(1, 500 + 1):
                src = "/mnt/usb/b.txt"
                des="/test"
                self.ssh.send("cp "+ src + " " + des +"/file_bak_"+str(num)+".zip"+"\r")

            self.ssh.send("rm -f "+ des + "/*" + "\r")
