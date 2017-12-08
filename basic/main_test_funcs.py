# -*- coding: utf-8 -*-

import re
import sys
import os
from fnmatch import fnmatch
import threading
import time
import copy
import pythoncom
from basic.suite import *
import shutil



def get_TC_files(rootfolder):
    dict_TCList = []
    file_filter = [r'^ats_\d{8}_\w+_test\.py$']
    items = os.listdir(rootfolder)
    items = sorted(items,key=str.lower)
    folders = []

    for item in items:
        if item[0]==".":
            continue
        itempath = os.path.join(rootfolder, item)
        if os.path.isfile(itempath):
            fileok=False
            for filter in file_filter:
                if re.match(filter, item, re.S):
                    fileok=True
                    break
            if fileok:
                start = itempath.find('/testcases/') + len('/testcases/')
                end = itempath.find(item)
                caseDict = {}
                caseDict['test_suite'] = itempath[start:end]
                caseDict['test_case'] = item[:-3]
                caseDict['TC_path'] =  itempath
                dict_TCList.append(caseDict)
        else:
            folders.append((item,itempath))
    pass
    for folder, itempath in folders:
        tmpFiles = get_TC_files(itempath)
        dict_TCList = dict_TCList + tmpFiles

    return dict_TCList


def decide_testcases(test_plan, local_testcases):
    '''
    test_plan: [{'test_case' : '', 'test_suite' : '', 'TC_path' : '',}],
            The value of test_suite is not always right. The value of TC_path is empty.
    local_testcases: [{'test_case' : '', 'test_suite' : '', 'TC_path' : '',}],
    return:
        same as local_testcases
    Note:
        pass
    '''
    to_run_list = []
    not_run_list = []

    for plan_tc in test_plan:
        local_exist = False
        for local_tc in local_testcases:
            if plan_tc['test_case'] == local_tc['test_case']:
                local_exist = True
                plan_tc['TC_path'] = local_tc['TC_path']
                plan_tc['test_suite'] = local_tc['test_suite']
                break
        if local_exist:
            to_run_list.append(plan_tc)
        else:
            not_run_list.append(plan_tc)

    return to_run_list, not_run_list



def sys_init(config_file_name):
    config_file = ConfigParser.ConfigParser()
    config_file.read(config_file_name)

    ats_path = config_file.get("system", "ats_path")
    if os.path.exists(ats_path + 'ats.pth'):
        pass
    elif os.path.exists(ats_path):
        shutil.copy(os.getcwd() + '/patch/ats.pth', ats_path)
    else:
        sys_error = "Dir: '%s' not found, your ATS env is not ready!" % (ats_path)
        return sys_error

    html_tool_path = config_file.get("system", "html_tool_path")
    if os.path.exists(html_tool_path):
        if os.path.exists(html_tool_path + 'htmloutput.py'):
            os.remove(html_tool_path + 'htmloutput.py')
        shutil.copy(os.getcwd() + '/patch/htmloutput.py', html_tool_path)
    else:
        sys_error = "Dir: '%s' not found, your ATS env is not ready!" % (html_tool_path)
        return sys_error

    return '' #success

class main_test_paras():
    def __init__(self):
        '''
        Please refer to g_tool_para in this module.
        Don't create your instance only when you re-set all the path.
        Notes:
            1. Use g_tool_para.init_tool_parameter() to set all the global parameters
               according to the special instance file.
        '''
        self.tool_path = os.getcwd() + "\\"
        self.all_TC_tuple_list = []
        self.config_file = None
        self.running_suite_path = self.tool_path + 'running_suite\\'
        self.suite_log_dir = ''
        self.test_report_file = ''

g_main_test_paras = main_test_paras()


