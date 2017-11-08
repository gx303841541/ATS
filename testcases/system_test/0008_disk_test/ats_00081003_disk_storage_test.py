#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import os
import sys

from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        self.ssh.connect()
        result = self.ssh.send('mount')
        self.LOG.debug(result)
        if result.find("ext4"):
            return self.case_pass()
        else:
            return self.case_fail('No ext4 found!')
