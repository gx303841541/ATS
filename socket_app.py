#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""air sim
by Kobe Gong. 2017-9-11
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

# 命令行参数梳理， 目前仅有-p 指定串口端口号


class ArgHandle():
    def __init__(self):
        self.parser = self.build_option_parser("-" * 50)

    def build_option_parser(self, description):
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            '-p', '--server-port',
            dest='server_port',
            action='store',
            default=5100,
            type=int,
            help='Specify TCP server port',
        )

        parser.add_argument(
            '-i', '--server-IP',
            dest='server_IP',
            action='store',
            default='192.168.10.1',
            help='Specify TCP server IP address',
        )

        parser.add_argument(
            '-c', '--client-count',
            dest='client_count',
            action='store',
            default=1,
            type=int,
            help='Specify how many socket client will be create',
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


# CMD loop, 可以查看各个串口的消息统计
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
        sys.exit()


# 系统调度
def sys_proc(action="default"):
    global thread_ids
    thread_ids = []
    for th in thread_list:
        thread_ids.append(threading.Thread(target=th[0], args=th[1:]))

    for th in thread_ids:
        th.setDaemon(True)
        th.start()
        # time.sleep(0.1)


def sys_join():
    for th in thread_ids:
        th.join()


# 系统初始化函数，在所有模块开始前调用
def sys_init():
    LOG.info("Let's go!!!")


# 系统清理函数，系统推出前调用
def sys_cleanup():
    for th in thread_ids:
        th.close()

    LOG.info("Goodbye!!!")


# 空调模拟程序入口
if __name__ == '__main__':
    # sys log init
    LOG = MyLogger(os.path.abspath(sys.argv[0]).replace('py', 'log'), clevel=logging.DEBUG,
                   rlevel=logging.WARN)
    cprint = cprint(__name__)

    # cmd arg init
    arg_handle = ArgHandle()
    arg_handle.run()

    # sys init
    sys_init()

    # multi thread
    global thread_list
    thread_list = []

    # create clients
    clients = []
    for i in range(1, arg_handle.get_args('client_count') + 1):
        LOG.yinfo('To create client: %d' % (i))
        client = my_socket.MyClient((arg_handle.get_args('server_IP'), arg_handle.get_args(
            'server_port')), LOG, Queue.Queue(), Queue.Queue(), heartbeat=15, debug=True, singlethread=False)
        thread_list.append([client.run_forever])
        thread_list.append([client.sendloop])

    # run threads
    sys_proc()
    #sys_join()

    # cmd loop
    signal.signal(signal.SIGINT, lambda signal, frame: cprint.notice_p('Exit SYSTEM: exit'))
    my_cmd = MyCmd()
    my_cmd.cmdloop()

    # sys clean
    sys_cleanup()
    sys.exit()
