#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""sim
by Kobe Gong. 2017-12-26
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
from protocol.wifi_protocol import Wifi

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
            choices={'air', 'hanger', 'waterfilter', 'airfilter', 'washer'},
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
        self.dev.sim_obj.status_show()

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


class BaseSim():
    status_lock = threading.Lock()

    def __init__(self, logger):
        self.LOG = logger
        self.wifi_obj = None

        # state data:
        self.task_obj = None

    @common_APIs.need_add_lock(status_lock)
    def set_item(self, item, value):
        self.__dict__[item] = value

    def run_forever(self):
        self.task_obj.add_task(
            'status maintain', self.status_maintain, 10000000, 60)
        self.task_obj.add_task('monitor event report',
                               self.monitor_event_report, 10000000, 1)
        return self.task_obj.task_proc()

    def status_maintain(self):
        pass

    def status_show(self):
        for item in sorted(self.__dict__):
            if item.startswith('_'):
                self.LOG.warn("%s: %s" % (item, str(self.__dict__[item])))

    def monitor_event_report(self):
        need_send_report = False
        if not hasattr(self, 'old_status'):
            self.old_status = defaultdict(lambda: {})
            for item in self.__dict__:
                if item.startswith('_'):
                    self.LOG.yinfo("need check item: %s" % (item))
                    self.old_status[item] = copy.deepcopy(self.__dict__[item])

        for item in self.old_status:
            if self.old_status[item] != self.__dict__[item]:
                need_send_report = True
                self.old_status[item] = copy.deepcopy(self.__dict__[item])

        if need_send_report:
            self.send_event_report()

    def send_event_report(self):
        return self.wifi_obj.add_send_data(self.wifi_obj.msg_build(self.get_event_report()))


