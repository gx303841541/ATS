#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""multi process app demo
by Kobe Gong. 2017-10-23
"""

import re
import sys
import time
import os
import shutil
import datetime
import multiprocessing
import random
import signal
import subprocess
import argparse
import logging
from cmd import Cmd
import decimal
if sys.platform == 'linux':
    import configparser as ConfigParser
    import queue as Queue
else:
    import ConfigParser
    import Queue

from collections import defaultdict

from basic.log_tool import MyLogger
from basic.cprint import cprint
import APIs.common_APIs as common_APIs
from APIs.common_APIs import my_system_no_check, my_system, my_system_full_output, protocol_data_printB
import my_socket.my_socket as my_socket

# 命令行参数
class ArgHandle():
    def __init__(self):
        self.parser = self.build_option_parser("-" * 50)

    def build_option_parser(self, description):
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            '-l', '--cmdloop',
            action='store_true',
            help='whether go into cmd loop',
        )
        return parser
        return parser

    def get_args(self, attrname):
        return getattr(self.args, attrname)

    def check_args(self):
        pass

    def run(self):
        self.args = self.parser.parse_args()
        cprint.notice_p("CMD line: " + str(self.args))
        self.check_args()


# CMD loop
class MyCmd(Cmd):
    def __init__(self):
        Cmd.__init__(self)
        self.prompt = "APP>"

    def default(self, arg, opts=None):
        try:
            subprocess.call(arg, shell=True)
        except:
            pass

    def emptyline(self):
        pass

    def help_exit(self):
        print("Will exit")

    def do_exit(self, arg, opts=None):
        cprint.notice_p("Exit CLI, good luck!")
        sys_cleanup()
        sys.exit()


# 系统调度
def sys_proc(action="default"):
    global process_ids
    process_ids = []
    for pr in process_list:
        process_ids.append(multiprocessing.Process(target=pr[0], args=pr[1:]))

    for pr in process_ids:
        pr.daemon = True
        pr.start()


def sys_join():
    for pr in process_ids:
        pr.join()


# 系统初始化函数，在所有模块开始前调用
def sys_init():
    LOG.info("Let's go!!!")


# 系统清理函数，系统退出前调用
def sys_cleanup():
    for pr in process_ids:
        pr.terminate()
    LOG.warn("Goodbye!!!")


# 主程序入口
if __name__ == '__main__':
    # sys log init
    LOG = MyLogger(os.path.abspath(sys.argv[0]).replace('py', 'log'), clevel=logging.DEBUG,
                   rlevel=logging.WARN)
    cprint = cprint(__name__)

    # sys init
    sys_init()

    # cmd arg init
    arg_handle = ArgHandle()
    arg_handle.run()

    # multi process
    global process_list
    process_list = []
    queue = multiprocessing.Queue()
    e = multiprocessing.Event()
    lock = multiprocessing.Lock()
    manager = multiprocessing.Manager()
    sum = manager.Value('tmp', 0)


    server = my_socket.MyServer(('', 8888), LOG, debug=True, singlethread=True)
    process_list.append([server.run_forever])
    #process_list.append([server.sendloop])

    # run threads
    sys_proc()

    if arg_handle.get_args('cmdloop'):
        # cmd loop
        signal.signal(signal.SIGINT, lambda signal, frame: cprint.notice_p('Exit SYSTEM: exit'))
        my_cmd = MyCmd()
        my_cmd.cmdloop()
    else:
        sys_join()

        # sys clean
        sys_cleanup()
        sys.exit()
