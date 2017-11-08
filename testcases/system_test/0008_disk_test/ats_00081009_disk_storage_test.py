#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import re
import os
import sys
import datetime

from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        self.serial.open()
        self.ssh.connect()
        self.ssh.send('mkdir /udisk/usb1/testfiles')
        self.serial.send('cd /udisk/user/testfiles')
        total_size = 5000 * 1
        for i in range(5000):
            self.ssh.send('dd if=/dev/zero of=testfile_%s count=1 bs=1k' % (i))
            self.serial.send('mkdir testdir_%s' % (i))
            self.serial.send('cd testdir_%s' % (i))

        start_time = datetime.datetime.now()
        result = self.ssh.send("cp -R /udisk/usb1/testfiles /udisk/user")
        end_time = datetime.datetime.now()
        time_diff = end_time - start_time
        total_time = time_diff.seconds + (time_diff.microseconds / (1000.0 * 1000))
        result = self.ssh.send('ls -lh /udisk/user')
        if re.search(r'testfiles', result, re.M):
            self.LOG.debug('cp -R /udisk/usb1/testfiles /udisk/user success!')
            self.LOG.info('cp files from usb1 use %ss, total size: %dk, speed is :%fk/s' % (total_time, total_size, total_size/ (total_time + 0.0)))
            return self.case_pass()
        else:
            self.LOG.error('cp -R /udisk/usb1/testfiles /udisk/user failed![%s]' % result)
            return self.case_fail()

    def common_clean_up(self):
        self.ssh.send("rm -rf /udisk/user/testfiles")
        self.ssh.send("rm -rf /udisk/usb1/testfiles")