class AirSim(BaseSim):
    def __init__(self, logger):
        self.LOG = logger
        self.wifi_obj = None

        # state data:
        self.task_obj = Task('AirSim-task', self.LOG)
        self._switchStatus = 'off'
        self._temperature = 16
        self._mode = "cold"
        self._speed = "low"
        self._wind_up_down = 'off'
        self._wind_left_right = 'off'

    def get_event_report(self):
        report_msg = {
            "method": "report",
            "attribute": {
                "switchStatus": self._switchStatus,
                "temperature": self._temperature,
                "mode": self._mode,
                "speed": self._speed,
                "wind_up_down": self._wind_up_down,
                "wind_left_right": self._wind_left_right
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
                        "switchStatus": self._switchStatus,
                        "temperature": self._temperature,
                        "mode": self._mode,
                        "speed": self._speed,
                        "wind_up_down": self._wind_up_down,
                        "wind_left_right": self._wind_left_right
                    }
                }
                return [json.dumps(rsp_msg)]
            if msg['nodeid'] == u"airconditioner.main.all_properties":
                self.LOG.warn("获取所有属性".decode('utf-8').encode(coding))
                rsp_msg = {
                    "method": "dm_get",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0,
                    "attribute": {
                        "switchStatus": self._switchStatus,
                        "temperature": self._temperature,
                        "mode": self._mode,
                        "speed": self._speed,
                        "wind_up_down": self._wind_up_down,
                        "wind_left_right": self._wind_left_right
                    }
                }
                return [json.dumps(rsp_msg)]
            else:
                self.LOG.warn('TODO in the feature!')

        elif msg['method'] == 'dm_set':
            if msg['nodeid'] == u"airconditioner.main.switch":
                self.LOG.warn(
                    ("开关机: %s" % (msg['params']["attribute"]["switch"])).decode('utf-8').encode(coding))
                self.set_item('_switchStatus',
                              msg['params']["attribute"]["switch"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            elif msg['nodeid'] == u"airconditioner.main.mode":
                self.LOG.warn(
                    ("设置模式: %s" % (msg['params']["attribute"]["mode"])).decode('utf-8').encode(coding))
                self.set_item('_mode', msg['params']["attribute"]["mode"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            elif msg['nodeid'] == u"airconditioner.main.temperature":
                self.LOG.warn(
                    ("设置温度: %s" % (msg['params']["attribute"]["temperature"])).decode('utf-8').encode(coding))
                self.set_item('_temperature',
                              msg['params']["attribute"]["temperature"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            elif msg['nodeid'] == u"airconditioner.main.speed":
                self.LOG.warn(
                    ("设置风速: %s" % (msg['params']["attribute"]["speed"])).decode('utf-8').encode(coding))
                self.set_item('_speed', msg['params']["attribute"]["speed"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            elif msg['nodeid'] == u"airconditioner.main.wind_up_down":
                self.LOG.warn(
                    ("设置上下摆风: %s" % (msg['params']["attribute"]["wind_up_down"])).decode('utf-8').encode(coding))
                self.set_item('_wind_up_down',
                              msg['params']["attribute"]["wind_up_down"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            elif msg['nodeid'] == u"airconditioner.main.wind_left_right":
                self.LOG.warn(
                    ("设置左右摆风: %s" % (msg['params']["attribute"]["wind_left_right"])).decode('utf-8').encode(coding))
                self.set_item('_wind_left_right',
                              msg['params']["attribute"]["wind_left_right"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            else:
                self.LOG.warn('TODO in the feature!')
        else:
            self.LOG.warn('TODO in the feature!')


class HangerSim(BaseSim):
    def __init__(self, logger):
        self.LOG = logger
        self.wifi_obj = None

        # state data:
        self.task_obj = Task('HangerSim-task', self.LOG)
        self._status = 'pause'
        self._light = "off"
        self._sterilization = "off"
        self._sterilization_duration = 20
        self._sterilization_remain = 20
        self._drying = "off"
        self._drying_duration = 120
        self._drying_remain = 120
        self._air_drying = 'off'
        self._air_drying_duration = 120
        self._air_drying_remain = 120

    def status_maintain(self):
        need_send_report = False
        if self._sterilization == 'on':
            need_send_report = True
            if self._sterilization_remain > 0:
                self.set_item('_sterilization_remain',
                              self._sterilization_remain - 1)
                if self._sterilization_remain <= 0:
                    self.set_item('_sterilization', 'off')
            else:
                self.set_item('_sterilization', 'off')

        if self._drying == 'on':
            need_send_report = True
            if self._drying_remain > 0:
                self.set_item('_drying_remain', self._drying_remain - 1)
                if self._drying_remain <= 0:
                    self.set_item('_drying', 'off')
            else:
                self.set_item('_drying', 'off')

        if self._air_drying == 'on':
            need_send_report = True
            if self._air_drying_remain > 0:
                self.set_item('_air_drying_remain',
                              self._air_drying_remain - 1)
                if self._air_drying_remain <= 0:
                    self.set_item('_air_drying', 'off')
            else:
                self.set_item('_air_drying', 'off')

        if need_send_report:
            # self.send_event_report()
            pass

    def get_event_report(self):
        report_msg = {
            "method": "report",
            "attribute": {
                "light": self._light,
                "sterilization": self._sterilization,
                "drying": self._drying,
                "air_drying": self._air_drying,
                "status": self._status,
                "sterilization_duration": self._sterilization_duration,
                "air_drying_duration": self._air_drying_duration,
                "drying_duration": self._drying_duration,
                "sterilization_remain": self._sterilization_remain,
                "air_drying_remain": self._air_drying_remain,
                "drying_remain": self._drying_remain
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
                        "light": self._light,
                        "sterilization": self._sterilization,
                        "drying": self._drying,
                        "air_drying": self._air_drying,
                        "status": self._status,
                        "sterilization_duration": self._sterilization_duration,
                        "air_drying_duration": self._air_drying_duration,
                        "drying_duration": self._drying_duration,
                        "sterilization_remain": self._sterilization_remain,
                        "air_drying_remain": self._air_drying_remain,
                        "drying_remain": self._drying_remain
                    }
                }
                return [json.dumps(rsp_msg)]
            else:
                self.LOG.warn('TODO in the feature!')

        elif msg['method'] == 'dm_set':
            if msg['nodeid'] == u"clothes_hanger.main.control":
                self.LOG.warn(
                    ("设置上下控制: %s" % (msg['params']["attribute"]["control"])).decode('utf-8').encode(coding))
                self.set_item('_status', msg['params']["attribute"]["control"])

                if self._status == 'up':
                    self.task_obj.add_task(
                        'change_status_top', self.set_item, 1, 10, '_status', 'top')

                elif self._status == 'down':
                    self.task_obj.add_task(
                        'change_status_bottom', self.set_item, 1, 10, '_status', 'bottom')

                elif self._status == 'pause':
                    self.task_obj.del_task('change_status_top')
                    self.task_obj.del_task('change_status_bottom')

                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            elif msg['nodeid'] == u"clothes_hanger.main.light":
                self.LOG.warn(
                    ("设置照明: %s" % (msg['params']["attribute"]["light"])).decode('utf-8').encode(coding))
                self.set_item('_light', msg['params']["attribute"]["light"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            elif msg['nodeid'] == u"clothes_hanger.main.sterilization":
                self.LOG.warn(
                    ("设置杀菌: %s" % (msg['params']["attribute"]["sterilization"])).decode('utf-8').encode(coding))
                self.set_item('_sterilization',
                              msg['params']["attribute"]["sterilization"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            elif msg['nodeid'] == u"clothes_hanger.main.sterilization_duration":
                self.LOG.warn(
                    ("设置杀菌时间: %s" % (msg['params']["attribute"]["sterilization_duration"])).decode('utf-8').encode(coding))
                self.set_item('_sterilization_duration',
                              msg['params']["attribute"]["sterilization_duration"])
                self.set_item('_sterilization_remain',
                              self._sterilization_duration)
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            elif msg['nodeid'] == u"clothes_hanger.main.drying":
                self.LOG.warn(
                    ("设置烘干: %s" % (msg['params']["attribute"]["drying"])).decode('utf-8').encode(coding))
                self.set_item('_drying', msg['params']["attribute"]["drying"])
                if self._drying == 'on':
                    self.set_item('_air_drying', 'off')
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            elif msg['nodeid'] == u"clothes_hanger.main.drying_duration":
                self.LOG.warn(
                    ("设置烘干时间: %s" % (msg['params']["attribute"]["drying_duration"])).decode('utf-8').encode(coding))
                self.set_item('_drying_duration',
                              msg['params']["attribute"]["drying_duration"])
                self.set_item('_drying_remain', self._drying_duration)
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            elif msg['nodeid'] == u"clothes_hanger.main.air_drying":
                self.LOG.warn(
                    ("设置风干: %s" % (msg['params']["attribute"]["air_drying"])).decode('utf-8').encode(coding))
                self.set_item(
                    '_air_drying', msg['params']["attribute"]["air_drying"])

                if self._air_drying == 'on':
                    self.set_item('_drying', 'off')
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            elif msg['nodeid'] == u"clothes_hanger.main.air_drying_duration":
                self.LOG.warn(
                    ("设置风干时间: %s" % (msg['params']["attribute"]["air_drying_duration"])).decode('utf-8').encode(coding))
                self.set_item('_air_drying_duration',
                              msg['params']["attribute"]["air_drying_duration"])
                self.set_item('_air_drying_remain', self._air_drying_duration)
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            else:
                self.LOG.warn('TODO in the feature!')
        else:
            self.LOG.warn('TODO in the feature!')


class WaterFilter(BaseSim):
    def __init__(self, logger):
        self.LOG = logger
        self.wifi_obj = None

        # state data:
        self.task_obj = Task('WaterFilter-task', self.LOG)
        self._filter_result = {
            "TDS": [
                500,
                100
            ]
        }
        self._status = 'filter'
        self._water_leakage = "off"
        self._water_shortage = "off"
        self._filter_time_used = {
            1: 101,
            2: 202,
        }
        self._filter_time_remaining = {
            1: 1899,
            2: 1798,
        }

    def reset_filter_time(self, id):
        if int(id) in self._filter_time_used:
            self._filter_time_used[int(id)] = 0
            self._filter_time_remaining[int(id)] = 2000
            return True
        else:
            self.LOG.error('Unknow ID: %s' % (id))
            return False

    def get_filter_time_used(self):
        filter_time_used_list = []
        for id in sorted(self._filter_time_used):
            filter_time_used_list.append(self._filter_time_used[id])
        return filter_time_used_list

    def get_filter_time_remaining(self):
        filter_time_remaining_list = []
        for id in sorted(self._filter_time_remaining):
            filter_time_remaining_list.append(self._filter_time_remaining[id])
        return filter_time_remaining_list

    def get_event_report(self):
        report_msg = {
            "method": "report",
            "attribute": {
                "filter_result": self._filter_result,
                "status": self._status,
                "water_leakage": self._water_leakage,
                "water_shortage": self._water_shortage,
                "filter_time_used": self.get_filter_time_used(),
                "filter_time_remaining": self.get_filter_time_remaining()
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
                        "filter_result": self._filter_result,
                        "status": self._status,
                        "water_leakage": self._water_leakage,
                        "water_shortage": self._water_shortage,
                        "filter_time_used": self.get_filter_time_used(),
                        "filter_time_remaining": self.get_filter_time_remaining()
                    }
                }
                return [json.dumps(rsp_msg)]
            else:
                self.LOG.warn('TODO in the feature!')

        elif msg['method'] == 'dm_set':
            if msg['nodeid'] == u"water_filter.main.control":
                self.LOG.warn(
                    ("设置冲洗: %s" % (msg['params']["attribute"]["control"])).decode('utf-8').encode(coding))
                self.set_item('_status', msg['params']["attribute"]["control"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                self.task_obj.add_task(
                    'change WaterFilter to filter', self.set_item, 1, 30, '_status', 'filter')
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"water_filter.main.reset_filter":
                self.LOG.warn(
                    ("复位滤芯: %s" % (msg['params']["attribute"]["reset_filter"])).decode('utf-8').encode(coding))
                filter_ids = msg['params']["attribute"]["reset_filter"]
                if 0 in filter_ids:
                    filter_ids = self.filter_time_used.keys()
                for filter_id in filter_ids:
                    self.reset_filter_time(filter_id)
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]
            else:
                self.LOG.warn('TODO in the feature!')

        else:
            self.LOG.warn('TODO in the feature!')


class AirFilter(BaseSim):
    def __init__(self, logger):
        self.LOG = logger
        self.wifi_obj = None

        # state data:
        self.task_obj = Task('AirFilter-task', self.LOG)
        self._air_filter_result = {
            "air_quality": [
                "low",
                "high"
            ],
            "PM25": [
                500,
                100
            ]
        }
        self._switch_status = 'off'
        self._child_lock_switch_status = "off"
        self._negative_ion_switch_status = "off"
        self._speed = "low"
        self._control_status = 'auto'
        self._filter_time_used = '101'
        self._filter_time_remaining = '1899'

    def get_event_report(self):
        report_msg = {
            "method": "report",
            "attribute": {
                "air_filter_result": self._air_filter_result,
                "switch_status": self._switch_status,
                "child_lock_switch_status": self._child_lock_switch_status,
                "negative_ion_switch_status": self._negative_ion_switch_status,
                "speed": self._speed,
                "control_status": self._control_status,
                "filter_time_used": self._filter_time_used,
                "filter_time_remaining": self._filter_time_remaining
            }
        }
        return json.dumps(report_msg)

    def protocol_handler(self, msg):
        coding = sys.getfilesystemencoding()
        if msg['method'] == 'dm_get':
            if msg['nodeid'] == u"air_filter.main.all_properties":
                self.LOG.warn("获取所有属性".decode('utf-8').encode(coding))
                rsp_msg = {
                    "method": "dm_get",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0,
                    "attribute": {
                        "air_filter_result": self._air_filter_result,
                        "switch_status": self._switch_status,
                        "child_lock_switch_status": self._child_lock_switch_status,
                        "negative_ion_switch_status": self._negative_ion_switch_status,
                        "speed": self._speed,
                        "control_status": self._control_status,
                        "filter_time_used": self._filter_time_used,
                        "filter_time_remaining": self._filter_time_remaining
                    }
                }
                return [json.dumps(rsp_msg)]
            else:
                self.LOG.warn('TODO in the feature!')

        elif msg['method'] == 'dm_set':
            if msg['nodeid'] == u"air_filter.main.switch":
                self.LOG.warn(
                    ("开关机: %s" % (msg['params']["attribute"]["switch"])).decode('utf-8').encode(coding))
                self.set_item('_switch_status',
                              msg['params']["attribute"]["switch"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"air_filter.main.child_lock_switch":
                self.LOG.warn(
                    ("童锁开关: %s" % (msg['params']["attribute"]["child_lock_switch"])).decode('utf-8').encode(coding))
                self.set_item('_child_lock_switch_status',
                              msg['params']["attribute"]["child_lock_switch"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"air_filter.main.negative_ion_switch":
                self.LOG.warn(
                    ("负离子开关: %s" % (msg['params']["attribute"]["negative_ion_switch"])).decode('utf-8').encode(coding))
                self.set_item('_negative_ion_switch_status',
                              msg['params']["attribute"]["negative_ion_switch"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"air_filter.main.control":
                self.LOG.warn(
                    ("设置模式切换: %s" % (msg['params']["attribute"]["control"])).decode('utf-8').encode(coding))
                self.set_item('_control_status',
                              msg['params']["attribute"]["control"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"air_filter.main.speed":
                self.LOG.warn(
                    ("设置风量调节: %s" % (msg['params']["attribute"]["speed"])).decode('utf-8').encode(coding))
                self.set_item('_speed', msg['params']["attribute"]["speed"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            else:
                self.LOG.warn('TODO in the feature!')

        else:
            self.LOG.warn('TODO in the feature!')


class Washer(BaseSim):
    def __init__(self, logger):
        self.LOG = logger
        self.wifi_obj = None

        # state data:
        self.task_obj = Task('Washer-task', self.LOG)
        self._status = 'halt'
        self._auto_detergent_switch = 'off'
        self._child_lock_switch_status = "off"
        self._add_laundry_switch = "off"
        self._sterilization = "off"
        self._spin = 0
        self._temperature = 28
        self._reserve_wash = 24
        self._mode = 'mix'
        self._time_left = 10

    def status_maintain(self):
        need_send_report = False
        if self._status == 'start':
            need_send_report = True
            if self._time_left > 0:
                self.set_item('_time_left',
                              self._time_left - 1)
                if self._time_left <= 0:
                    self.set_item('_status', 'halt')
            else:
                self.set_item('_status', 'halt')

        if need_send_report:
            # return self.send_event_report()
            pass

    def get_event_report(self):
        report_msg = {
            "method": "report",
            "attribute": {
                "child_lock_switch": self._child_lock_switch_status,
                "auto_detergent_switch": self._auto_detergent_switch,
                "add_laundry_switch": self._add_laundry_switch,
                "sterilization": self._sterilization,
                "spin": self._spin,
                "temperature": self._temperature,
                "reserve_wash": self._reserve_wash,
                "mode": self._mode,
                "status": self._status,
                "time_left": self._time_left
            }
        }
        return json.dumps(report_msg)

    def protocol_handler(self, msg):
        coding = sys.getfilesystemencoding()
        if msg['method'] == 'dm_get':
            if msg['nodeid'] == u"wash_machine.main.all_properties":
                self.LOG.warn("获取所有属性".decode('utf-8').encode(coding))
                rsp_msg = {
                    "method": "dm_get",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0,
                    "attribute": {
                        "child_lock_switch": self._child_lock_switch_status,
                        "auto_detergent_switch": self._auto_detergent_switch,
                        "add_laundry_switch": self._add_laundry_switch,
                        "sterilization": self._sterilization,
                        "spin": self._spin,
                        "temperature": self._temperature,
                        "reserve_wash": self._reserve_wash,
                        "mode": self._mode,
                        "status": self._status,
                        "time_left": self._time_left
                    }
                }
                return [json.dumps(rsp_msg)]
            else:
                self.LOG.warn('TODO in the feature!')

        elif msg['method'] == 'dm_set':
            if msg['nodeid'] == u"wash_machine.main.control":
                self.LOG.warn(
                    ("启动暂停: %s" % (msg['params']["attribute"]["control"])).decode('utf-8').encode(coding))
                self.set_item('_status', msg['params']["attribute"]["control"])
                self.set_item('_time_left', 10)
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"wash_machine.main.child_lock_switch":
                self.LOG.warn(
                    ("童锁开关: %s" % (msg['params']["attribute"]["child_lock_switch"])).decode('utf-8').encode(coding))
                self.set_item('_child_lock_switch_status',
                              msg['params']["attribute"]["child_lock_switch"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"wash_machine.main.auto_detergent_switch":
                self.LOG.warn(
                    ("设置智能投放: %s" % (msg['params']["attribute"]["auto_detergent_switch"])).decode('utf-8').encode(coding))
                self.set_item('_auto_detergent_switch',
                              msg['params']["attribute"]["auto_detergent_switch"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"wash_machine.main.add_laundry_switch":
                self.LOG.warn(
                    ("设置中途添衣: %s" % (msg['params']["attribute"]["add_laundry_switch"])).decode('utf-8').encode(coding))
                self.set_item('_add_laundry_switch',
                              msg['params']["attribute"]["add_laundry_switch"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"wash_machine.main.sterilization":
                self.LOG.warn(
                    ("一键除菌: %s" % (msg['params']["attribute"]["sterilization"])).decode('utf-8').encode(coding))
                self.set_item('_sterilization',
                              msg['params']["attribute"]["sterilization"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"wash_machine.main.mode":
                self.LOG.warn(
                    ("设置模式: %s" % (msg['params']["attribute"]["mode"])).decode('utf-8').encode(coding))
                self.set_item('_mode', msg['params']["attribute"]["mode"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"wash_machine.main.spin":
                self.LOG.warn(
                    ("设置脱水: %s" % (msg['params']["attribute"]["spin"])).decode('utf-8').encode(coding))
                self.set_item('_spin', msg['params']["attribute"]["spin"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"wash_machine.main.temperature":
                self.LOG.warn(
                    ("设置温度: %s" % (msg['params']["attribute"]["temperature"])).decode('utf-8').encode(coding))
                self.set_item('_temperature',
                              msg['params']["attribute"]["temperature"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            elif msg['nodeid'] == u"wash_machine.main.reserve_wash":
                self.LOG.warn(
                    ("设置预约功能: %s" % (msg['params']["attribute"]["reserve_wash"])).decode('utf-8').encode(coding))
                self.set_item('_reserve_wash',
                              msg['params']["attribute"]["reserve_wash"])
                rsp_msg = {
                    "method": "dm_set",
                    "req_id": msg['req_id'],
                    "msg": "success",
                    "code": 0
                }
                return [json.dumps(rsp_msg)]

            else:
                self.LOG.warn('TODO in the feature!')

        else:
            self.LOG.warn('TODO in the feature!')


if __name__ == '__main__':
    LOG = MyLogger(os.path.abspath(sys.argv[0]).replace('py', 'log'), clevel=logging.INFO,
                   rlevel=logging.WARN)
    cprint = cprint(__name__)

    sys_init()

    arg_handle = ArgHandle()
    arg_handle.run()

    global thread_list
    thread_list = []

    if arg_handle.get_args('device_type') == 'air':
        sim = AirSim(logger=LOG)
        deviceCategory = 'airconditioner.new'
    elif arg_handle.get_args('device_type') == 'hanger':
        sim = HangerSim(logger=LOG)
        deviceCategory = 'clothes_hanger.main'
    elif arg_handle.get_args('device_type') == 'waterfilter':
        sim = WaterFilter(logger=LOG)
        deviceCategory = 'water_filter.main'
    elif arg_handle.get_args('device_type') == 'airfilter':
        sim = AirFilter(logger=LOG)
        deviceCategory = 'air_filter.main'
    elif arg_handle.get_args('device_type') == 'washer':
        sim = Washer(logger=LOG)
        deviceCategory = 'wash_machine.main'
    wifi = Wifi(('192.168.10.1', 65381), logger=LOG,
                sim_obj=sim, time_delay=arg_handle.get_args('time_delay'), mac=arg_handle.get_args('mac'), deviceCategory=deviceCategory)
    thread_list.append([wifi.schedule_loop])
    thread_list.append([wifi.send_data_loop])
    thread_list.append([wifi.recv_data_loop])
    thread_list.append([wifi.heartbeat_loop])
    thread_list.append([sim.run_forever])

    sys_proc()

    if arg_handle.get_args('debug'):
        dmsg = {
            "method": "dm_set",
            "req_id": 178237278,
            "nodeid": "water_filter.main.control",
            "params": {
                "attribute": {
                    "control": "clean"
                }
            }
        }

        dmsg = {
            "method": "dm_set",
            "req_id": 178237278,
            "nodeid": "clothes_hanger.main.sterilization",
            "params": {
                "attribute": {
                    "sterilization": "on",
                }
            }
        }
        time.sleep(1)
        sim.wifi_obj.queue_in.put(
            b'\x77\x56\x43\xaa' + struct.pack('>H', len(json.dumps(dmsg)) + 2) + b'\x03' + json.dumps(dmsg) + b'\x00')

    if True:
        signal.signal(signal.SIGINT, lambda signal,
                      frame: cprint.notice_p('Exit SYSTEM: exit'))
        my_cmd = MyCmd(logger=LOG, dev=wifi)
        my_cmd.cmdloop()

    else:
        sys_join()
        sys_cleanup()
        sys.exit()
