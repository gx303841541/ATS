#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""log tool
by Kobe Gong. 2017-8-21
"""

import logging
import sys
import os
from logging.handlers import RotatingFileHandler
import traceback
if sys.platform == 'linux':
    import coloredlogs
    coloredlogs.DEFAULT_DATE_FORMAT = ''
    coloredlogs.DEFAULT_LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'

from .cprint import cprint



# Windows CMD命令行 字体颜色定义 text colors
FOREGROUND_BLACK = 0x00  # black.
FOREGROUND_DARKBLUE = 0x01  # dark blue.
FOREGROUND_DARKGREEN = 0x02  # dark green.
FOREGROUND_DARKSKYBLUE = 0x03  # dark skyblue.
FOREGROUND_DARKRED = 0x04  # dark red.
FOREGROUND_DARKPINK = 0x05  # dark pink.
FOREGROUND_DARKYELLOW = 0x06  # dark yellow.
FOREGROUND_DARKWHITE = 0x07  # dark white.
FOREGROUND_DARKGRAY = 0x08  # dark gray.
FOREGROUND_BLUE = 0x09  # blue.
FOREGROUND_GREEN = 0x0a  # green.
FOREGROUND_SKYBLUE = 0x0b  # skyblue.
FOREGROUND_RED = 0x0c  # red.
FOREGROUND_PINK = 0x0d  # pink.
FOREGROUND_YELLOW = 0x0e  # yellow.
FOREGROUND_WHITE = 0x0f  # white.


# Windows CMD命令行 背景颜色定义 background colors
BACKGROUND_BLUE = 0x10  # dark blue.
BACKGROUND_GREEN = 0x20  # dark green.
BACKGROUND_DARKSKYBLUE = 0x30  # dark skyblue.
BACKGROUND_DARKRED = 0x40  # dark red.
BACKGROUND_DARKPINK = 0x50  # dark pink.
BACKGROUND_DARKYELLOW = 0x60  # dark yellow.
BACKGROUND_DARKWHITE = 0x70  # dark white.
BACKGROUND_DARKGRAY = 0x80  # dark gray.
BACKGROUND_BLUE = 0x90  # blue.
BACKGROUND_GREEN = 0xa0  # green.
BACKGROUND_SKYBLUE = 0xb0  # skyblue.
BACKGROUND_RED = 0xc0  # red.
BACKGROUND_PINK = 0xd0  # pink.
BACKGROUND_YELLOW = 0xe0  # yellow.
BACKGROUND_WHITE = 0xf0  # white.


class MyLogger:
    def __init__(self, path, clevel=logging.DEBUG, cenable=True, flevel=logging.DEBUG, fenable=True, rlevel=logging.DEBUG, renable=True):
        if sys.platform == 'linux':
            coloredlogs.install(level=clevel)

        self.cprint = cprint()
        self.p = logging.getLogger(path)
        self.p.setLevel(logging.DEBUG)
        #fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%m-%d %H:%M:%S')
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')

        # 设置CMD日志
        if cenable == True and sys.platform == 'linux':
            pass
        else:
            sh = logging.StreamHandler()
            sh.setFormatter(fmt)
            sh.setLevel(clevel)
            self.p.addHandler(sh)

        # 设置文件日志
        if fenable == True:
            fh = logging.FileHandler(path)
            fh.setFormatter(fmt)
            fh.setLevel(flevel)
            self.p.addHandler(fh)

        # 定义一个RotatingFileHandler，最多备份5个日志文件，每个日志文件最大10M
        if renable == True:
            rh = RotatingFileHandler(
                'system.log', maxBytes=10 * 1024 * 1024, backupCount=5)
            rh.setFormatter(fmt)
            rh.setLevel(rlevel)
            self.p.addHandler(rh)

    def debug(self, message):
        s = traceback.extract_stack()
        msg_prefix = '[' + \
            os.path.basename(s[-2][0]) + ': ' + str(s[-2][1]) + '] '

        self.cprint.set_colour(FOREGROUND_BLUE)
        self.p.debug(msg_prefix + message)
        self.cprint.reset_colour()

    def info(self, message):
        s = traceback.extract_stack()
        msg_prefix = '[' + \
            os.path.basename(s[-2][0]) + ': ' + str(s[-2][1]) + '] '

        self.cprint.set_colour(FOREGROUND_GREEN)
        self.p.info(msg_prefix + message)
        self.cprint.reset_colour()

    def yinfo(self, message):
        s = traceback.extract_stack()
        msg_prefix = '[' + \
            os.path.basename(s[-2][0]) + ': ' + str(s[-2][1]) + '] '

        self.cprint.set_colour(FOREGROUND_YELLOW)
        self.p.info(msg_prefix + message)
        self.cprint.reset_colour()

    def warn(self, message):
        s = traceback.extract_stack()
        msg_prefix = '[' + \
            os.path.basename(s[-2][0]) + ': ' + str(s[-2][1]) + '] '

        self.cprint.set_colour(FOREGROUND_PINK)
        self.p.warn(msg_prefix + message)
        self.cprint.reset_colour()

    def error(self, message):
        s = traceback.extract_stack()
        msg_prefix = '[' + \
            os.path.basename(s[-2][0]) + ': ' + str(s[-2][1]) + '] '

        self.cprint.set_colour(FOREGROUND_RED)
        self.p.error(msg_prefix + message)
        self.cprint.reset_colour()

    def critical(self, message):
        s = traceback.extract_stack()
        msg_prefix = '[' + \
            os.path.basename(s[-2][0]) + ': ' + str(s[-2][1]) + '] '

        self.cprint.set_colour(FOREGROUND_RED)
        self.p.critical(msg_prefix + message)
        self.cprint.reset_colour()


if __name__ == '__main__':
    mylog = MyLogger('yyx.log')
    mylog.debug("11111")
    mylog.info("11111")
    mylog.warn("11111")
    mylog.error("11111")
    mylog.cprint.error_p('xxoo')
