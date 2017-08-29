#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods



@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        self.LOG.warn('caseid:  ' + self.case_id)
        self.my_print()
        return 7


