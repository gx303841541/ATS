# -*- coding: utf-8 -*-

"""common tool
by Kobe Gong 2017-8-21
"""

#import queue, fcntl
import threading
import re, os, sys
from subprocess import *
import functools



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


#run a cmd and check exec result
def my_system(*cmd):
    return check_output(*cmd, universal_newlines=True, shell=True)

    
#run a cmd without check exec result
def my_system_no_check(*cmd):
    print('run:' + cmd[0])
    return get_output(*cmd, universal_newlines=True, shell=True)


#run a cmd without check exec result
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
            file_list += get_file_by_re(os.path.join(dir, os.path.basename(item)), file_re)

        else:
            continue

    return file_list


def dir_copy(source_dir, target_dir):   
    for f in os.listdir(source_dir):
        sourceF = os.path.join(source_dir, f)
        targetF = os.path.join(target_dir, f)

        if os.path.isfile(sourceF):   
            #创建目录   
            if not os.path.exists(targetF):
                os.makedirs(target_dir)
             
            #文件不存在，或者存在但是大小不同，覆盖   
            if not os.path.exists(targetF) or (os.path.exists(targetF) and (os.path.getsize(targetF) != os.path.getsize(sourceF))):
                #2进制文件
                open(targetF, "wb").write(open(sourceF, "rb").read())  
            else:
                pass
    
        elif os.path.isdir(sourceF):   
            dir_copy(sourceF, targetF) 



def dirit(dir):
    if not dir.endswith(os.path.sep):
        dir += os.path.sep

    return re.sub(r'%s+' % (re.escape(os.path.sep)), re.escape(os.path.sep), dir, re.S)


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
