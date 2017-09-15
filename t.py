# -*- coding: UTF-8 -*-
import threadpool
import time



import multiprocessing
import os
from datetime import datetime


def subprocess(number):
    # 子进程
    print(' %d subprocess' % number)
    pid = os.getpid()  # 得到当前进程号
    print('process id: %s, start time: %s' % (pid, datetime.now().isoformat()))
    time.sleep(30)  # 当前进程休眠30秒
    print('process id: %s, end time: %s' % (pid, datetime.now().isoformat()))


def mainprocess():
    # 主进程
    print('main process: %d' % os.getpid())
    t_start = datetime.now()
    pool = multiprocessing.Pool(4)
    for i in range(8):
        pool.apply_async(subprocess, args=(i,))
    print('xxoo')
    pool.close()
    pool.join()
    t_end = datetime.now()
    print('main process end: %d ms' % (t_end - t_start).microseconds)


def xxoo(sleep_time=9):
    print('my name is: %s, will sleep %ds' % ('jj', sleep_time))
    time.sleep(sleep_time)


if __name__ == '__main__':

    # 主测试函数
    mainprocess()

    #pool = threadpool.ThreadPool(4)
    #reqs = threadpool.makeRequests(xxoo, range(60, 80))
    #[pool.putRequest(req) for req in reqs]
    #pool.wait()    