#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ATS framework
by Kobe Gong 2017-8-21
use:
    define testcase interface follow nose's case
"""

import os
import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')
import re
import datetime
import traceback
from abc import ABCMeta, abstractmethod

from nose.tools import with_setup, nottest, istest
from nose.tools import assert_equal


# define testcase which can be find by nose
class TestCase(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def setup(self):
        self.update_db_info()

    def teardown(self):
        if self.serial.is_open():
            self.serial.close()

        if self.ssh.is_open():
            self.ssh.close()

        if self.telnet.is_open():
            self.telnet.close()

        self.wifi.wifi_close()


    @istest
    @with_setup(setup, teardown)
    def test(self):
        # 0:pass
        # 1:faile
        self.common_config()
        result = 0
        try:
            result = self.run()
        except Exception as e:
            traceback.print_exc()
            self.LOG.critical(str(e))
            assert False
        else:
            assert_equal(0, result)
        finally:
            self.common_clean_up()

    @abstractmethod
    def run(self):
        pass

    def common_config(self):
        pass

    def common_clean_up(self):
        pass

    def case_pass(self, success_info='pass'):
        self.LOG.info(success_info)
        return 0

    def case_fail(self, error_info='fail'):
        self.LOG.error(error_info)
        return 1
