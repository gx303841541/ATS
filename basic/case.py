#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""case tool
   by Kobe Gong. 2017-8-25
"""

import re, random, sys, time, os, shutil, datetime
import threading
import ConfigParser

from basic.cprint import cprint
import APIs.common_APIs as common_APIs
from APIs.common_APIs import my_system_no_check, my_system, my_system_full_output

case_lock = threading.Lock()

#ATS use this to manage a testcase
CASE_STATE = ['not_start', 'ongoing', 'running', 'done']
class Case():
    def __init__(self, config_file, id, name, dir, state='not_start'):
        self.id = id
        self.name = name
        self.dir = dir
        self.state = state
        self.result = None
        self.config_file = config_file
        self.cprint = cprint(__name__)      


    def __cmp__(self, other):  
        if self.__eq__(other):  
            return 0  
        elif self.__lt__(other):  
            return -1  
        else:  
            return 1  
  

    def __eq__(self, other):  
        if not isinstance(other, Case):  
            raise TypeError, "Can't cmp other type to Case!"  
        if self.name == other.name:  
            return True  
        else:  
            return False 


    def __lt__(self, other):  
        if not isinstance(other, Case):  
            raise TypeError, "Can't cmp other type to Case!"  
        if self.name < other.name:  
            return True   
        else:  
            return False 


    def __clean_testlog(self):
        try:
            self.log_dir = self.config_file.get("system", "result_dir")
            dir_separator = os.path.sep

            if os.path.exists(self.log_dir + dir_separator + 'tmp' + dir_separator):
                shutil.rmtree(self.log_dir + dir_separator + 'tmp' + dir_separator)
            os.mkdir(self.log_dir + dir_separator + 'tmp' + dir_separator)

        except Exception as er:
            self.cprint.error_p("Something wrong!!![%s]" % (er))


    def __get_tmp_dir(self):
        log_dir = self.log_dir
        dir_separator = os.path.sep
        return common_APIs.dirit(self.log_dir + dir_separator + 'tmp' + dir_separator)


    def get_case_id(self):
        return self.id

    def get_case_name(self):
        return self.name


    def get_case_dir(self):
        return self.dir


    def get_case_state(self):
        return self.state


    def set_case_state(self, state):
        if state in CASE_STATE:
            self.state = state
            return 0
        else:
            return 1


    def get_case_result(self):
        return self.result


    def set_case_result(self, result):
        self.result = result
        return 0


    def run(self):
        self.__clean_testlog()
        my_system_full_output("nosetests {} -s --exe".format(self.get_case_dir()+ self.get_case_name()))
        common_APIs.dir_copy(self.__get_tmp_dir(), self.config_file.get("system", "result_dir") + os.path.sep + 'default' + os.path.sep)
