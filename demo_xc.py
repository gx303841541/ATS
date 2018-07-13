#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""asyncio process app demo
by Kobe Gong. 2017-12-21
"""
import argparse
import asyncio
import datetime
import decimal
import functools
import logging
import os
import random
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
from cmd import Cmd
from collections import defaultdict

import APIs.common_APIs as common_APIs
import connections.my_socket as my_socket
from APIs.common_APIs import (my_system, my_system_full_output,
                              my_system_no_check, protocol_data_printB)
from basic.cprint import cprint
from basic.log_tool import MyLogger
from basic.async_task import AsyncBase




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
        sys.exit()


def sys_init():
    # sys log init
    global LOG
    LOG = MyLogger(os.path.abspath(sys.argv[0]).replace(
        'py', 'log'), clevel=logging.DEBUG, renable=False)
    global cprint
    cprint = cprint(os.path.abspath(sys.argv[0]).replace('py', 'log'))

    # cmd arg init
    global arg_handle
    arg_handle = ArgHandle()
    arg_handle.run()
    LOG.info("Let's go!!!")


def sys_cleanup():
    LOG.info("Goodbye!!!")


# sys start, should be modify by diff APP
def sys_run():

    def hello_word(s='1', s1='2', s2='3'):
        LOG.info("what is the fuck: %s, %s, %s" % (s, s1, s2))

    loop_obj = AsyncBase(logger=LOG)
    #loop_obj.add_func(loop_obj.get_func_obj(hello_word, 'your', s1='mum', s2='xxoo'), 5)
    cro1 = loop_obj.make_coroutine(hello_word, 'your', s1='mum', s2='xxoo1')
    cro2 = loop_obj.make_coroutine(hello_word, 'your', s1='mum', s2='xxoo2')
    cro3 = loop_obj.make_coroutine(hello_word, 'your', s1='mum', s2='xxoo3')


    loop_obj.task_proc_thread()

    LOG.warn("async task has already started!")

    loop_obj.add_func_to_thread(hello_word)
    loop_obj.add_coroutine_to_thread(cro1)
    loop_obj.add_coroutine_to_thread(cro2)
    loop_obj.add_coroutine_to_thread(cro3)


    time.sleep(999)

    loop_obj.timer(functools.partial(hello_word, 'xxoo', 'fuck you '), 5)


    if arg_handle.get_args('cmdloop'):
        # cmd loop
        signal.signal(signal.SIGINT, lambda signal,
                      frame: cprint.notice_p('Exit SYSTEM: exit'))
        my_cmd = MyCmd()
        my_cmd.cmdloop()
    else:
        pass


# 主程序入口
if __name__ == '__main__':
    sys_init()
    sys_run()
    sys_cleanup()
