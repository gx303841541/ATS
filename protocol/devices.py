#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""devices sim
by Kobe Gong. 2018-1-15
"""

import copy
import datetime
import decimal
import json
import logging
import os
import random
import re
import shutil
import struct
import sys
import threading
import time
from collections import defaultdict

import APIs.common_APIs as common_APIs
from basic.log_tool import MyLogger
from basic.task import Task
from protocol.light_protocol import SDK

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

coding = sys.getfilesystemencoding()


class BaseSim():
    status_lock = threading.Lock()

    def __init__(self, logger):
        self.LOG = logger
        self.sdk_obj = None

        # state data:
        self.task_obj = None

    @common_APIs.need_add_lock(status_lock)
    def set_item(self, item, value):
        if item in self.__dict__:
            self.__dict__[item] = value
        else:
            self.LOG.error("Unknow item: %s" % (item))

    def status_show(self):
        for item in sorted(self.__dict__):
            if item.startswith('_'):
                self.LOG.warn("%s: %s" % (item, str(self.__dict__[item])))

    def run_forever(self):
        self.task_obj.add_task(
            'status maintain', self.status_maintain, 10000000, 60)
        self.task_obj.add_task('monitor event report',
                               self.monitor_event_report, 10000000, 1)
        return self.task_obj.task_proc()

    def status_maintain(self):
        pass

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
            self.send_msg(self.get_event_report())

    def send_msg(self, msg):
        return self.sdk_obj.add_send_data(self.sdk_obj.msg_build(msg))


class AirSim(BaseSim):
    def __init__(self, logger):
        self.LOG = logger
        self.sdk_obj = None

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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
            else:
                self.LOG.warn('TODO in the feature!')
        else:
            self.LOG.warn('TODO in the feature!')


class HangerSim(BaseSim):
    def __init__(self, logger):
        self.LOG = logger
        self.sdk_obj = None

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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)
            else:
                self.LOG.warn('TODO in the feature!')
        else:
            self.LOG.warn('TODO in the feature!')


class WaterFilter(BaseSim):
    def __init__(self, logger):
        self.LOG = logger
        self.sdk_obj = None

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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)
            else:
                self.LOG.warn('TODO in the feature!')

        else:
            self.LOG.warn('TODO in the feature!')


class AirFilter(BaseSim):
    def __init__(self, logger):
        self.LOG = logger
        self.sdk_obj = None

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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)

            else:
                self.LOG.warn('TODO in the feature!')

        else:
            self.LOG.warn('TODO in the feature!')


class Washer(BaseSim):
    def __init__(self, logger):
        self.LOG = logger
        self.sdk_obj = None

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
                return json.dumps(rsp_msg)
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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)

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
                return json.dumps(rsp_msg)

            else:
                self.LOG.warn('TODO in the feature!')

        else:
            self.LOG.warn('TODO in the feature!')


class Door(BaseSim):
    def __init__(self, logger, sdk_obj, self_ip='192.168.10.1', deviceID="1001201600FF81992F49"):
        self.LOG = logger
        self.sdk_obj = sdk_obj
        self.sdk_obj.sim_obj = self
        self.sdk_obj.heartbeat_interval = 60
        self.sdk_obj.heartbeat_data = self.sdk_obj.msg_build(
            self.get_heartbeat_msg())

        # state data:
        self.task_obj = Task('Washer-task', self.LOG)
        self.dev_register = False
        self._type = 2016
        self._subDeviceType = 88
        self._deviceID = deviceID
        self._subDeviceID = deviceID
        self._name = b'dog door'
        self._manufacturer = b'HDIOT'
        self._ip = self_ip
        self._mac = b'00:FF:81:99:2F:49'
        self._mask = b'255.255.255.0'
        self._version = b'1.0.01'
        self._time = datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S').encode('utf-8')
        self._appVersionInfo = b'appVersionInfo.8.8.8'
        self._fileServerUrl = b'http://192.168.10.1/noexist'
        self._ntpServer = b'4.4.4.4'
        self._openDuration = 10
        self._current_openDuration = 10
        self._alarmTimeout = 20
        self._startTime = b'1988-08-08'
        self._endTime = datetime.datetime.now().strftime('%Y-%m-%d').encode('utf-8')
        self._UserType = b''
        self._userID = b''
        self._CredenceType = b''
        self._credenceNo = b'12345678'
        self._State = 0

    def run_forever(self):
        self.task_obj.add_task(
            'status maintain', self.status_maintain, 10000000, 1)

        self.task_obj.add_task('monitor event report',
                               self.monitor_record, 10000000, 1)

        self.task_obj.add_task(
            'dev register', self.to_register_dev, 10000000, 1)

        return self.task_obj.task_proc()

    def status_maintain(self):
        if self._State == 1 or self._State == '1':
            if self._current_openDuration > 0:
                self.set_item('_current_openDuration',
                              self._current_openDuration - 1)
                if self._current_openDuration <= 0:
                    self.set_item('_current_openDuration', self._openDuration)
                    self.set_item('_State', 0)
            else:
                self.set_item('_State', 0)

    def monitor_record(self):
        need_send_report = False
        if not hasattr(self, 'old_status'):
            self.old_status = defaultdict(lambda: {})
            for item in self.__dict__:
                if item == "_State":
                    self.LOG.yinfo("need check item: %s" % (item))
                    self.old_status[item] = copy.deepcopy(self.__dict__[item])

        for item in self.old_status:
            if self.old_status[item] != self.__dict__[item]:
                need_send_report = True
                self.old_status[item] = copy.deepcopy(self.__dict__[item])

        if need_send_report:
            self.LOG.warn("记录上传".decode('utf-8').encode(coding))
            self.send_msg(self.get_upload_record())

    def to_register_dev(self):
        if self.dev_register:
            self.LOG.debug("设备已经注册".decode('utf-8').encode(coding))
        else:
            self.LOG.debug("发送设备注册".decode('utf-8').encode(coding))
            self.send_msg(self.get_dev_register_msg())

    def get_dev_register_msg(self):
        report_msg = {
            "Command": "COM_DEV_REGISTER",
            "Data": [
                {
                    "Type": self._type,
                    "deviceID": self._deviceID,
                    "manufacturer": self._manufacturer,
                    "ip": self._ip,
                    "mac": self._mac,
                    "mask": self._mask,
                    "version": self._version,
                }
            ]
        }
        return json.dumps(report_msg)

    def get_upload_record(self):
        report_msg = {
            "Command": 'COM_UPLOAD_RECORD',
            "Data": [
                {
                    "deviceID": self._deviceID,
                    "recordTime": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode('utf-8'),
                    "RecordType": "FACE_OPEN_DOOR_RECORD",
                    "CredenceType": self._CredenceType,
                    "passType": random.randint(0, 1),
                }
            ]
        }
        return json.dumps(report_msg)

    def get_heartbeat_msg(self):
        report_msg = {
            "Command": "COM_HEARTBEAT",
        }
        return json.dumps(report_msg)

    def protocol_handler(self, msg, ack=False):
        coding = sys.getfilesystemencoding()
        if ack:
            if msg['Command'] == 'COM_DEV_REGISTER':
                self.LOG.warn("设备注册应答: ".decode('utf-8').encode(coding))
                self.dev_register = True
                return None
            else:
                self.LOG.warn('Unknow msg: %s!' % (msg['Command']))
                return None

        # 系统管理
        if msg['Command'] == 'COM_QUERY_DIR':
            self.LOG.warn("设备目录查询: ".decode('utf-8').encode(coding))
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
                "Data": [
                    {
                        "deviceID": self._deviceID,
                        "name": self._name,
                        "manufacturer": self._manufacturer,
                        "version": self._version,
                        "subDeviceType": self._subDeviceType
                    }
                ]
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_DEV_RESET':
            self.LOG.warn("恢复出厂设置: ".decode('utf-8').encode(coding))
            self.sdk_obj.connection_close()
            time.sleep(5)
            self.sdk_obj.connection_setup()
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_READ_TIME':
            self.LOG.warn("读取时间: ".decode('utf-8').encode(coding))
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
                "Data": [
                    {
                        "time": self._time
                    }
                ]
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_SET_TIME':
            self.LOG.warn("设置时间: ".decode('utf-8').encode(coding))
            self.set_item('_time', msg['Data']['time'])
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_CORRECTION':
            self.LOG.warn("立即校时: ".decode('utf-8').encode(coding))
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_READ_SYSTEM_VERSION':
            self.LOG.warn("读取系统版本信息: ".decode('utf-8').encode(coding))
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
                "Data": [
                    {
                        "appVersionInfo": self._appVersionInfo
                    }
                ]
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_NOTIFY_UPDATE':
            self.LOG.warn("通知设备升级: ".decode('utf-8').encode(coding))
            self.set_item('_version', msg['Data']['newVersion'])
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
            }
            return json.dumps(rsp_msg)

        # 设备参数
        elif msg['Command'] == 'COM_READ_PARAMETER':
            self.LOG.warn("读取参数: ".decode('utf-8').encode(coding))
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
                "Data": [
                    {
                        "deviceID": self._deviceID,
                        "fileServerUrl": self._fileServerUrl,
                        "ntpServer": self._ntpServer,
                        "openDuration": self._openDuration,
                        "alarmTimeout": self._alarmTimeout,
                    }
                ]
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_SETTING_PARAMETERS':
            self.LOG.warn("设置参数: ".decode('utf-8').encode(coding))
            self.set_item('_fileServerUrl', msg['Data']['fileServerUrl'])
            self.set_item('_ntpServer', msg['Data']['ntpServer'])
            self.set_item('_alarmTimeout', msg['Data']['alarmTimeout'])
            self.set_item('_openDuration', msg['Data']['openDuration'])
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_LOAD_CERTIFICATE':
            self.LOG.warn("下发固定凭证信息: ".decode('utf-8').encode(coding))
            self.set_item('_startTime', msg['Data']['startTime'])
            self.set_item('_endTime', msg['Data']['endTime'])
            self.set_item('_subDeviceID', msg['Data']['subDeviceID'])
            self.set_item('_UserType', msg['Data']['UserType'])
            self.set_item('_CredenceType', msg['Data']['CredenceType'])
            self.set_item('_credenceNo', msg['Data']['credenceNo'])
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_READ_CERTIFICATE':
            self.LOG.warn("读取固定凭证信息: ".decode('utf-8').encode(coding))
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
                "Data": [
                    {
                        "startTime": self._startTime,
                        "endTime": self._endTime,
                        "CredenceType": self._CredenceType,
                        "credenceNo": self._credenceNo,
                    }
                ]
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_DELETE_CERTIFICATE':
            self.LOG.warn("删除固定凭证信息: ".decode('utf-8').encode(coding))
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_LOAD_CERTIFICATE_IN_BATCH':
            self.LOG.warn("批量下发固定凭证信息: ".decode('utf-8').encode(coding))
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_READ_CERTIFICATE_IN_BATCH':
            self.LOG.warn("批量读取固定凭证信息: ".decode('utf-8').encode(coding))
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
                "Data": [
                    {
                        "deviceID": self._deviceID,
                        "httpUrl": self._httpUrl,
                        "opTime": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode('utf-8'),
                    }
                ]
            }
            return json.dumps(rsp_msg)

        elif msg['Command'] == 'COM_DELETE_CERTIFICATE_IN_BATCH':
            self.LOG.warn("清除固定凭证操作: ".decode('utf-8').encode(coding))
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
            }
            return json.dumps(rsp_msg)

        # 设备操控
        elif msg['Command'] == 'COM_GATE_CONTROL':
            self.LOG.warn(("开关闸（门）: %s" % (msg['Data']['operateType'])).decode(
                'utf-8').encode(coding))
            self.set_item('_State', msg['Data']['operateType'])
            self.set_item('_userID', msg['Data']['userID'])
            self.set_item('_userType', msg['Data']['userType'])
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
            }
            return json.dumps(rsp_msg)

        # 事件上报
        elif msg['Command'] == 'COM_QUERY_DEV_STATUS':
            self.LOG.warn(("设备状态查询: %s" % ()).decode('utf-8').encode(coding))
            rsp_msg = {
                "Command": msg['Command'],
                "Result": 0,
                "Data": [
                    {
                        "State": self._State,
                    }
                ]
            }
            return json.dumps(rsp_msg)

        else:
            self.LOG.warn('Unknow msg: %s!' % (msg['Command']))
            return None
