#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import re
import os
import sys
import random
import datetime

from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        total_size = 0
        self.ssh.connect()
        self.ssh.send("mkdir /udisk/monitor/testfiles10000_part1")
        for i in range(9000):
            size = random.randint(200, 1 * 1024)
            total_size += size
            self.ssh.send('dd if=/dev/zero of=/udisk/monitor/testfiles10000_part1/testfile_%s count=%s bs=1k' % (i, size))

        self.ssh.send("mkdir /udisk/monitor/testfiles10000_part2")
        for i in range(9000, 10000):
            size = random.randint(1024, 10 * 1024)
            total_size += size
            self.ssh.send('dd if=/dev/zero of=/udisk/monitor/testfiles10000_part2/testfile_%s count=%s bs=1k' % (i, size))


        start_time = datetime.datetime.now()
        result = self.ssh.send("cp -a /udisk/monitor/testfiles10000_part1 /udisk/monitor/testfiles10000_part2 /udisk/usb1/")
        end_time = datetime.datetime.now()
        time_diff = end_time - start_time
        total_time = time_diff.seconds + (time_diff.microseconds / (1000.0 * 1000))

        result = self.ssh.send('ls -lh /udisk/usb1')
        if re.search(r'testfiles10000_part1', result, re.M) and re.search(r'testfiles10000_part2', result, re.M):
            self.LOG.debug('cp -r /udisk/monitor/testfiles10000/ /udisk/usb1 success!')
            self.LOG.info('cp files to usb1 use %ss, total size: %dk, speed is :%fk/s' % (total_time, total_size, total_size/ (total_time + 0.0)))
        else:
            self.LOG.error('cp -r /udisk/monitor/testfiles10000/ /udisk/usb1 failed![%s]' % result)
            return self.case_fail()

        start_time = datetime.datetime.now()
        result = self.ssh.send("cp -a /udisk/usb1/testfiles10000_part1 /udisk/usb1/testfiles10000_part2 /udisk/user/")
        end_time = datetime.datetime.now()
        time_diff = end_time - start_time
        total_time = time_diff.seconds + (time_diff.microseconds / (1000.0 * 1000))

        result = self.ssh.send('ls -lh /udisk/user')
        if re.search(r'testfiles10000_part1', result, re.M) and re.search(r'testfiles10000_part2', result, re.M):
            self.LOG.debug('cp -r /udisk/usb1/testfiles10000/ /udisk/user success!')
            self.LOG.info('cp files from usb1 use %ss, total size: %dk, speed is :%fk/s' % (total_time, total_size, total_size/ (total_time + 0.0)))
            return self.case_pass()
        else:
            self.LOG.error('cp -r /udisk/usb1/testfiles10000/ /udisk/user failed![%s]' % result)
            return self.case_fail()

    def common_clean_up(self):
        self.ssh.send("rm -rf /udisk/monitor/testfiles10000_part1")
        self.ssh.send("rm -rf /udisk/monitor/testfiles10000_part2")
        self.ssh.send("rm -rf /udisk/user/testfiles10000_part1")
        self.ssh.send("rm -rf /udisk/user/testfiles10000_part2")
        self.ssh.send("rm -rf /udisk/usb1/testfiles10000_part1")
        self.ssh.send("rm -rf /udisk/usb1/testfiles10000_part2")
