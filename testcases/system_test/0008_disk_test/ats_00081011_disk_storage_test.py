#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import os
import sys
import re

from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        self.ssh.connect()
        result = self.ssh.send('dd if=/dev/zero of=/root/1G.file bs=1024 count=1000000')
        self.LOG.info('max write speed:\n' + result)
        return self.case_pass()

    def common_clean_up(self):
        self.ssh.send("rm -rf /root/1G.file")
