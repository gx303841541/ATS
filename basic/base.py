#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

class Base(framework.TestCase):
    __metaclass__ = ABCMeta

    def __init__(self, config_file='C:\\ATS\\config.ini', case_id='xxxxxxxx'):
        super(Base, self).__init__()
        self.config_file = ConfigParser.ConfigParser()
        self.config_file.read(config_file)

        self.case_id = case_id
        self.log_dir = self.config_file.get("system", "result_dir")
        dir_separator = os.path.sep

        self.log_dir += dir_separator + 'tmp' + dir_separator + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '-' + self.case_id + dir_separator
        self.log_dir = common_APIs.dirit(self.log_dir)
        try:
            os.mkdir(self.log_dir)
        except Exception as er:
            print('Can not create log dir: %s\n[[%s]]' % (self.log_dir, str(er)))
            sys.exit()

        self.LOG = MyLogger(self.log_dir + 'output.log', clevel=logging.DEBUG, renable=False)

        self.serial = MySerial(port=self.config_file.get("serial", "port"), baudrate=self.config_file.get("serial", "baudrate"), logger=self.LOG)
        self.ssh = MySsh(host=self.config_file.get("network", "host"), user=self.config_file.get("network", "user"), password=self.config_file.get("network", "password"), log_file=self.log_dir, logger=self.LOG)
        self.telnet = MyTelnet(host=self.config_file.get("network", "host"), user=self.config_file.get("network", "user"), prompt='^.*OpenWrt.*#\s*$', log_file=self.log_dir, logger=self.LOG)


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
        pass


    def close(self):
        return self.conn.close()


    def is_open(self):
        if self.conn:
            return True
        else:
            return False


class MyTelnet():
    def __init__(self, host, user=None, prompt='^.*(\$|#)', log_file=sys.stdout, logger=None):
        self.prompt = prompt
        self.host = host
        self.user = user
        self.log_file = log_file
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


    def send(self, cmd, timeout=5, prompt=None):
        if prompt == None:
            prompt = self.prompt

        try:
            self.LOG.debug('To send cmd: %s, expect [%s]' % (cmd, prompt))
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


class MySerial():
    def __init__(self, port=None, baudrate=115200, logger=None):
        self.LOG = logger
        self.port = port
        self.baudrate = baudrate
        self.com = None


    def get_available_ports(self):
        port_list = list(serial.tools.list_ports.comports())
        r_port_list = []

        if len(port_list) <= 0:
            #self.LOG.error("Can't find any serial port!")
            pass

        else:
            for i in range(len(port_list)):
                serial_name = list(port_list[i])[0]
                self.LOG.debug("Get serial port: %s" % {serial_name})
                r_port_list.append(serial_name)

        return r_port_list


    def open(self):

        port_list = self.get_available_ports()
        if self.port in port_list:
            pass
        elif self.port == 'any' and port_list:
            self.port = port_list[0]
        else:
            self.LOG.error("Can't find any serial port!")
            return 1

        try:  
            self.com = serial.Serial(self.port, baudrate=self.baudrate, timeout=5)
            if self.is_open():
                pass
            else:
                self.LOG.error("Can't open %s fail!" % (com))
                return 1  

        except Exception as er:
            self.com = None  
            self.LOG.error('Open %s fail!' % (com))
            return 1


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
        return self.com.readall()


    def write(self, data):
        return self.com.write(data)