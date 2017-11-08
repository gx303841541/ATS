#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import os
import sys
import re
import threading
import datetime

from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        self.ssh.connect()
        self.ssh.send("dd if=/dev/zero of=/udisk/usb1/FAT32_4G count=%d bs=1M" % (1024 * 4))
        self.ssh.send("cp /udisk/usb1/FAT32_4G /udisk/monitor")
        result = self.ssh.send('ls -lh /udisk/monitor/FAT32_4G')
        if re.search(r'4\.0G.*FAT32_4G', result, re.M):
            self.LOG.debug('cp /udisk/usb1/FAT32_4G /udisk/monitor success!')
            return self.case_pass()
        else:
            self.LOG.error('cp /udisk/usb1/FAT32_4G /udisk/monitor failed![%s]' % result)
            return self.case_fail()

    def common_clean_up(self):
        self.ssh.send("rm -rf /udisk/monitor/FAT32_4G")
        self.ssh.send("rm -rf /udisk/usb1/FAT32_4G")
