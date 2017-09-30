# -*- coding: utf-8 -*-

"""common APIs
by Kobe Gong 2017-8-21
use:
    all the funcs can be used by any module should be here
"""

#import queue, fcntl
import threading
import re
import os
import sys
from subprocess import *
import functools
import struct


'''
def file_lock(open_file):
    return fcntl.flock(open_file, fcntl.LOCK_EX | fcntl.LOCK_NB)

def file_unlock(open_file):
    return fcntl.flock(open_file, fcntl.LOCK_UN)
'''


def get_output(*popenargs, **kwargs):
    process = Popen(*popenargs, stdout=PIPE, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    return output


def pipe_output(*popenargs, **kwargs):
    process = Popen(*popenargs, stdout=PIPE, stderr=PIPE, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    return output


def full_output(*popenargs, **kwargs):
    process = Popen(*popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    return output


# run a cmd and check exec result
def my_system(*cmd):
    return check_output(*cmd, universal_newlines=True, shell=True)


# run a cmd without check exec result
def my_system_no_check(*cmd):
    print('run:' + cmd[0])
    return get_output(*cmd, universal_newlines=True, shell=True)


# run a cmd without check exec result
def my_system_full_output(*cmd):
    print('run:' + cmd[0])
    return full_output(*cmd, universal_newlines=True, shell=True)


def register_caseid(casename):
    def cls_decorator(cls):
        def __init__(self, config_file='C:\\ATS\\config.ini', case_id='xxxxxxxx'):
            super(cls, self).__init__(case_id=casename.split('_')[1])

        cls.__init__ = __init__
        return cls
    return cls_decorator


# get all the files match regex 'file_re' from a dir
def get_file_by_re(dir, file_re):
    file_list = []
    if os.path.exists(dir):
        pass
    else:
        print(dir + ' not exist!\n')
        return file_list

    all_things = os.listdir(dir)

    for item in all_things:
        if os.path.isfile(os.path.join(dir, os.path.basename(item))) and re.match(file_re, item, re.S):
            file_list.append(os.path.join(dir, os.path.basename(item)))

        elif os.path.isdir(os.path.join(dir, os.path.basename(item))):
            file_list += get_file_by_re(os.path.join(dir,
                                                     os.path.basename(item)), file_re)

        else:
            continue

    return file_list


# use to copy a dir to another dir
def dir_copy(source_dir, target_dir):
    for f in os.listdir(source_dir):
        sourceF = os.path.join(source_dir, f)
        targetF = os.path.join(target_dir, f)

        if os.path.isfile(sourceF):
            # 创建目录
            if not os.path.exists(targetF):
                os.makedirs(target_dir)

            # 文件不存在，或者存在但是大小不同，覆盖
            if not os.path.exists(targetF) or (os.path.exists(targetF) and (os.path.getsize(targetF) != os.path.getsize(sourceF))):
                # 2进制文件
                open(targetF, "wb").write(open(sourceF, "rb").read())
            else:
                pass

        elif os.path.isdir(sourceF):
            dir_copy(sourceF, targetF)


# use to make a dir standard
def dirit(dir):
    if not dir.endswith(os.path.sep):
        dir += os.path.sep

    return re.sub(r'%s+' % (re.escape(os.path.sep)), re.escape(os.path.sep), dir, re.S)


# use to add lock befow call the func
def need_add_lock(lock):
    def sync_with_lock(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            lock.acquire()
            try:
                return func(*args, **kwargs)
            finally:
                lock.release()

        return new_func
    return sync_with_lock


# Hex print
def protocol_data_printB(data, title=''):
    datas = re.findall(r'([\x00-\xff])', data, re.M)
    ret = title + ' %s bytes:' % (len(datas)) + '\n\t\t'
    counter = 0
    for item in datas:
        ret += '{:02x}'.format(ord(item)) + ' '
        counter += 1
        if counter == 10:
            ret += ' ' + '\n\t\t'
            counter -= 10

    return ret


# create CRC
def crc(s):
    result = 0
    for i in range(len(s)):
        result += struct.unpack('B', s[i])[0]

    result %= 0xff
    return struct.pack('B', result)
