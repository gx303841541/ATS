#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""sim
by Kobe Gong. 2018-1-15
"""


import argparse
import copy
import datetime
import decimal
import json
import logging
import os
import random
import re
import shutil
import signal
import struct
import subprocess
import sys
import threading
import time
from cmd import Cmd
from collections import defaultdict

import APIs.common_APIs as common_APIs
from APIs.common_APIs import (my_system, my_system_full_output,
                              my_system_no_check, protocol_data_printB)
from basic.cprint import cprint
from basic.log_tool import MyLogger
from basic.task import Task
from protocol.devices import Door
from protocol.light_protocol import SDK

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')


class ArgHandle():
    def __init__(self):
        self.parser = self.build_option_parser("-" * 50)

    def build_option_parser(self, description):
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            '-d', '--debug',
            dest='debug',
            action='store_true',
            help='debug switch',
        )
        parser.add_argument(
            '-t', '--time-delay',
            dest='time_delay',
            action='store',
            default=500,
            type=int,
            help='time delay(ms) for msg send to router, default time is 500(ms)',
        )
        parser.add_argument(
            '--device',
            dest='device_type',
            action='store',
            choices={'door', 'elevator'},
            default='air',
            help='Specify device type',
        )
        parser.add_argument(
            '-p', '--server-port',
            dest='server_port',
            action='store',
            default=20001,
            type=int,
            help='Specify TCP server port',
        )
        parser.add_argument(
            '-i', '--server-IP',
            dest='server_IP',
            action='store',
            default='192.168.10.12',
            help='Specify TCP server IP address',
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
    def __init__(self, logger, sdk_obj=None, sim_obj=None):
        Cmd.__init__(self)
        self.prompt = "SIM>"
        self.sdk_obj = sdk_obj
        self.sim_obj = sim_obj
        self.LOG = logger

    def help_log(self):
        cprint.notice_p(
            "change logger level: log {0:critical, 1:error, 2:warning, 3:info, 4:debug}")

    def do_log(self, arg, opts=None):
        level = {
            '0': logging.CRITICAL,
            '1': logging.ERROR,
            '2': logging.WARNING,
            '3': logging.INFO,
            '4': logging.DEBUG,
        }
        if int(arg) in range(5):
            self.LOG.set_level(level[arg])
        else:
            cprint.warn_p("unknow log level: %s!" % (arg))

    def help_st(self):
        cprint.notice_p("show state")

    def do_st(self, arg, opts=None):
        self.sim_obj.status_show()

    def help_set(self):
        cprint.notice_p("show state")

    def do_set(self, arg, opts=None):
        args = arg.split()
        self.sim_obj.set_item(args[0], args[1])

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


def sys_init():
    LOG.info("Let's go!!!")


def sys_cleanup():
    LOG.info("Goodbye!!!")


if __name__ == '__main__':
    LOG = MyLogger(os.path.abspath(sys.argv[0]).replace('py', 'log'), clevel=logging.DEBUG,
                   rlevel=logging.WARN)
    cprint = cprint(__name__)

    sys_init()

    arg_handle = ArgHandle()
    arg_handle.run()

    global thread_list
    thread_list = []

    sdk = SDK((arg_handle.get_args('server_IP'), arg_handle.get_args('server_port')), logger=LOG,
              time_delay=arg_handle.get_args('time_delay'))
    sim = Door(logger=LOG, sdk_obj=sdk)
    thread_list.append([sdk.schedule_loop])
    thread_list.append([sdk.send_data_loop])
    thread_list.append([sdk.recv_data_loop])
    thread_list.append([sdk.heartbeat_loop])
    thread_list.append([sim.run_forever])

    sys_proc()

    if arg_handle.get_args('debug'):
        dmsg = b'\x48\x44\x58\x4d\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30\x31\x30\x30\x34\x32\x30\x31\x36\x35\x38\x46\x43\x44\x42\x44\x38\x33\x34\x31\x45\x01\x00\x00\x00\x01\x00\x00\x00\x29\x00\x00\x8f\x20\x7b\x22\x72\x65\x73\x75\x6c\x74\x22\x3a\x30\x2c\x22\x63\x6f\x6d\x6d\x61\x6e\x64\x22\x3a\x22\x43\x4f\x4d\x5f\x44\x45\x56\x5f\x52\x45\x47\x49\x53\x54\x45\x52\x22\x7d'
        time.sleep(1)
        sim.sdk_obj.queue_in.put(dmsg)

    if True:
        signal.signal(signal.SIGINT, lambda signal,
                      frame: cprint.notice_p('Exit SYSTEM: exit'))
        my_cmd = MyCmd(logger=LOG, sdk_obj=sdk, sim_obj=sim)
        my_cmd.cmdloop()

    else:
        sys_join()
        sys_cleanup()
        sys.exit()
