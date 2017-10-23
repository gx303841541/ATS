#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""air app sim
by Kobe Gong. 2017-10-16
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
import Queue
import json

from collections import defaultdict

from basic.log_tool import MyLogger
from basic.cprint import cprint
import APIs.common_APIs as common_APIs
from APIs.common_APIs import my_system_no_check, my_system, my_system_full_output, protocol_data_printB
from protocol.air_control_sim import AirControl
from protocol.protocol_process import PProcess
import my_socket.my_socket as my_socket

# 命令行参数梳理，-t time interval; -u uuid
class ArgHandle():
    def __init__(self):
        self.parser = self.build_option_parser("-" * 50)

    def build_option_parser(self, description):
        parser = argparse.ArgumentParser(description=description)

        parser.add_argument(
            '-t', '--time-interval',
            dest='time_interval',
            action='store',
            default=200,
            type=int,
            help='time intervavl for msg send to router',
        )

        parser.add_argument(
            '-u', '--device-uuid',
            dest='device_uuid',
            action='store',
            default='000e83c6c10000000000c85b765caf43',
            help='Specify device uuid',
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
        cprint.notice_p("show all msgs info!")

    def do_sts(self, arg, opts=None):
        pass

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


def getMsgup(req_id, uuid):
    msg_temp_up={
        "uuid": "111",
        "encry": "false",
        "content": {
            "method":"dm_set",
            "req_id":113468,
            "token":"",
            "nodeid": "airconditioner.main.temperature",
            "params":{
                "device_uuid":"",
                "attribute":{
                    "temperature":26
                }
            }
        }
    }
    msg_temp_up['content']['req_id'] = req_id
    msg_temp_up['content']['params']['device_uuid'] = uuid
    return str(json.dumps(msg_temp_up)) + '\n'

def getMsgdown(req_id, uuid):
    msg_temp_down={
        "uuid": "111",
        "encry": "false",
        "content": {
            "method":"dm_set",
            "req_id":113468,
            "token":"",
            "nodeid": "airconditioner.main.temperature",
            "params":{
                "device_uuid":"",
                "attribute":{
                    "temperature":27
                }
            }
        }
    }
    msg_temp_down['content']['req_id'] = req_id
    msg_temp_down['content']['params']['device_uuid'] = uuid
    return str(json.dumps(msg_temp_down)) + '\n'



# 空调遥控器模拟程序入口
if __name__ == '__main__':
    # sys log init
    LOG = MyLogger(os.path.abspath(sys.argv[0]).replace('py', 'log'), clevel=logging.DEBUG, renable=False)

    cprint = cprint(os.path.abspath(sys.argv[0]).replace('py', 'log'))

    # cmd arg init
    arg_handle = ArgHandle()
    arg_handle.run()

    # sys init
    sys_init()

    # multi thread
    global thread_list
    thread_list = []



    queue_in, queue_out = Queue.Queue(), Queue.Queue()
    client = my_socket.MyClient(('192.168.10.1', 5100), LOG, queue_in, queue_out, singlethread=False)
    thread_list.append([client.run_forever])
    thread_list.append([client.sendloop])


    air_control = AirControl(queue_in=queue_in, queue_out=queue_out, logger=LOG)
    pp = PProcess({'onlyone': air_control}, LOG)
    thread_list.append([pp.run_forever])


    # run threads
    sys_proc()


    try:
        while True:
            while client.connected != True:
                pass
            req_id = random.randint(100, 9999999)
            msg = getMsgup(req_id, arg_handle.get_args('device_uuid'))
            air_control.msgst[req_id]['send_time'] = datetime.datetime.now()
            air_control.queue_out.put(msg)
            LOG.info("send: " + msg.strip())
            time.sleep(arg_handle.get_args('time_interval') / 1000.0)

            req_id += 1
            msg = getMsgdown(req_id, arg_handle.get_args('device_uuid'))
            air_control.msgst[req_id]['send_time'] = datetime.datetime.now()
            air_control.queue_out.put(msg)
            LOG.info("send: " + msg.strip())
            time.sleep(arg_handle.get_args('time_interval') / 1000.0)


    except KeyboardInterrupt:
        LOG.info('KeyboardInterrupt!')
        sys.exit()

    except Exception as e:
        LOG.error('something wrong!' + str(e))
        sys.exit()
