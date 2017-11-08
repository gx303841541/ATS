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
        self.fail = 0
        self.ssh.connect()
        result = self.ssh.send("dd if=/dev/zero of=/udisk/monitor/testfile_25G count=%d bs=1M" % (1024 * 25))
        self.ssh.send("dd if=/udisk/monitor/testfile_25G bs=64K of=/udisk/usb1/testfile_25G")
        result = self.ssh.send('ls -lh /udisk/usb1/testfile_25G')
        if re.search(r'5\.0G.*testfile_25G', result, re.M):
            self.LOG.debug('dd if=/udisk/monitor/testfile_25G bs=64K of=/udisk/usb1/testfile_25G success!')
            #return self.case_pass()
        else:
            self.LOG.error('dd if=/udisk/monitor/testfile_25G bs=64K of=/udisk/usb1/testfile_25G failed![%s]' % result)
            return self.case_fail()

        self.ssh.send("dd if=/udisk/usb1/testfile_25G bs=64K of=/udisk/user/testfile_25G")
        result = self.ssh.send('ls -lh /udisk/user/testfile_25G')
        if re.search(r'5\.0G.*testfile_25G', result, re.M):
            self.LOG.debug('dd if=/udisk/usb1/testfile_25G bs=64K of=/udisk/user/testfile_25G success!')
            #return self.case_pass()
        else:
            self.LOG.error('dd if=/udisk/usb1/testfile_25G bs=64K of=/udisk/user/testfile_25G failed![%s]' % result)
            return self.case_fail()

        process_ids = []
        process_ids.append(threading.Thread(target=self.file_cp, args=('/udisk/usb1/testfile_25G', '/udisk/monitor/testfile_25G_mul')))
        process_ids.append(threading.Thread(target=self.file_cp, args=('/udisk/monitor/testfile_25G', '/udisk/usb1/testfile_25G_mul')))
        for pr in process_ids:
            pr.daemon = True
            pr.start()

        for pr in process_ids:
            pr.join()

        if self.fail == 1:
            return self.case_fail()
        else:
            return self.case_pass()

    def common_clean_up(self):
        self.ssh.send("rm -rf /udisk/monitor/testfile_25G")
        self.ssh.send("rm -rf /udisk/user/testfile_25G")
        self.ssh.send("rm -rf /udisk/usb1/testfile_25G")
        self.ssh.send("rm -rf /udisk/monitor/testfile_25G_mul")
        self.ssh.send("rm -rf /udisk/usb1/testfile_25G_mul")

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
