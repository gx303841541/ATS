#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""CLI loop
by Kobe Gong 2017-8-21
use:
    go into ATS'CLI
"""

import re
import sys
import time
import os
import shutil
import datetime
import threading
import random
import signal
import subprocess
import argparse
import logging
if sys.platform == 'linux':
    import configparser as ConfigParser
    import queue as Queue
else:
    import ConfigParser
    import Queue
from cmd import Cmd
import decimal

from cowpy import cow

from basic.log_tool import MyLogger
from basic.cprint import cprint
from basic.suite import Suite
from basic.case import Case
import APIs.common_APIs as common_APIs
from APIs.common_APIs import my_system_no_check, my_system, my_system_full_output


class ArgHandle():
    def __init__(self, name):
        self.parser = self.build_option_parser("-" * 50)

    def build_option_parser(self, description):
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            '-l', '--cmdloop',
            action='store_true',
            help='whether go into cmd loop',
        )
        return parser

    def get_args(self, attrname):
        return getattr(self.args, attrname)

    def check_args(self):
        pass

    def run(self):
        self.args = self.parser.parse_args()
        cprint.notice_p("CMD line: " + str(self.args))
        self.check_args()


class MyCmd(Cmd):
    def __init__(self, config_file='config.ini'):
        Cmd.__init__(self)
        self.prompt = "ATS>"
        self.config_file_ori = config_file
        self.config_file = ConfigParser.ConfigParser()
        self.config_file.read(config_file)
        self.case_re = r'^ats_\d{8}_\w+_test\.py$'
        self.__case_update()
        self.log_dir = self.config_file.get("system", "result_dir")
        self.dir_separator = os.path.sep
        self.last_suite = None
        self.last_suite_log_dir = None

    def __case_update(self):
        self.cases = {}
        self.suites = {}
        self.suite_name_to_id = {}
        self.case_dir = self.config_file.get("system", "case_dir")
        case_list = common_APIs.get_file_by_re(self.case_dir, self.case_re)
        for case in case_list:
            m = re.match(
                r'^(?P<case_dir>.*?)(?P<case_file>(?P<case_name>ats_(?P<case_id>\d{8})_\w+_test\.py))$', case, re.S)
            self.cases[m.group('case_id')] = Case(config_file=self.config_file, id=m.group(
                'case_id'), name=m.group('case_name'), dir=m.group('case_dir'))

        tmp_suites = []
        for case in sorted(self.cases):
            if self.cases[case].get_case_dir() in tmp_suites:
                continue
            else:
                tmp_suites.append(self.cases[case].get_case_dir())
        tmp_suites.sort()

        # create suite bojects
        for i in range(1, len(tmp_suites) + 1):
            all_things = os.listdir(tmp_suites[i - 1])
            dir_list = []
            case_list = []

            for item in all_things:
                if os.path.isfile(os.path.join(tmp_suites[i - 1], os.path.basename(item))) and re.match(self.case_re, item, re.S):
                    case_list.append(os.path.join(
                        tmp_suites[i - 1], os.path.basename(item)))
                elif os.path.isdir(os.path.join(tmp_suites[i - 1], os.path.basename(item))) and item.endswith('test'):
                    dir_list.append(os.path.join(
                        tmp_suites[i - 1], os.path.basename(item)))
                else:
                    continue

            name = re.sub(r'[A-Z]+:', '', tmp_suites[i - 1])
            name = re.sub(r'%s$' % re.escape(os.path.sep), '', name)
            self.suites[str(i)] = Suite(config_file=self.config_file, id=i,
                                        name=os.path.basename(name), cases=case_list, sub_suites=dir_list, dirstr=tmp_suites[i - 1])
            self.suite_name_to_id[name] = str(i)

        # create log dir is not exist
        if not os.path.exists(self.config_file.get("system", "result_dir")):
            os.makedirs(self.config_file.get("system", "result_dir"))

    def __get_id_by_name(self, name):
        # cprint.debug_p(name)
        r = re.match(r'^ats_(?P<id>\d{8})_\w+\.py$',
                     os.path.basename(name), re.S)
        return r.group('id')

    def __clean_testlog(self):
        dir_separator = os.path.sep
        try:
            self.log_dir = common_APIs.dirit(
                self.config_file.get("system", "result_dir"))

            if os.path.exists(self.log_dir + 'tmp' + dir_separator):
                shutil.rmtree(self.log_dir + 'tmp' + dir_separator)
            os.mkdir(self.log_dir + 'tmp' + dir_separator)

        except Exception as er:
            cprint.error_p("Something wrong!!![%s]" % (er))

    def __get_tmp_dir(self):
        log_dir = self.log_dir
        dir_separator = os.path.sep
        return common_APIs.dirit(self.log_dir + dir_separator + 'tmp' + dir_separator)

    def help_listcase(self):
        cprint.common_p("list case info by case id")

    def do_listcase(self, arg=None, opts=None):
        if arg in self.cases:
            cprint.debug_p(arg + ':')
            for item in sorted(self.cases[arg].__dict__):
                if item in ['config_file', 'cprint']:
                    continue

                cprint.common_p("    " + item.ljust(20) + ':    ' +
                                str(getattr(self.cases[arg], item)).ljust(40))
            cprint.debug_p('-' * 30)
        else:
            cprint.warn_p('unknow case: %s' % (arg))

    def help_listcases(self):
        cprint.common_p(
            "list all the cases under dir:{}".format(self.case_dir))

    def do_listcases(self, arg, opts=None):
        for case in sorted(self.cases):
            self.do_listcase(arg=case)
        cprint.notice_p('total: %s' % (len(self.cases)))

    def help_listsuite(self):
        cprint.common_p(
            "list all the subsuites and cases under the given suite")

    def ndo_suite_show(self, id, pre_str='', fatherdir=''):
        dir = self.suites[id].get_suite_name()

        if len(fatherdir) > 0 and not fatherdir.endswith(self.dir_separator):
            fatherdir += self.dir_separator

        cprint.notice_p(pre_str + dir.replace(fatherdir, '') + ':')

        pre_str += ' ' * (len(dir) + 1 - len(fatherdir))
        for item in self.suites[id].get_suite_cases():
            if self.cases[self.__get_id_by_name(item)].get_case_result() in ['pass', None]:
                cprint.common_p(pre_str + item)
            else:
                cprint.error_p(pre_str + item)

        for subdir in self.suites[id].get_suite_sub_suites():
            subdir = common_APIs.dirit(subdir)
            if subdir in self.suite_name_to_id:
                self.ndo_suite_show(
                    self.suite_name_to_id[subdir], pre_str, dir)
            else:
                cprint.error_p(subdir + ' is wrong suite name!')

    def do_listsuite(self, arg, opts=None):
        if arg in self.suites:
            self.ndo_suite_show(arg)
        else:
            cprint.warn_p('unknow suite: %s' % (arg))

    def help_listsuites(self):
        cprint.common_p("will list all the suites")

    def do_listsuites(self, arg, opts=None):
        for index in sorted(self.suites, cmp=lambda x, y: cmp(int(x), int(y))):
            cprint.notice_p("    " + str(self.suites[index].get_suite_id()).ljust(
                10) + ':    ' + self.suites[index].dirstr.ljust(40))
            cprint.common_p('-' * 30)

    def help_srun(self):
        cprint.common_p("run suite")

    def __faild_cases_proc(self, stout_file, suite=None):
        cprint.debug_p("To open %s:\n" % (stout_file))
        with open(stout_file, 'r') as f:
            all = f.read()
            if len(all) > 0:
                log_list = re.split(r'==========+', all, re.S)
                if log_list:
                    pass
                else:
                    cprint.error_p("nose output log format wrong!")
            else:
                cprint.error_p("No case found or something unknow happen!")
                return 1

            cases = re.split(r'[\r\n]+(?=#\d+)', log_list[0], maxsplit=0)
            # cases = re.findall(r'(#\d+\s+.*?[\r\n]+(?:ok|FAIL|ERROR))', log_list[0], re.S)

            cprint.debug_p('Total cases: ' + str(len(cases)))

            total_cases = 0
            pass_cases = 0
            fail_cases = 0
            fail_list = []
            for case in cases:

                info = re.findall(
                    r'(^#\d+\s+\w+|^(?:ok|FAIL|ERROR))', case, re.M)
                if len(info) == 2:
                    name, result = info
                elif len(info) == 1 and case == cases[-1]:
                    name, result = info + ['interrupted']
                else:
                    cprint.error_p(
                        'ATS result handler module has errors, please check here!')
                    for i in info:
                        cprint.error_p(i)

                r = re.match(
                    r'#(?P<index>\d+)\s+(?P<name>\w+)', name, re.S)
                if r:
                    total_cases += 1
                else:
                    continue

                if result == 'ok':
                    result = 'pass'
                    pass_cases += 1
                    cprint.notice_p(r.group('index').ljust(
                        5) + ': ' + r.group('name').ljust(60, '.') + result)
                else:
                    #result = 'fail'
                    fail_cases += 1
                    fail_list.append(r.group('name') + '.py')
                    cprint.error_p(r.group('index').ljust(
                        5) + ': ' + r.group('name').ljust(60, '.') + result)
                self.cases[self.__get_id_by_name(
                    r.group('name') + '.py')].set_case_result(result)
                self.cases[self.__get_id_by_name(
                    r.group('name') + '.py')].set_case_state('done')

            # add fail cases to related suite
            if fail_cases:
                self.last_suite.set_suite_fail_cases(fail_list)

            # give a simple report
            cprint.common_p("Total: {}".format(total_cases))
            cprint.notice_p("pass : {}".format(pass_cases))
            cprint.error_p("fail : {}".format(fail_cases))

            with decimal.localcontext() as ctx:
                ctx.prec = 2
                if total_cases > 0:
                    cprint.common_p('Success Rate: '.ljust(
                        20) + "%.2f" % (pass_cases * 100.0 / total_cases) + '%')
                else:
                    cprint.common_p('Success Rate:'.ljust(20) + '0.00%')

    def do_srun(self, arg, opts=None):
        suite_id_list = re.findall(r'(\d+)', arg, re.M)
        suites = []
        suite = ''
        if suite_id_list:
            for id in suite_id_list:
                if id in self.suites:
                    suites.append(self.suites[id])
                    cprint.yinfo_p("Found suite ID: %s, name: %s" % (id, self.suites[id].get_suite_name()))
                else:
                    cprint.error_p("unknow suite ID: %s" % id)

            if len(suites) > 1:
                id_sum = str(int(common_APIs.find_max(self.suites.keys())) + 1)
            else:
                id_sum = suite_id_list[0]

            if id_sum in self.suites:
                suite = self.suites[id_sum]
            else:
                for item in suites:
                    if suite:
                        suite += item
                    else:
                        suite = item
                self.suites[id_sum] = suite
                self.suites[id_sum].id = id_sum

            if len(suites) > 1:
                self.suite_name_to_id[suite.get_suite_name()] = id_sum
            cprint.yinfo_p("Run suite ID: %s, name: %s" % (id_sum, suite.get_suite_name()))
            self.last_suite = suite
            suite.run()
            self.__faild_cases_proc(suite.suite_log_dir + 'stdout.log')

        else:
            cprint.error_p("unknow arg: %s" % arg)

    def help_runagain(self):
        cprint.common_p("run last failed cases again")

    def do_runagain(self, arg, opts=None):
        self.__clean_testlog()
        if not self.last_suite:
            cprint.warn_p('No suite had ran so far!')
            return 1
        else:
            cprint.notice_p('Last suite is: %s' %
                            (self.last_suite.get_suite_name()))
            log_dir = self.last_suite.suite_log_dir
            my_system_no_check("nosetests {} -v -s --failed --exe --with-xunit --xunit-file={} --with-html-output --html-out-file={}  2>{}".format(
                self.last_suite.dirstr, log_dir + 'again_result.xml', log_dir + 'again_result.html', log_dir + 'again_stdout.log'))
            common_APIs.dir_copy(self.__get_tmp_dir(), log_dir)
            self.__faild_cases_proc(log_dir + 'again_stdout.log')

    def help_crun(self):
        cprint.common_p("run case")

    def do_crun(self, arg, opts=None):
        self.__clean_testlog()

        if re.match(r'^\d{8}$', arg, re.S):
            if arg in self.cases:
                self.cases[arg].run()
            else:
                cprint.warn_p('%s not found!' % (arg))
        else:
            cprint.error_p("unknow arg: %s" % arg)

    def help_createsuite(self):
        print("help_creatsuite")

    def do_createsuite(self, arg, opts=None):
        print("do_creatsuite")

    def help_addcase(self):
        print("help_addcase")

    def do_addcase(self, arg, opts=None):
        print("do_addcase")

    def help_delcase(self):
        print("help_delcase")

    def do_delcase(self, arg, opts=None):
        print("do_delcase")

    def help_givereport(self):
        print("help_givereport")

    def do_givereport(self, arg, opts=None):
        print("do_givereport")

    def default(self, arg, opts=None):
        try:
            subprocess.call(arg, shell=True)
        except:
            pass

    def emptyline(self):
        pass

    def help_exit(self):
        print("Will exit CTS")

    def do_exit(self, arg, opts=None):
        if os.path.exists(self.config_file.get("system", "case_dir") + self.dir_separator + '.noseids'):
            os.remove(self.config_file.get("system", "case_dir") +
                      self.dir_separator + '.noseids')

        for item in common_APIs.get_file_by_re(self.config_file.get("system", "case_dir"), r'.noseids'):
            os.remove(item)
        if os.path.exists(r'.noseids'):
            cprint.notice_p("To delete .noseids ...")
            os.remove(r'.noseids')

        for item in common_APIs.get_file_by_re(self.config_file.get("system", "case_dir"), r'.*\.pyc'):
            os.remove(item)

        self.config_file = ConfigParser.ConfigParser()
        self.config_file.read(self.config_file_ori)
        self.config_file.set("router_db", "update_flag", 0)
        self.config_file.write(open(self.config_file_ori, "w"))
        cprint.notice_p("Exit CLI, good luck!")
        sys.exit()


def sys_proc(action="default"):
    global thread_ids
    thread_ids = []
    for th in thread_list:
        thread_ids.append(threading.Thread(target=th[0], args=th[1:]))

    for th in thread_ids:
        th.setDaemon(True)
        th.start()
        time.sleep(0.1)

    # for th in thread_ids:
    #    th.join()


def sys_init():
    cprint.notice_p(cow.milk_random_cow('Are you ready?'))
    LOG.info("Let's go!!!")

    config_file_name = 'config.ini'
    config_file = ConfigParser.ConfigParser()
    config_file.read(config_file_name)

    ats_path = config_file.get("system", "ats_path")

    if os.path.exists(ats_path + 'ats.pth'):
        pass
    elif os.path.exists(ats_path):
        shutil.copy(os.getcwd() + '/patch/ats.pth', ats_path)
    else:
        LOG.p.critical(
            "Dir: '%s' not found, your ATS env is not ready!" % (ats_path))
        sys.exit()

    html_tool_path = config_file.get("system", "html_tool_path")
    if os.path.exists(html_tool_path):
        if os.path.exists(html_tool_path + 'htmloutput.py'):
            os.remove(html_tool_path + 'htmloutput.py')
        shutil.copy(os.getcwd() + '/patch/htmloutput.py', html_tool_path)

    else:
        LOG.p.critical(
            "Dir: '%s' not found, your ATS env is not ready!" % (html_tool_path))
        sys.exit()


def sys_cleanup():
    LOG.p.info("Goodbye!!!")


def sig_handler(signal, frame):
    cprint.notice_p('Get signal KeyboardInterrupt')


if __name__ == '__main__':
    # sys log init
    LOG = MyLogger(__name__ + ".log", clevel=logging.DEBUG,
                   rlevel=logging.WARN)

    cprint = cprint(__name__)

    # arg init
    arg_handle = ArgHandle("arg")
    arg_handle.run()

    sys_init()

    global thread_list
    thread_list = []
    if arg_handle.get_args('cmdloop'):

        sys_proc()

        # cmd loop
        signal.signal(signal.SIGINT, sig_handler)
        while True:
            try:
                my_cmd = MyCmd()
                my_cmd.cmdloop()
            # except IOError, e:
            #    if e.errno == 4:
            #        cprint.notice_p('Exit SYSTEM: exit')
            #    else:
            #        cprint.warn_p("some unknow error happen!")
            except KeyboardInterrupt:
                cprint.notice_p('Exit SYSTEM: exit')

    else:
        pass

    sys_cleanup()
    sys.exit()
