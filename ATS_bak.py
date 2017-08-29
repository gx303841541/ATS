#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re, sys, time, os, shutil, datetime
import threading
import random
import signal
import subprocess
import argparse, logging
import ConfigParser
from cmd import Cmd

from basic.log_tool import MyLogger
from basic.cprint import cprint
import APIs.common_APIs as common_APIs
from APIs.common_APIs import my_system_no_check, my_system, my_system_full_output
import decimal


class ArgHandle():
    def __init__(self, name):
        self.parser = self.build_option_parser("-" * 50)

    def build_option_parser(self, description):
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument(
            '-l', '--cmdloop',
            action='store_true',
            help='whether go into cmd loop',
        )
        return parser

    def get_args(self, attrname):
        return getattr(self.args, attrname)

    def check_args(self):
        pass

    def run(self):
        self.args = self.parser.parse_args()
        cprint.notice_p("CMD line: " + str(self.args))
        self.check_args()


class MyCmd(Cmd): 
    def __init__(self, config_file='config.ini'):
        Cmd.__init__(self)
        self.prompt = "ATS>"
        self.config_file = ConfigParser.ConfigParser()
        self.config_file.read(config_file)
        self.case_re = r'^ats_\d{8}_\w+_test\.py$'
        self.__case_update()
        self.log_dir = self.config_file.get("system", "result_dir")
        self.dir_separator = self.config_file.get("system", "dir_separator")

    def __case_update(self):
        self.cases = {}
        self.suites = []
        self.case_dir =  self.config_file.get("system", "case_dir")
        case_list = common_APIs.get_file_by_re(self.case_dir, self.case_re)
        for case in case_list:
            m = re.match(r'^(?P<case_dir>.*?)(?P<case_file>ats_(?P<case_id>\d{8})_\w+_test\.py)$', case, re.S)
            self.cases[m.group('case_id')] = {
                'case_dir': m.group('case_dir'),
                'case_name': m.group('case_file'),
                #'case_id': m.group('case_id'),
            }
        
        for case in sorted(self.cases):
            if self.cases[case]['case_dir'] in self.suites:
                continue
            else:
                self.suites.append(self.cases[case]['case_dir'])
        self.suites.sort()

        if not os.path.exists(self.config_file.get("system", "result_dir")):
            os.mkdir(self.config_file.get("system", "result_dir"))

    def __clean_testlog(self):
        try:
            log_dir = self.log_dir
            dir_separator = self.dir_separator

            if os.path.exists(self.config_file.get("system", "result_dir") + dir_separator + 'tmp/'):
                shutil.rmtree(self.config_file.get("system", "result_dir") + dir_separator + 'tmp/')
            os.mkdir(self.config_file.get("system", "result_dir") + dir_separator + 'tmp/')

        except Exception as er:
            cprint.error_p("Something wrong!!![%s]" % (er))


    def __get_suite_dir(self, suite_name):
        suite_name = re.sub(r'^[A-Z]+:', '', suite_name, re.S)
        log_dir = self.log_dir
        dir_separator = self.dir_separator
        log_dir += dir_separator + re.sub(r'%s+' % (dir_separator), '_', suite_name, re.S) + '-' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + dir_separator
        log_dir = re.sub(r'%s+' % (dir_separator), dir_separator, log_dir, re.S)
        return log_dir 


    def __get_tmp_dir(self):
        log_dir = self.log_dir
        dir_separator = self.dir_separator
        return re.sub(r'%s+' % (dir_separator), dir_separator, self.log_dir + dir_separator + 'tmp' + dir_separator, re.S) 


    def help_listcase(self):  
        cprint.common_p("list case info by case id")

      
    def do_listcase(self, arg=None, opts=None):
        if arg in self.cases:
            cprint.debug_p(arg + ':')
            for item in self.cases[arg]:
                cprint.common_p("    " + item.ljust(20) + ':    ' + str(self.cases[arg][item]).ljust(40))
            cprint.debug_p('-' * 30)
        else:
            cprint.warning_p('unknow case: %s' % (arg))


    def help_listcases(self):  
        cprint.common_p("list all the cases onder dir:{}".format(self.case_dir))

      
    def do_listcases(self, arg, opts=None):
        for case in sorted(self.cases):
            cprint.debug_p(case + ':')
            for item in self.cases[case]:
                cprint.common_p("    " + item.ljust(20) + ':    ' + str(self.cases[case][item]).ljust(40))
            cprint.debug_p('-' * 30)
        cprint.notice_p('total: %s' % (len(self.cases)))


    def help_listsuite(self):  
        cprint.common_p("list all the subsuites and cases under the given suite")

 
    def ndo_suite_show(self, dir, pre_str='', fatherdir=''):
        dir_list = []
        all_things = os.listdir(dir)
        if len(fatherdir) > 0 and not fatherdir.endswith(self.config_file.get("system", "dir_separator")):
            fatherdir += self.config_file.get("system", "dir_separator")

        cprint.notice_p(pre_str + dir.replace(fatherdir, '') + ':')

        pre_str += ' ' * (len(dir) + 1 - len(fatherdir))
        for item in all_things:       
            if os.path.isfile(os.path.join(dir, os.path.basename(item))) and re.match(self.case_re, item, re.S):
                cprint.common_p(pre_str + item)

            elif os.path.isdir(os.path.join(dir, os.path.basename(item))) and item.startswith('test'):
                dir_list.append((os.path.join(dir, os.path.basename(item)), pre_str, dir))

            else:
                continue      

        for subdir in dir_list:
            self.ndo_suite_show(subdir[0], subdir[1], subdir[2])


    def do_listsuite(self, arg, opts=None):
        if arg in self.suites:      
            self.ndo_suite_show(arg)
        else:
            cprint.warning_p('unknow suite: %s' % (arg))


    def help_listsuites(self):  
        cprint.common_p("will list all the suites")

      
    def do_listsuites(self, arg, opts=None):
        for i in range(len(self.suites)):
            cprint.notice_p("    " + str(i).ljust(10) + ':    ' + self.suites[i].ljust(40))
            cprint.common_p('-' * 30)


    def help_run(self):  
        cprint.common_p("run case or suite")


    def __faild_cases_proc(self, stout_file, suite=None):
        cprint.debug_p("To open %s:\n" % (stout_file))
        with open(stout_file, 'r') as f:
            all = f.read()
            if len(all) > 0:
                log_list = re.split(r'\n\n+', all, re.S)
                if log_list:
                    pass
                else:
                    cprint.error_p("nose output log format wrong!")
            else:
                cprint.error_p("No case found or something unknow happen!")
                return 1


            cases = re.findall(r'(#\d+\s+[\w.]+\s+[.]+\s+.*?[\r\n]+(?:ok|FAIL))(?:[\s\r\n]|$)', log_list[0], re.S | re.I)

            cprint.debug_p('Total cases: ' + str(len(cases)))

            total_cases = 0
            pass_cases = 0
            fail_cases = 0
            for case in cases:
                r = re.match(r'#(?P<index>\d+)\s+(?P<name>\w+)[\w.]+\s+[.]+\s+.*?[\r\n]+(?P<result>\w+)(?:[\r\n]+|$)', case, re.S)
                if r:
                    total_cases += 1    
                else:
                    continue

                if r.group('result') == 'ok':
                    result = 'pass'
                    pass_cases += 1
                    cprint.notice_p(r.group('index').ljust(5) + ': ' + r.group('name').ljust(40, '.') + result)
                else:
                    result = 'fail'
                    fail_cases += 1
                    cprint.error_p(r.group('index').ljust(5) + ': ' + r.group('name').ljust(40, '.') + result)

            #add fail cases to related suite


            #give a simple report
            cprint.common_p("Total: {}".format(total_cases))
            cprint.notice_p("pass : {}".format(pass_cases))
            cprint.error_p("fail : {}".format(fail_cases))

            with decimal.localcontext() as ctx:
                ctx.prec = 2
                if total_cases > 0:
                    cprint.common_p('Success Rate: '.ljust(20) + "%.2f" % (pass_cases * 100.0 / total_cases) + '%')
                else:
                    cprint.common_p('Success Rate:'.ljust(20) + '0.00%')


      
    def do_run(self, arg, opts=None):
        self.__clean_testlog()

        if re.match(r'^\d{8}$', arg, re.S):
            my_system_full_output("nosetests {} -s --exe".format(self.cases[arg]['case_dir'] + self.cases[arg]['case_name']))
            common_APIs.dir_copy(self.__get_tmp_dir(), self.config_file.get("system", "result_dir") + self.dir_separator + 'default' + self.dir_separator)


        elif os.path.isdir(arg) or (re.match(r'\d+', arg, re.S) and int(arg) < len(self.suites)):
            self.last_suite_name = arg if os.path.isdir(arg) else self.suites[int(arg)]
            log_dir = self.__get_suite_dir(self.last_suite_name)

            try:
                os.mkdir(log_dir)
            except Exception as er:
                cprint.error_p('Can not create log dir: %s\n[[%s]]' % (log_dir, str(er)))
                sys.exit()

            cmd_result = my_system_no_check("nosetests -w {} -v -s --exe --with-id --with-xunit --xunit-file={} --with-html-output --html-out-file={} 2>{}".format(self.last_suite_name, log_dir + 'result.xml', log_dir + 'result.html', log_dir + 'stdout.log'))
            common_APIs.dir_copy(self.__get_tmp_dir(), log_dir)

            self.__faild_cases_proc(log_dir + 'stdout.log')
                

        elif arg == 'again':
            pass

        else:
            cprint.error_p("unknow arg: %s" % arg)


    def help_runagain(self):  
        cprint.common_p("run last failed cases again")

      
    def do_runagain(self, arg, opts=None):
        self.__clean_testlog()

        log_dir = self.__get_suite_dir(self.last_suite_name)

        try:
            os.mkdir(log_dir)
        except Exception as er:
            cprint.error_p('Can not create log dir: %s\n[[%s]]' % (log_dir, str(er)))
            sys.exit()

        my_system_no_check("nosetests -w {} -v -s --failed --exe --with-xunit --xunit-file={} --with-html-output --html-out-file={}  2>{}".format(self.last_suite_name, log_dir + 'result.xml', log_dir + 'result.html', log_dir + 'stdout.log'))
        common_APIs.dir_copy(self.__get_tmp_dir(), log_dir)

        self.__faild_cases_proc(log_dir + 'stdout.log')


    def help_creatsuite(self):  
        print("help_creatsuite")

      
    def do_creatsuite(self, arg, opts=None):  
        print("do_creatsuite")


    def help_addcase(self):  
        print("help_addcase")

      
    def do_addcase(self, arg, opts=None):  
        print("do_addcase")


    def help_delcase(self):  
        print("help_delcase")

      
    def do_delcase(self, arg, opts=None):  
        print("do_delcase")


    def help_showcase(self):  
        print("help_creatsuite")

 
    def do_showcase(self, arg, opts=None):  
        print("help_creatsuite")


    def help_showsuite(self):  
        print("help_creatsuite")

 
    def do_showsuite(self, arg, opts=None):  
        print("help_creatsuite")


    def help_givereport(self):  
        print("help_givereport")

      
    def do_givereport(self, arg, opts=None):  
        print("do_givereport")      


    def default(self, arg, opts=None):
        try:
            subprocess.call(arg, shell=True)
        except:
            pass       

 
    def emptyline(self):
        pass

      
    def help_exit(self):
        print("Will exit CTS")

      
    def do_exit(self, arg, opts=None):
        if os.path.exists(self.config_file.get("system", "case_dir") + self.dir_separator + '.noseids'):
            os.remove(self.config_file.get("system", "case_dir") + self.dir_separator + '.noseids')
        LOG.p.info("Goodbye!!!")
        sys.exit()  



def sys_proc(action="default"):
    global thread_ids
    thread_ids = []
    for th in thread_list:
        thread_ids.append(threading.Thread(target=th[0], args=th[1:]))

    for th in thread_ids:
        th.setDaemon(True)        
        th.start()
        time.sleep(0.1)

    #for th in thread_ids:        
    #    th.join() 


def sys_init():
    LOG.p.info("Let's go!!!")


def sys_cleanup():
    pass


if __name__ == '__main__':
    #sys log init
    LOG = MyLogger(__name__ + ".log", clevel=logging.DEBUG, rlevel=logging.WARN)

    cprint = cprint(__name__)
    
    #arg init
    arg_handle = ArgHandle("arg")
    arg_handle.run()

    sys_init()


    global thread_list
    thread_list = []
    if arg_handle.get_args('cmdloop') or True:
 
        sys_proc()

        #cmd loop    
        #signal.signal(signal.SIGINT, lambda signal, frame: print("%s[32;2m%s%s[0m" % (chr(27), '\nExit CLI: CTRL+Q, Exit SYSTEM: exit', chr(27))))
        my_cmd = MyCmd()
        my_cmd.cmdloop()


    else:
        pass


        
        

        
        
        
        
        
        
        
