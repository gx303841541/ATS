#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys

from basic.base import Base

class Test(Base):
    def run(self):
        self.LOG.warn('What is the thing!')
        self.LOG.debug('caseid:  ' + self.case_id)
        return 1
