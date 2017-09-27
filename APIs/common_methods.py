# -*- coding: utf-8 -*-

"""common methods
by Kobe Gong 2017-8-21
use:
    methods in class CommMethod can be used by all the testcases
"""

from basic.base import Base


class CommMethod(Base):

    def my_print(self):
        self.LOG.warn('Just for test!')