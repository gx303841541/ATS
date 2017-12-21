#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""base
by Kobe Gong 2017-8-21
use:
    ATS basic
"""

import os, logging, datetime, re, sys, time
from abc import ABCMeta, abstractmethod
import serial
import serial.tools.list_ports
import ConfigParser


import framework.framework as framework
from . log_tool import MyLogger
import APIs.common_APIs as common_APIs
from connections.my_serial import MySerial, Robot, Wifi
from connections.http import Http
from connections.win_network import WinNetwork
from connections.my_ssh import MySsh
from connections.my_telnet import MyTelnet

class Base(framework.TestCase):
    __metaclass__ = ABCMeta

    def __init__(self, config_file='C:\\ATS\\config.ini', case_id='xxxxxxxx'):
        super(Base, self).__init__()

        #system config
        self.config_file_ori = config_file
        self.config_file = ConfigParser.ConfigParser()
        self.config_file.read(config_file)

        #got case id
        self.case_id = case_id

        #create log dir
        self.log_dir = self.config_file.get("system", "result_dir")
        dir_separator = os.path.sep
        self.log_dir += dir_separator + 'tmp' + dir_separator + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '-' + self.case_id + dir_separator
        self.log_dir = common_APIs.dirit(self.log_dir)
        try:
            os.mkdir(self.log_dir)
        except Exception as er:
            print('Can not create log dir: %s\n[[%s]]' % (self.log_dir, str(er)))
            sys.exit()

        #create the log obj
        self.LOG = MyLogger(self.log_dir + 'output.log', clevel=logging.DEBUG, renable=False)

        #common objs
        self.serial = MySerial(port=self.config_file.get("serial", "port"), baudrate=self.config_file.get("serial", "baudrate"), logger=self.LOG)
        self.ssh = MySsh(host=self.config_file.get("network", "host"), user=self.config_file.get("network", "user"), password=self.config_file.get("network", "password"), log_file=self.log_dir, logger=self.LOG)
        self.telnet = MyTelnet(host=self.config_file.get("network", "host"), user=self.config_file.get("network", "user"), logger=self.LOG)
        self.http = Http(router_url='http://' + self.config_file.get("network", "host") + '/cgi-bin/test1', logger=self.LOG)
        self.win_network = WinNetwork(self.config_file.get("network", "ssid"))
        self.robot = Robot(port=self.config_file.get("robot", "port"), baudrate=self.config_file.get("robot", "baudrate"), logger=self.LOG)
        self.wifi = Wifi(port=self.config_file.get("wifi", "port"), baudrate=self.config_file.get("wifi", "baudrate"), logger=self.LOG)

        self.router_logged =False
