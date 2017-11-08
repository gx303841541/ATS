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
        self.ssh.send("dd if=/dev/zero of=/root/1G.file count=1024 bs=1M")
        result = self.ssh.send('dd if=/root/1G.file bs=64k | dd of=/dev/null')
        self.LOG.info('max read speed:\n' + result)
        return self.case_pass()

    def common_clean_up(self):
        self.ssh.send("rm -rf /root/1G.file")