class running_thread(threading.Thread):  # The timer class is derived from the class threading.Thread
    def __init__(self, frame):
        threading.Thread.__init__(self)
        self.frame = frame

    def run(self):  # Overwrite run() method, put what you want the thread do here
        create_running_suite(g_main_test_paras.all_TC_tuple_list, g_main_test_paras.running_suite_path)
        self.ATS_suite = Suite(config_file=g_main_test_paras.config_file, id=0, name=g_main_test_paras.running_suite_path, cases='', sub_suites='')
        g_main_test_paras.suite_log_dir = self.ATS_suite.get_suite_log_dir()
        g_main_test_paras.test_report_file = g_main_test_paras.suite_log_dir + 'result.html'

        self.test_daemon = threading.Thread(target=self.start_test, name='Test Daemon')
        self.monitor_daemon = threading.Thread(target=self.start_monitor, name='Monitor Daemon')

        self.test_daemon.start()
        self.monitor_daemon.start()

        while self.test_daemon.isAlive():
            time.sleep(0.5)
        while self.monitor_daemon.isAlive():
            time.sleep(0.5)

        #self.frame.Run_StopConfig()
        self.frame.GUI_enable(False)


    def start_test(self):
        # A thread should call below at the beginning if window COM is used.
        # In this tool, we use "win32com.client.Dispatch('Excel.Application')" in sag_report.py
        pythoncom.CoInitialize()
        #test cases list
        self.ATS_suite.run()

    def start_monitor(self):
        #test cases list
        all_TC_num = len(g_main_test_paras.all_TC_tuple_list)
        done_TC_num = 0
        # for i in range(1, 11):
        #     time.sleep(1)
        #     self.frame.PercentageShow(10, i, 0, 0)
        self.frame.PercentageShow(all_TC_num, 0, 0, 0)

        while all_TC_num > done_TC_num:
            time.sleep(2)
            TC_status_list = get_TC_stat_info(g_main_test_paras.test_report_file)
            if len(TC_status_list)> 0:
                stat_info = calc_stat_info(TC_status_list)
                if stat_info[0] > done_TC_num:
                    self.frame.PercentageShow(all_TC_num, stat_info[1], stat_info[2], stat_info[3])
                    self.frame.GUI_update_test_result(TC_status_list)
                    done_TC_num = stat_info[0]

#register_ProcessBar_func(self.PercentageShow)         #register processbar show func
#common functions

def create_running_suite(tpl_TC_list, suite_path):
    if os.path.exists(suite_path):
        shutil.rmtree(suite_path)
    os.mkdir(suite_path)
    for tpl_TC in tpl_TC_list:
        dstFile = suite_path + tpl_TC['test_case'] + '.py'
        shutil.copy(tpl_TC['TC_path'], dstFile)


from basic.HT_HTML_parser import *


def calc_stat_info(TC_stats_list):

    stat_info = {'pass': 0,
                'fail' : 0,
                'error': 0,
                 }
    for TC_status in TC_stats_list:
        stat_info[TC_status[1]] = stat_info[TC_status[1]] + 1

    totalNum = stat_info['pass'] + stat_info['fail'] + stat_info['error']
    status_list = [totalNum, stat_info['pass'], stat_info['fail'],stat_info['error']]
    return status_list

def get_TC_stat_info(test_report_file):
    '''

    :param test_report_file:
    :return:
    '''
    #Count Pass Fail Error Skip View
    html_name = r"C:\ATS\testcases\ats_result\_ATS_running_suite_-20171201_101917\result.html"
    #html_name = r"C:\ATS\testcases\ats_result\_ATS_running_suite_-20171130_144746\result.html"
    html_name = test_report_file
    if os.path.exists(html_name):
        htmlFile = open(html_name, 'r')
    else:
        return []

    content = htmlFile.read()
    parser = HT_HTML_parser()
    parser.feed(content)

    #try to get the test cases info
    type_index = 0
    info_type = ['test_case',  'result',  'error_msg']
    index_sum = len(info_type)
    TC_status_list = []
    search_go = False
    for buffer in parser.data:
        if buffer == 'Test Group/Test case':
            search_go = True
            continue
        if search_go:
            if type_index == 0:
                TC_tuple = []
            info = get_match_info(info_type[type_index], buffer)
            if info != '':
                type_index += 1
                type_index = type_index%index_sum
                TC_tuple.append(info)
                if type_index == 0:
                    if len(TC_tuple) < index_sum:
                        TC_tuple.append('Some infomation of test case missing in the result.html')
                    TC_status_list.append(TC_tuple)

    return TC_status_list


def get_match_info(info_type, buffer):
    '''

    :param info_type:  test_case, result, error_msg,
    :param buffer:
    :return:
    '''
    info_type_pattern = {'test_case': r'^(ats_\d{8}_\w+_test)$',
                         'result'    : r'^\s*(pass|fail|error|skip)\s*',
                         'error_msg' : r'^(\s*(ft|pt)\d{1,}\.\d{1,}: ats_.*)',
                         }

    info_pattern = info_type_pattern[info_type]
    pattern = re.compile(info_pattern, re.S)
    match = pattern.match(buffer)
    if match:
        info = match.group()
    else:
        info = ''
    if info_type == 'result':
        info = info.strip()

    return info

if __name__ == '__main__':
    stats_list = get_TC_stat_info('')
    for stats in stats_list:
        print stats[0], stats[1]
        #print stats[2]
    stat_list = calc_stat_info(stats_list)
    print stat_list