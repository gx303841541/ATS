# -*- coding: utf-8 -*-

"""common methods
by Kobe Gong 2017-8-21
use:
    methods in class CommMethod can be used by all the testcases
"""
import re
import sys
import json
import time

from basic.base import Base


class CommMethod(Base):
    def convert_to_dictstr(self, src):
        if isinstance(src, dict):
            return json.dumps(src, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

        elif isinstance(src, str):
            return json.dumps(json.loads(src), sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

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

    def json_compare(self, template, target):
        return self.dict_compare(json.loads(template), json.loads(target))

    def dict_compare(self, template, target):
        if not isinstance(template, dict):
            self.LOG.error("template: %s is not dict instance!" % (str(template)))
            return False

        if not isinstance(target, dict):
            self.LOG.error("target: %s is not dict instance!" % (str(target)))
            return False

        if template == target:
            return True
        else:
            def dict_print(src, dst, indent=''):
                self.LOG.info(indent + '{')
                for key in sorted(list(set((src.keys() + dst.keys())))):
                    if key in src and key in dst:
                        if isinstance(src[key], dict):
                            self.LOG.info(indent + '  ' + key + ' : ')
                            dict_print(src[key], dst[key], indent + '  ')
                        else:
                            info = indent + '  ' + key + ' : ' + str(src[key])
                            if src[key] == dst[key] or re.match(r'^no_need$', str(src[key]), re.I):
                                self.LOG.info(info)
                            else:
                                info += ' VS ' + str(dst[key])
                                self.LOG.info(info.ljust(120, '-') + 'diff')

                    elif key in src:
                        if isinstance(src[key], dict):
                            self.LOG.info((indent + '  ' + key + ' : ').ljust(120, '-') + 'left')
                            dict_print(src[key], {}, indent + '  ')
                        else:
                            info = indent + '  ' + key + ' : ' + str(src[key])
                            self.LOG.info(info.ljust(120, '-') + 'left')
                    else:
                        if isinstance(dst[key], dict):
                            self.LOG.info((indent + '  ' + key + ' : ').ljust(120, '-') + 'right')
                            dict_print({}, dst[key], indent + '  ')
                        else:
                            info = indent + '  ' + key + ' : ' + str(dst[key])
                            self.LOG.info(info.ljust(120, '-') + 'right')
                self.LOG.info(indent + '}')
            dict_print(template, target)
            self.LOG.error("template != target")
            return False

    def json_items_compare(self, template_dict, target):
        return self.dict_items_compare(template_dict, json.loads(target))

    def dict_items_compare(self, template_dict, target):
        result = True
        if not isinstance(target, dict):
            self.LOG.error("target: %s is not dict instance!" % (str(target)))
            return False
        else:
            def find_item(item, target_dict):
                for key in target_dict:
                    if isinstance(target_dict[key], dict):
                        if find_item(item, target_dict[key]):
                            return True
                    else:
                        if key == item[0] and target_dict[key] == item[1]:
                            self.LOG.info('Found %s' % (str(item)))
                            return True
                        else:
                            continue
                return False

            for item in template_dict.items():
                if find_item(item, target):
                    pass
                else:
                    self.LOG.error('Not find %s in target:\n%s' % (str(item), self.convert_to_dictstr(target)))
                    result = False
        return result

    def mysleep(self, timeout=1, feedback=None, *arg):
        counter = 0
        while True:
            if feedback and feedback(*arg):
                return True
            elif counter >= timeout:
                return False
            else:
                self.LOG.debug('Total %ds, %ds left...' % (timeout, timeout - counter))
                counter += 1
                time.sleep(1)

    def socket_send_to_router(self, data):
        pass

    def socket_recv_from_router(self, timeout=5):
        pass
