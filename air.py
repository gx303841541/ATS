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
import ConfigParser
from cmd import Cmd
import decimal

from collections import defaultdict

from basic.log_tool import MyLogger
from basic.cprint import cprint
import APIs.common_APIs as common_APIs
from APIs.common_APIs import my_system_no_check, my_system, my_system_full_output, protocol_data_printB
from protocol.air_protocol import Protocol_proc, Air

# 命令行参数梳理， 目前仅有-p 指定串口端口号
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

        parser.add_argument(
            '-n', '--serial-number',
            dest='serial_number',
            action='store',
            default=8,
            type=int,
            help='Specify how many serial port will be listened',
        )

        parser.add_argument(
            '-p', '--serial-port',
            dest='port_list',
            action='append',
            # metavar='pattern',
            # required=True,
            default=[],
            help='Specify serial port',
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
    def __init__(self, coms_list):
        Cmd.__init__(self)
        self.prompt = "AIR>"
        self.coms_list = coms_list

    def help_sts(self):
        cprint.notice_p("show all msgs received!")

    def do_sts(self, arg, opts=None):
        msg_statistics = defaultdict(int)
        for com in self.coms_list:
            cprint.common_p(self.coms_list[com].port + ':')
            msgs_dict = self.coms_list[com].get_msg_msg_statistics()
            for msg in msgs_dict:
                cprint.notice_p('\t' * 2 + msg + ': ' + str(msgs_dict[msg]))
                msg_statistics[msg] += msgs_dict[msg]

        cprint.debug_p('ALL' + ':')
        for msg in msg_statistics:
            cprint.notice_p('\t' * 2 + msg + ': ' + str(msg_statistics[msg]))

    def help_st(self):
        cprint.notice_p("show one port msg received!")

    def do_st(self, arg, opts=None):
        if re.match(r'^\d+$', arg) and arg in self.coms_list:
            cprint.common_p(self.coms_list[arg].port + ':')
            msgs_dict = self.coms_list[arg].get_msg_msg_statistics()
            for msg in msgs_dict:
                cprint.notice_p('\t' * 2 + msg + ': ' + str(msgs_dict[msg]))
        else:
            cprint.warning_p("unknow port: %s!" % (arg))

    def help_send(self):
        cprint.notice_p("send sting to comx, 'all' mean to all")

    def do_send(self, arg, opts=None):
        args = arg.split()
        if len(args) > 1 and args[0] in (self.coms_list.keys() + ['all']):
            if args[0] == 'all':
                for com in self.coms_list:
                    self.coms_list[com].queue_out.put(' '.join(args[1:]))
            else:
                self.coms_list[args[0]].queue_out.put(' '.join(args[1:]))
        else:
            cprint.warning_p("unknow port: %s!" % (arg))

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
        time.sleep(0.1)

    # for th in thread_ids:
    #    th.join()


# 系统初始化函数，在所有模块开始前调用
def sys_init():
    LOG.info("Let's go!!!")


# 系统清理函数，系统推出前调用
def sys_cleanup():
    LOG.info("Goodbye!!!")


# 空调模拟程序入口
if __name__ == '__main__':
    # sys log init
    LOG = MyLogger(__name__ + ".log", clevel=logging.DEBUG,
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
    if arg_handle.get_args('cmdloop') or True:

        # create serial objs
        global coms_list
        coms_list = {}
        for com_id in arg_handle.get_args('port_list'):
            coms_list[com_id] = Air('COM' + com_id, logger=LOG)
            thread_list.append([coms_list[com_id].run_forever])

        # create protocal handle obj
        msg_proc = Protocol_proc(coms_list, logger=LOG)
        thread_list.append([msg_proc.run_forever])

        # run threads
        sys_proc()

        # cmd loop
        signal.signal(signal.SIGINT, lambda signal, frame: cprint.notice_p(
            'Exit SYSTEM: exit'))
        my_cmd = MyCmd(coms_list, )
        my_cmd.cmdloop()

    else:
        pass

    # sys clean
    sys_cleanup()
    sys.exit()
