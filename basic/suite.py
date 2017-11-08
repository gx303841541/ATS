#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""suite mgr
   by Kobe Gong. 2017-8-25
"""

import re
import random
import sys
import time
import os
import shutil
import datetime
import threading
import functools
import logging
import decimal
import subprocess
import ConfigParser

from basic.cprint import cprint
import APIs.common_APIs as common_APIs
from APIs.common_APIs import my_system_no_check, my_system, my_system_full_output

#suite_lock = threading.Lock()


# ATS use this to manage a suite
class Suite():
    def __init__(self, config_file, id, name, cases, sub_suites):
        self.config_file = config_file
        self.cprint = cprint(__name__)
        self.id = id
        self.name = name
        self.cases = cases
        self.sub_suites = sub_suites
        self.fail_cases = []
        self.need_stop = False

    def __cmp__(self, other):
        if self.__eq__(other):
            return 0
        elif self.__lt__(other):
            return -1
        else:
            return 1

    def __eq__(self, other):
        if not isinstance(other, Suite):
            raise TypeError, "Can't cmp other type to Suite!"
        if self.name == other.name:
            return True
        else:
            return False

    def __lt__(self, other):
        if not isinstance(other, Suite):
            raise TypeError, "Can't cmp other type to Suite!"
        if self.name < other.name:
            return True
        else:
            return False

    def __clean_testlog(self):
        try:
            self.log_dir = self.config_file.get("system", "result_dir")
            dir_separator = os.path.sep

            if os.path.exists(self.log_dir + dir_separator + 'tmp' + dir_separator):
                shutil.rmtree(self.log_dir + dir_separator +
                              'tmp' + dir_separator)
            os.mkdir(self.log_dir + dir_separator + 'tmp' + dir_separator)

        except Exception as er:
            self.cprint.error_p("Something wrong!!![%s]" % (er))

    def __get_tmp_dir(self):
        log_dir = self.log_dir
        dir_separator = os.path.sep
        return common_APIs.dirit(self.log_dir + dir_separator + 'tmp' + dir_separator)

    def __get_suite_dir(self):
        suite_name = re.sub(r'^[A-Z]+:', '', self.name, re.S)
        log_dir = self.config_file.get("system", "result_dir")
        dir_separator = os.path.sep
        log_dir += dir_separator + re.sub(r'%s+' % (re.escape(dir_separator)), '_', suite_name,
                                          re.S) + '-' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + dir_separator
        return common_APIs.dirit(log_dir)

    def get_suite_id(self):
        return self.id

    def get_suite_name(self):
        return self.name

    def get_suite_cases(self):
        return self.cases

    def get_suite_sub_suites(self):
        return self.sub_suites

    def get_suite_fail_cases(self):
        return self.fail_cases

    def set_suite_fail_cases(self, fail_cases):
        if not isinstance(fail_cases, list):
            raise TypeError
        else:
            for case in fail_cases:
                if case in self.fail_cases:
                    continue
                else:
                    self.fail_cases.append(fail_cases)

    def my_son(self, *arg):
        grandson = threading.Thread(target=self.mu_grandson)
        grandson.setDaemon(True)
        grandson.start()
        while self.need_stop == False:
            #self.cprint.yinfo_p("Oh, it is son!")
            time.sleep(1)
        #self.cprint.yinfo_p("Oh, son stop!")

    def mu_grandson(self, *arg):
        cmd_result = my_system_no_check("nosetests -w {} -v -s --exe --with-id --with-xunit --xunit-file={} --with-html-output --html-out-file={} 2>{}".format(
            self.get_suite_name(), self.suite_log_dir + 'result.xml', self.suite_log_dir + 'result.html', self.suite_log_dir + 'stdout.log'))
        self.need_stop = True
        #self.cprint.notice_p("Oh, grandson stop!")

    def run(self):
        self.__clean_testlog()
        log_dir = self.__get_suite_dir()
        self.suite_log_dir = log_dir
        try:
            os.mkdir(log_dir)
        except Exception as er:
            cprint.error_p(
                'Can not create log dir: %s\n[[%s]]' % (log_dir, str(er)))
            sys.exit()

        son = threading.Thread(target=self.my_son)
        son.start()
        try:
            while(self.need_stop == False):
                #self.cprint.warn_p("Oh, it is me!")
                time.sleep(1)
        except Exception as e:
            #self.cprint.warn_p("Oh, me stop!" + str(e))
            pass
        finally:
            self.need_stop = True
            son.join()
            self.need_stop = False
            #self.cprint.warn_p("Oh, update stop flag!")

        common_APIs.dir_copy(self.__get_tmp_dir(), log_dir)
        return log_dir


if __name__ == '__main__':
    pass
