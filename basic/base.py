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

import telnetlib
import paramiko

import framework.framework as framework
from . log_tool import MyLogger
import APIs.common_APIs as common_APIs
from my_serial.my_serial import MySerial
from my_http.http import Http
from win_network.win_network import WinNetwork

class Base(framework.TestCase):
    __metaclass__ = ABCMeta

    def __init__(self, config_file='C:\\ATS\\config.ini', case_id='xxxxxxxx'):
        super(Base, self).__init__()

        #system config
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


#ssh to router
class MySsh():
    def __init__(self, host, user=None, password=None, log_file=sys.stdout, logger=None):
        self.host = host
        self.user = user
        self.password = password
        self.log_file = log_file
        self.LOG = logger
        self.conn = None


    def connect(self):
        self.LOG.debug('ssh to %s' % (self.host))
        #paramiko.util.log_to_file(self.log_file + 'ssh.log')
        self.conn = paramiko.SSHClient()
        self.conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.conn.connect(self.host, 22, self.user, self.password, timeout=5)


    def send(self, cmd, timeout=5, prompt=None):
        self.LOG.debug('To send cmd: %s' % (cmd))
        try:
            stdin, stdout, stderr = self.conn.exec_command(cmd)
            err = stderr.read()
            out = stdout.read()

        except Exception as er:
            self.LOG.error('Send %s wrong: %s\n[[%s]]' % (cmd, err, str(er)))
            return None
        return out


    def get(self, timeout=5, prompt=None):
        try:
            stdin, stdout, stderr = self.conn.exec_command('\n')
            err = stderr.read()
            out = stdout.read()

        except Exception as er:
            self.LOG.error('get output wrong: %s\n[%s]' % (err, str(er)))
            return None
        return out + err


    def close(self):
        return self.conn.close()


    def is_open(self):
        if self.conn:
            return True
        else:
            return False


#telnet to router
class MyTelnet():
    def __init__(self, host, user=None, logger=None):
        self.host = host
        self.user = user
        self.LOG = logger
        self.conn = None


    def connect(self):
        self.LOG.debug('telnet to %s' % (self.host))
        self.conn = telnetlib.Telnet(self.host, timeout=5)
        try:
            self.conn.open(self.host)
            time.sleep(1)
            rd = self.conn.read_very_eager()

        except Exception as er:
            self.LOG.critical("open telnet wrong!!![%s]" % (er))
            self.conn.close()
            self.conn = None
            return 0


    def send(self, cmd, timeout=5):
        self.LOG.debug('To send cmd: %s' % (cmd))
        try:
            cmd = cmd.encode('ascii')
            x = self.conn.write(cmd +'\n')
            time.sleep(1)
            r = self.conn.read_very_eager()
            return r

        except Exception as er:
            self.LOG.critical("send %s wrong!!![%s]" % (cmd, er))
            self.conn.close()
            return 0


    def get(self, timeout=5, prompt=None):
        pass


    def close(self):
        return self.conn.close()


    def is_open(self):
        if self.conn:
            return True
        else:
            return False
