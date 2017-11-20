# -*- coding: utf-8 -*-

"""common methods
by Kobe Gong 2017-8-21
use:
    methods in class CommMethod can be used by all the testcases
"""
import re
import sys
import json

from basic.base import Base


class CommMethod(Base):
    def convert_to_dictstr(self, src):
        if isinstance(src, dict):
            return json.dumps(src, sort_keys=True, indent=4, separators=(',', ': ')).decode('utf-8').encode(sys.getfilesystemencoding())

        elif isinstance(src, str):
            return json.dumps(json.loads(src), sort_keys=True, indent=4, separators=(',', ': ')).decode('utf-8').encode(sys.getfilesystemencoding())

        else:
            self.LOG.error('Unknow type(%s): %s' % (src, str(type(src))))
            return None

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
