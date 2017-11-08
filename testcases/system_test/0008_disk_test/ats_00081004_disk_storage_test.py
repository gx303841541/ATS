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
        result = self.ssh.send("dd if=/dev/zero of=/udisk/usb1/testfiles count=5 bs=1M")
        self.ssh.send("cp -R /udisk/usb1/testfiles /udisk/user")
        result = self.ssh.send('ls -l /udisk/user/testfiles')
        if re.search(r'testfiles', result, re.S):
            self.LOG.debug('cp -R /udisk/usb1/testfiles /udisk/user success!')
        else:
            self.LOG.error('cp -R /udisk/usb1/testfiles /udisk/user failed![%s]' % result)
            return self.case_fail()

        self.ssh.send("cp -R /udisk/user/testfiles /udisk/monitor")
        result = self.ssh.send('ls -l /udisk/monitor/testfiles')
        if re.search(r'testfiles', result, re.S):
            self.LOG.debug('cp -R /udisk/user/testfiles /udisk/monitor success!')
        else:
            self.LOG.error('cp -R /udisk/user/testfiles /udisk/monitor failed!')
            return self.case_fail()

        self.ssh.send("mv /udisk/user/testfiles /udisk/monitor/testfiles2")
        result = self.ssh.send('ls -l /udisk/monitor/testfiles2')
        if re.search(r'testfiles2', result, re.S):
            self.LOG.debug('mv /udisk/user/testfiles /udisk/monitor/testfiles2 success!')
        else:
            self.LOG.error('mv /udisk/user/testfiles /udisk/monitor/testfiles2 failed!')
            return self.case_fail()

        self.ssh.send("mv /udisk/monitor/testfiles /udisk/user/testfiles2")
        result = self.ssh.send('ls -l /udisk/user/testfiles2')
        if re.search(r'testfiles2', result, re.S):
            self.LOG.debug('mv /udisk/monitor/testfiles /udisk/user/testfiles2 success!')
        else:
            self.LOG.error('mv /udisk/monitor/testfiles /udisk/user/testfiles2 failed!')
            return self.case_fail()

        return self.case_pass()


    def common_clean_up(self):
        self.ssh.send("rm -rf /udisk/usb1/testfiles")
        self.ssh.send("rm -rf /udisk/user/testfiles")
        self.ssh.send("rm -rf /udisk/monitor/testfiles")
        self.ssh.send("rm -rf /udisk/monitor/testfiles2")
        self.ssh.send("rm -rf /udisk/user/testfiles2")
