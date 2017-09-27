#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""serial module
by Kobe Gong. 2017-9-11
"""

import os
import logging
import datetime
import re
import sys
import time
from abc import ABCMeta, abstractmethod
import serial
import serial.tools.list_ports

# serial comm class


class MySerial():
    def __init__(self, port=None, baudrate=9600, logger=None):
        self.LOG = logger
        self.port = port
        self.baudrate = baudrate
        self.com = None
        #self.LOG.debug("Create serial obj for : %s" % (port))

    def get_available_ports(self):
        port_list = list(serial.tools.list_ports.comports())
        r_port_list = []

        if len(port_list) <= 0:
            #self.LOG.error("Can't find any serial port!")
            pass
        else:
            for i in range(len(port_list)):
                serial_name = list(port_list[i])[0]
                self.LOG.debug("Get serial port: %s" % (serial_name))
                r_port_list.append(serial_name)

        return r_port_list

    def open(self):
        port_list = self.get_available_ports()
        if self.port in port_list:
            pass
        elif self.port == 'any' and port_list:
            self.port = port_list[0]
        else:
            #self.LOG.error("Can't find any serial port!")
            return 1

        try:
            self.com = serial.Serial(
                self.port, baudrate=self.baudrate, timeout=100)
            if self.is_open():
                self.LOG.debug("port: %s open success" % (self.port))
            else:
                self.LOG.error("Can't open %s!" % (self.port))
                return 1

        except Exception as er:
            self.com = None
            self.LOG.error('Open %s fail!' % (self.port))
            return 1

        return 0

    def close(self):
        if type(self.com) != type(None):
            self.com.close()
            self.com = None
            return True

        return not self.com.isOpen()

    def is_open(self):
        if self.com:
            return self.com.isOpen()
        else:
            return False

    def readn(self, n=1):
        return self.com.read(n)

    def readline(self):
        return self.com.readline()

    def readlines(self):
        return self.com.readlines()

    def readall(self):
        return self.com.read_all()

    def read_until(self, prompt):
        ret = self.com.read_until(terminator=prompt)
        self.LOG.yinfo(ret)
        return re.search(r'%s' % (prompt), ret, re.S)

    def readable(self):
        return self.com.readable()

    def write(self, data):
        return self.com.write(data + '\r')

    def timeout_set(self, timeout=100):
        self.com.timeout = timeout
