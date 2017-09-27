#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ATS framework
by Kobe Gong 2017-8-21
use:
    define testcase interface follow nose's case
"""

import os
import sys
import re
import datetime
from abc import ABCMeta, abstractmethod

from nose.tools import with_setup, nottest, istest
from nose.tools import assert_equal


# define testcase which can be find by nose
class TestCase(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    def setup(self):
        # test precondition
        pass

    def teardown(self):
        # test clean up!
        pass

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
        if self.serial.is_open():
            self.serial.close()

        if self.ssh.is_open():
            self.ssh.close()

        if self.telnet.is_open():
            self.telnet.close()
