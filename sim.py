#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""sim
by Kobe Gong. 2017-12-26
"""

import argparse
import datetime
import decimal
import json
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
from APIs.common_APIs import (my_system, my_system_full_output,
                              my_system_no_check, protocol_data_printB)
from basic.cprint import cprint
from basic.log_tool import MyLogger
from protocol.wifi_protocol import Wifi


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
            '-m', '--mac',
            dest='mac',
            action='store',
            default='123456',
            help='Specify wifi module mac address',
        )
        parser.add_argument(
            '--device',
            dest='device_type',
            action='store',
            choices={'air', 'hanger', 'water'},
            default='air',
            help='Specify device type',
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
    def __init__(self, logger, dev):
        Cmd.__init__(self)
        self.prompt = "SIM>"
        self.dev = dev
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
        self.dev.sim_obj.show_state()

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


class AirSim():
    def __init__(self, logger):
        self.LOG = logger

        # state data:
        self.switchStatus = 'off'
        self.temperature = 16
        self.mode = "cold"
        self.speed = "low"
        self.wind_up_down = 'off'
        self.wind_left_right = 'off'

    def show_state(self):
        for item in self.__dict__:
            if item == 'LOG':
                continue
            self.LOG.warn("%s: %s" % (item, str(self.__dict__[item])))

    def get_event_report(self):
        report_msg = {
            "method": "report",
            "attribute": {
                "switchStatus": self.switchStatus,
                "temperature": self.temperature,
                "mode": self.mode,
                "speed": self.speed,
                "wind_up_down": self.wind_up_down,
                "wind_left_right": self.wind_left_right
            }
        }
        return json.dumps(report_msg)

    def protocol_handler(self, msg):
        coding = sys.getfilesystemencoding()
        if msg['method'] == 'dm_get':
            if msg['nodeid'] == u"airconditioner.new.all_properties":
                self.LOG.warn("获取所有属性".decode('utf-8').encode(coding))
                rsp_msg = {
                    "method": "dm_get",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0,
                    "attribute": {
                        "switchStatus": self.switchStatus,
                        "temperature": self.temperature,
                        "mode": self.mode,
                        "speed": self.speed,
                        "wind_up_down": self.wind_up_down,
                        "wind_left_right": self.wind_left_right
                    }
                }
                return [json.dumps(rsp_msg)]
            else:
                self.LOG.warn('TODO in the feature!')

        elif msg['method'] == 'dm_set':
            if msg['nodeid'] == u"airconditioner.main.switch":
                self.LOG.warn(
                    ("开关机: %s" % (msg['params']["attribute"]["switch"])).decode('utf-8').encode(coding))
                self.switchStatus = msg['params']["attribute"]["switch"]
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg), self.get_event_report()]
            elif msg['nodeid'] == u"airconditioner.main.mode":
                self.LOG.warn(
                    ("设置模式: %s" % (msg['params']["attribute"]["mode"])).decode('utf-8').encode(coding))
                self.mode = msg['params']["attribute"]["mode"]
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg), self.get_event_report()]
            elif msg['nodeid'] == u"airconditioner.main.temperature":
                self.LOG.warn(
                    ("设置温度: %s" % (msg['params']["attribute"]["temperature"])).decode('utf-8').encode(coding))
                self.temperature = msg['params']["attribute"]["temperature"]
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg), self.get_event_report()]
            elif msg['nodeid'] == u"airconditioner.main.speed":
                self.LOG.warn(
                    ("设置风速: %s" % (msg['params']["attribute"]["speed"])).decode('utf-8').encode(coding))
                self.speed = msg['params']["attribute"]["speed"]
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg), self.get_event_report()]
            elif msg['nodeid'] == u"airconditioner.main.wind_up_down":
                self.LOG.warn(
                    ("设置上下摆风: %s" % (msg['params']["attribute"]["wind_up_down"])).decode('utf-8').encode(coding))
                self.wind_up_down = msg['params']["attribute"]["wind_up_down"]
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg), self.get_event_report()]
            elif msg['nodeid'] == u"airconditioner.main.wind_left_right":
                self.LOG.warn(
                    ("设置左右摆风: %s" % (msg['params']["attribute"]["wind_left_right"])).decode('utf-8').encode(coding))
                self.wind_left_right = msg['params']["attribute"]["wind_left_right"]
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg), self.get_event_report()]
            else:
                self.LOG.warn('TODO in the feature!')
        else:
            self.LOG.warn('TODO in the feature!')


class HangerSim():
    def __init__(self, logger):
        self.LOG = logger

        # state data:
        self.status = 'pause'
        self.light = "off"
        self.sterilization = "off"
        self.drying = "off"
        self.air_drying = 'off'

    def show_state(self):
        for item in self.__dict__:
            if item == 'LOG':
                continue
            self.LOG.warn("%s: %s" % (item, str(self.__dict__[item])))

    def get_event_report(self):
        report_msg = {
            "method": "report",
            "attribute": {
                "light": self.light,
                "sterilization": self.sterilization,
                "drying": self.drying,
                "air_drying": self.air_drying,
                "status": self.status
            }
        }
        return json.dumps(report_msg)

    def protocol_handler(self, msg):
        coding = sys.getfilesystemencoding()
        if msg['method'] == 'dm_get':
            if msg['nodeid'] == u"clothes_hanger.main.all_properties":
                self.LOG.warn("获取所有属性".decode('utf-8').encode(coding))
                rsp_msg = {
                    "method": "dm_get",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0,
                    "attribute": {
                        "light": self.light,
                        "sterilization": self.sterilization,
                        "drying": self.drying,
                        "air_drying": self.air_drying,
                        "status": self.status
                    }
                }
                return [json.dumps(rsp_msg)]
            else:
                self.LOG.warn('TODO in the feature!')

        elif msg['method'] == 'dm_set':
            if msg['nodeid'] == u"clothes_hanger.main.control":
                self.LOG.warn(
                    ("设置上下控制: %s" % (msg['params']["attribute"]["control"])).decode('utf-8').encode(coding))
                self.status = msg['params']["attribute"]["control"]
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg), self.get_event_report()]
            elif msg['nodeid'] == u"clothes_hanger.main.light":
                self.LOG.warn(
                    ("设置照明: %s" % (msg['params']["attribute"]["light"])).decode('utf-8').encode(coding))
                self.light = msg['params']["attribute"]["light"]
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg), self.get_event_report()]
            elif msg['nodeid'] == u"clothes_hanger.main.sterilization":
                self.LOG.warn(
                    ("设置杀菌: %s" % (msg['params']["attribute"]["sterilization"])).decode('utf-8').encode(coding))
                self.sterilization = msg['params']["attribute"]["sterilization"]
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg), self.get_event_report()]
            elif msg['nodeid'] == u"clothes_hanger.main.drying":
                self.LOG.warn(
                    ("设置烘干: %s" % (msg['params']["attribute"]["drying"])).decode('utf-8').encode(coding))
                self.drying = msg['params']["attribute"]["drying"]
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg), self.get_event_report()]
            elif msg['nodeid'] == u"clothes_hanger.main.air_drying":
                self.LOG.warn(
                    ("设置风干: %s" % (msg['params']["attribute"]["air_drying"])).decode('utf-8').encode(coding))
                self.air_drying = msg['params']["attribute"]["air_drying"]
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg), self.get_event_report()]
            else:
                self.LOG.warn('TODO in the feature!')
        else:
            self.LOG.warn('TODO in the feature!')


class WaterFilter():
    def __init__(self, logger):
        self.LOG = logger

        # state data:
        self.filter_result = {
            "TDS": [
                500,
                100
            ]
        }
        self.status = 'filter'
        self.water_leakage = "off"
        self.water_shortage = "off"
        self.filter_time_used = "1000"
        self.filter_time_remaining = '300'

    def show_state(self):
        for item in self.__dict__:
            if item == 'LOG':
                continue
            self.LOG.warn("%s: %s" % (item, str(self.__dict__[item])))

    def get_event_report(self):
        report_msg = {
            "method": "report",
            "attribute": {
                "filter_result": self.filter_result,
                "status": self.status,
                "water_leakage": self.water_leakage,
                "water_shortage": self.water_shortage,
                "filter_time_used": self.filter_time_used,
                "filter_time_remaining": self.filter_time_remaining
            }
        }
        return json.dumps(report_msg)

    def protocol_handler(self, msg):
        coding = sys.getfilesystemencoding()
        if msg['method'] == 'dm_get':
            if msg['nodeid'] == u"water_filter.main.all_properties":
                self.LOG.warn("获取所有属性".decode('utf-8').encode(coding))
                rsp_msg = {
                    "method": "dm_get",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0,
                    "attribute": {
                        "filter_result": self.filter_result,
                        "status": self.status,
                        "water_leakage": self.water_leakage,
                        "water_shortage": self.water_shortage,
                        "filter_time_used": self.filter_time_used,
                        "filter_time_remaining": self.filter_time_remaining
                    }
                }
                return [json.dumps(rsp_msg)]
            else:
                self.LOG.warn('TODO in the feature!')

        elif msg['method'] == 'dm_set':
            if msg['nodeid'] == u"water_filter.main.control":
                self.LOG.warn(
                    ("设置冲洗: %s" % (msg['params']["attribute"]["control"])).decode('utf-8').encode(coding))
                self.status = msg['params']["attribute"]["control"]
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg), self.get_event_report()]
            else:
                self.LOG.warn('TODO in the feature!')

        else:
            self.LOG.warn('TODO in the feature!')


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

    # multi thread
    global thread_list
    thread_list = []

    if arg_handle.get_args('device_type') == 'air':
        sim = AirSim(logger=LOG)
        deviceCategory = 'airconditioner.new'
    elif arg_handle.get_args('device_type') == 'hanger':
        sim = HangerSim(logger=LOG)
        deviceCategory = 'clothes_hanger.main'
    elif arg_handle.get_args('device_type') == 'water':
        sim = WaterFilter(logger=LOG)
        deviceCategory = 'water_filter.main'
    wifi = Wifi(('192.168.10.1', 65381), logger=LOG,
                sim_obj=sim, mac=arg_handle.get_args('mac'), deviceCategory=deviceCategory)
    thread_list.append([wifi.schedule_loop])
    thread_list.append([wifi.send_data_loop])
    thread_list.append([wifi.recv_data_loop])
    thread_list.append([wifi.heartbeat_loop])

    # run threads
    sys_proc()

    if arg_handle.get_args('cmdloop') or True:
        # cmd loop
        signal.signal(signal.SIGINT, lambda signal,
                      frame: cprint.notice_p('Exit SYSTEM: exit'))
        my_cmd = MyCmd(logger=LOG, dev=wifi)
        my_cmd.cmdloop()

    else:
        sys_join()

        # sys clean
        sys_cleanup()
        sys.exit()
