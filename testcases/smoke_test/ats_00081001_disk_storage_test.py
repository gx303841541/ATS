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
    
def findstr(cmdstrings,findstr):
    return cmdstrings.find(findstr)
    
    
def main():
    cmdstr=execmd("df -h")
    result1=findstr(cmdstr,"/udisk/monitor")
    result2=findstr(cmdstr,"/udisk/user")
    result3=findstr(cmdstr,"465.5G")
    result4=findstr(cmdstr,"465.6G")
    print cmdstr
    print result1,result2,result3,result4
    if result1 == -1 or result2 == -1 or result3 == -1 or result4 == -1:
        return 1
    else:
        return 0

#main()
