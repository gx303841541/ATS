#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import os
import sys
import re
import threading
import datetime
import random

from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        self.fail = 0
        self.ssh.connect()
        self.ssh.send("mkdir /udisk/user/manyfiles")
        total_size = 0
        total_time = 0
        threshold_time = 0
        for i in range(1000):
            size = random.randint(1, 1 * 1024)
            total_size += size
            self.ssh.send('dd if=/dev/zero of=/udisk/user/manyfiles/testfile_%s count=%s bs=1k' % (i, size))

        for i in range(1000, 1100):
            size = random.randint(1 * 1024, 100 * 1024)
            total_size += size
            self.ssh.send('dd if=/dev/zero of=/udisk/user/manyfiles/testfile_%s count=%s bs=1k' % (i, size))

        for i in range(1100, 1110):
            size = random.randint(100 * 1024, 1024 * 1024)
            total_size += size
            self.ssh.send('dd if=/dev/zero of=/udisk/user/manyfiles/testfile_%s count=%s bs=1k' % (i, size))

        for i in range(1110, 1111):
            size = random.randint(1024 * 1024, 2 * 1024 * 1024)
            total_size += size
            self.ssh.send('dd if=/dev/zero of=/udisk/user/manyfiles/testfile_%s count=%s bs=1k' % (i, size))

        while total_time < 7 * 24 * 60 * 60:
            this_time = self.file_cp('/udisk/user/manyfiles', '/udisk/usb1/manyfiles')
            self.ssh.send('rm -rf /udisk/user/manyfiles')
            total_time += this_time
            threshold_time += this_time

            this_time = self.file_cp('/udisk/usb1/manyfiles', '/udisk/user/manyfiles')
            self.ssh.send('rm -rf /udisk/usb1/manyfiles')
            total_time += this_time
            threshold_time += this_time
            if threshold_time >= 16 * 60 * 60:
                time.sleep(24 * 60 * 60 - threshold_time)
                threshold_time = 0
            self.LOG.debug('Total time is: %d, threshold time is %d' % (total_time, threshold_time))

        if self.fail == 0:
            return self.case_pass()
        else:
            return self.case_fail()

    def common_clean_up(self):
        self.ssh.send("rm -rf /udisk/user/manyfiles")
        self.ssh.send("rm -rf /udisk/usb1/manyfiles")

    def file_cp(self, src, dst):
        start_time = datetime.datetime.now()
        result = self.ssh.send("cp -a %s %s" % (src, dst))
        end_time = datetime.datetime.now()
        time_diff = end_time - start_time
        total_time = time_diff.seconds + (time_diff.microseconds / (1000.0 * 1000))

        result = self.ssh.send('ls -lh %s' % (os.path.dirname(dst)))
        if re.search(r'%s' % os.path.basename(dst), result, re.M):
            self.LOG.debug('cp %s to %s success!' % (src, dst))
            self.LOG.info('cp use %ss' % (total_time))
        else:
            self.LOG.error('cp %s to %s failed![%s]' % (result, src, dst))
            self.fail = 1
        return total_time
