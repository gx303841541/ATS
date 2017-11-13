# -*- coding: utf-8 -*-

"""common methods
by Kobe Gong 2017-8-21
use:
    methods in class CommMethod can be used by all the testcases
"""
import re, sys

from basic.base import Base


class CommMethod(Base):
    def myprint(self):
        self.LOG.warn('Just for test!')

    def router_db_info(self, cmds, db='/db/iot_new_router.db', mode_line=True):
        if self.serial.is_open():
            pass
        else:
            self.serial.open()
        self.serial.send('sqlite3 %s' % (db))

        if mode_line:
            self.serial.send('.mode line')

        for cmd in cmds:
            self.serial.send(cmd)

        self.serial.send('.exit')
        info_list = self.serial.readlines()
        info_str = ''.join(info_list)

        a = re.findall(u'(\w+)\s*=\s*((?:\w|[\u4e00-\u9fa5])+)', info_str, re.M)
        result_dict = {}
        for name, value in a:
            result_dict[name] = value

        result_str = re.sub(r'\[\d+\.\d+\].*$', '', info_str, re.M)

        return result_str, result_dict
