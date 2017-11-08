#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import re
import os
import sys

from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        self.serial.open()
        self.ssh.connect()
        self.ssh.send('mkdir /udisk/user/testfiles')
        self.serial.send('cd /udisk/user/testfiles')
        for i in range(100):
            self.serial.send('mkdir testdir_%s' % (i))
            self.serial.send('cd testdir_%s' % (i))
            for j in range(1000):
                self.ssh.send('dd if=/dev/zero of=testfile_%s_%s count=1 bs=1k' % (i, j))

        cp_result = self.ssh.send("cp -R /udisk/user/testfiles /udisk/usb1")
        ls_result = self.ssh.send('ls -lh /udisk/usb1')
        if re.search(r'testfiles', ls_result, re.M):
            self.LOG.debug('cp -R /udisk/user/testfiles /udisk/usb1 success!\n' + cp_result)
            return self.case_pass()
        else:
            self.LOG.error('cp -R /udisk/user/testfiles /udisk/usb1 failed![%s]' % ls_result)
            time.sleep(90)
            return self.case_fail()

    def common_clean_up(self):
        self.ssh.send("rm -rf /udisk/user/testfiles")
        self.ssh.send("rm -rf /udisk/usb1/testfiles")
