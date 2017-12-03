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
if sys.platform == 'linux':
    import queue as Queue
else:
    import Queue

from basic.base import Base
import my_socket.my_socket as my_socket


class CommMethod(Base):
    def convert_to_dictstr(self, src):
        if isinstance(src, dict):
            return json.dumps(src, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

        elif isinstance(src, str):
            return json.dumps(json.loads(src), sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False)

        else:
            self.LOG.error('Unknow type(%s): %s' % (src, str(type(src))))
            return None

    def update_db_info(self):
        if int(self.config_file.get("router_db", "update_flag")):
            pass
        else:
            # 数据库查询
            cmds = ['select * from table_user_list;',
                    'select * from table_family_list;']
            result = self.get_router_db_info(cmds)
            if not len(result[1]):
                self.LOG.warn('Read DB failed! Maybe router not binding!')
                return
            self.config_file.set("router_db", "update_flag", 1)
            self.config_file.set("router_db", "family_id", result[1]['id'])
            self.config_file.set("router_db", "user_id", result[1]['user_id'])
            self.config_file.set("router_db", "family_name", result[1]['name'])
            self.config_file.set("router_db", "phone", result[1]['phone'])

            # 数据库中存在相同key时，分开查询
            cmds = ['select * from table_router;']
            result = self.get_router_db_info(cmds)
            self.config_file.set("router_db", "device_uuid", result[1]['device_uuid'])
            self.config_file.set("router_db", "router_id", result[1]['id'])
            self.config_file.write(open(self.config_file_ori, "w"))

        self.common_para_dict = {
            "family_id": int(self.config_file.get("router_db", "family_id")),
            "user_id": int(self.config_file.get("router_db", "user_id")),
            "family_name": self.config_file.get("router_db", "family_name"),
            "phone": self.config_file.get("router_db", "phone"),
            "device_uuid": self.config_file.get("router_db", "device_uuid"),
            "router_id": self.config_file.get("router_db", "router_id"),
        }

    def get_router_db_info(self, cmds, db='/db/iot_new_router.db', mode_line=True):
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

        a = re.findall(
            u'(\w+)\s*=\s*((?:\S)+)', info_str, re.M)
        result_dict = {}
        for name, value in a:
            result_dict[name] = value

        result_str = re.sub(r'\[\d+\.\d+\].*$', '', info_str, re.M)

        return result_str, result_dict

    def get_router_db_info_dict(self, cmds, db='/db/iot_new_router.db', mode_line=True, separator='\n'):
        result_list = []
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
        info_str = re.sub(r'\[\d+\.\d+\].*$', '', info_str, re.M)

        iterms = [item for item in re.split(r'separator', info_str) if item]
        if iterms:
            for item in iterms:
                a = re.findall(u'(\w+)\s*=\s*((?:\S)+)', info_str, re.M)
                tmp_dict = {}
                for name, value in a:
                    tmp_dict[name] = value
                if tmp_dict:
                    result_list.append(tmp_dict)
        else:
            self.LOG.warn('Read DB failed, no item found!')
        return result_list

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
                    if isinstance(target_dict[key], list):
                        for i in target_dict[key]:
                            if isinstance(i, dict):
                                if find_item(item, i):
                                    return True
                                else:
                                    self.LOG.warn(unicode(i))
                                    continue
                    else:
                        if key == item[0] and target_dict[key] == item[1]:
                            self.LOG.info('Found %s' % (unicode(item)))
                            return True
                        else:
                            continue
                return False

            for item in template_dict.items():
                if find_item(item, target):
                    pass
                else:
                    self.LOG.error('Not find %s in target:\n%s' %
                                   (unicode(item), self.convert_to_dictstr(target)))
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
                self.LOG.debug('Total %ds, %ds left...' %
                               (timeout, timeout - counter))
                counter += 1
                time.sleep(1)

    def socket_send_to_router(self, data):
        self.client = my_socket.MyClient(
            (self.config_file.get("network", "host"), 5100), self.LOG, Queue.Queue(), Queue.Queue(), debug=True, printB=False)

        if self.client.is_connected() or self.client.connect():
            pass
        else:
            self.LOG.error("Connect to router failed!")
            return False

        self.client.send_once(data)
        return True

    def socket_recv_from_router(self, timeout=1, pkg_num=0):
        data = ''
        if pkg_num == 0:
            tmp = 1
            while tmp:
                tmp = self.client.recv_once(timeout)
                data += tmp
        else:
            for i in range(pkg_num):
                data += self.client.recv_once(timeout)
        return data

    def json_compare(self, template, target):
        return self.dict_compare(template, json.loads(target))

    def dict_compare(self, template, target):
        if not isinstance(template, dict):
            self.LOG.error("template: %s is not dict instance!" %
                           (str(template)))
            return False

        if not isinstance(target, dict):
            self.LOG.error("target: %s is not dict instance!" % (str(target)))
            return False

        result = True
        if template == target:
            return result
        else:
            def list_print(src, dst, indent=''):
                result = True
                if len(src) != len(dst):
                    result = False

                def dict_modify(src_dict, dst_key):
                    for item in src_dict:
                        if isinstance(src_dict[item], dict):
                            if dict_modify(src_dict[item], dst_key):
                                return True
                        else:
                            if item == dst_key and src_dict[dst_key] != 'no_need':
                                src_dict[dst_key] = 'no_need'
                                return True
                    return False

                def find_from_dict(src_dict):
                    keys = []
                    for item in src_dict:
                        if isinstance(item, dict):
                            keys += find_from_dict(item)
                        else:
                            if re.match(r'no_need', unicode(src_dict[item]), re.I):
                                keys.append(item)
                    return keys

                keys = []
                for item in src:
                    if isinstance(item, dict) and item:
                        keys += find_from_dict(item)

                for k in keys:
                    for item in dst:
                        if isinstance(item, dict):
                            dict_modify(item, k)

                self.LOG.info(indent + '[')
                check_list = []
                for item in sorted(list(src + dst)):
                    if item in check_list:
                        continue
                    else:
                        check_list.append(item)

                    if item in src and item in dst:
                        if isinstance(item, dict):
                            if not dict_print(item, item, indent + '  '):
                                result = False
                        else:
                            info = indent + '  ' + unicode(item)
                            self.LOG.info(info)
                    elif item in src:
                        if isinstance(item, dict):
                            if not dict_print(item, {}, indent + '  '):
                                result = False

                        elif isinstance(item, list):
                            if not dict_print(item, [], indent + '  '):
                                result = False

                        else:
                            info = indent + '  ' + unicode(item)
                            self.LOG.info(info.ljust(
                                100, '-') + 'expected only')
                            result = False
                    else:
                        if isinstance(item, dict):
                            if not dict_print({}, item, indent + '  '):
                                result = False

                        elif isinstance(item, list):
                            if not list_print([], item, indent + '  '):
                                result = False

                        else:
                            info = indent + '  ' + unicode(item)
                            self.LOG.info(info.ljust(
                                100, '-') + 'actuality only')
                            result = False
                self.LOG.info(indent + ']')
                return result

            def dict_print(src, dst, indent=''):
                result = True
                self.LOG.info(indent + '{')
                for key in sorted(list(set((src.keys() + dst.keys())))):
                    if key in src and key in dst:
                        if isinstance(src[key], dict):
                            self.LOG.info(indent + '  ' + key + ' : ')
                            if not dict_print(src[key], dst[key], indent + '  '):
                                result = False

                        elif isinstance(src[key], list):
                            if not list_print(src[key], dst[key], indent + '  '):
                                result = False

                        else:
                            info = indent + '  ' + key + \
                                ' : ' + unicode(src[key])
                            if src[key] == dst[key] or re.match(r'^no_need$', unicode(src[key]), re.I):
                                self.LOG.info(info)
                            else:
                                info += ' VS ' + unicode(dst[key])
                                self.LOG.info(info.ljust(
                                    100, '-') + 'mismatch')
                                result = False
                    elif key in src:
                        if isinstance(src[key], dict):
                            self.LOG.info(
                                (indent + '  ' + key + ' : ').ljust(100, '-') + 'expected only')
                            if not dict_print(src[key], {}, indent + '  '):
                                result = False
                        else:
                            info = indent + '  ' + key + \
                                ' : ' + unicode(src[key])
                            self.LOG.info(info.ljust(
                                100, '-') + 'expected only')
                            result = False
                    else:
                        if isinstance(dst[key], dict):
                            self.LOG.info(
                                (indent + '  ' + key + ' : ').ljust(100, '-') + 'actuality only')
                            if not dict_print({}, dst[key], indent + '  '):
                                result = False
                        else:
                            info = indent + '  ' + key + \
                                ' : ' + unicode(dst[key])
                            self.LOG.info(info.ljust(
                                100, '-') + 'actuality only')
                            result = False
                self.LOG.info(indent + '}')
                return result

            result = dict_print(template, target)
            if not result:
                self.LOG.error("template != target")
            return result

    def get_package_by_keyword(self, package_str, keyword_list, except_keyword_list=None, package_separator='\n'):
        if not len(package_str):
            self.LOG.warn("package str is empty!")
            return False

        packages = [pkg for pkg in re.split(
            r'%s' % (package_separator), package_str) if pkg]
        self.LOG.info('%d package found!' % (len(packages)))

        self.LOG.info('keywords are: %s' % (str(keyword_list)))
        target_package_list = packages
        for keyword in keyword_list:
            self.LOG.debug('use: %s to select packages...' % (keyword))
            target_package_list = [package for package in target_package_list if re.search(
                r'%s' % (keyword), package)]
            self.LOG.info('%d package left!' % (len(target_package_list)))

        if except_keyword_list:
            for keyword in except_keyword_list:
                self.LOG.debug('use: %s to exclude packages...' % (keyword))
                target_package_list = [package for package in target_package_list if not re.search(
                    r'%s' % (keyword), package)]
                self.LOG.info('%d package left!' % (len(target_package_list)))

        return target_package_list
