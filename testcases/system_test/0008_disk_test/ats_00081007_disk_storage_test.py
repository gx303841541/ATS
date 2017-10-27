#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import telnetlib
import os
import sys
sys.path.append(os.path.abspath('.'))
from APIs.common_APIs import register_caseid
import APIs.common_methods as common_methods


@register_caseid(casename=__name__)
class Test(common_methods.CommMethod):

    def run(self):
        return main()


        
Host = '192.168.10.1' 
finish = ':/#'
#执行命令
def execmd(comm):
        #print comm
        comm=comm.encode('ascii')
        tn = telnetlib.Telnet(Host)
        tn.open(Host)
        time.sleep(5)
        rd=tn.read_very_eager()
        x=tn.write(comm +'\n')
        time.sleep(3)
        rd=tn.read_very_eager()
        return rd
#copy文件    
def copyfile():
    try:
        execmd("cp -R //udisk//user//testfiles //udisk//usb1")
        return 0
    except Exception,e:
        return 1
    
def main():
    return copyfile()
    
    
