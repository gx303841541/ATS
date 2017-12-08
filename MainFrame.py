#Boa:Frame:ManagerFrame

import wx
from basic.main_test_funcs import *

# try:
#     dirName = os.path.dirname(os.path.abspath(__file__))
# except:
#     dirName = os.path.dirname(os.path.abspath(sys.argv[0]))
#
# sys.path.append(os.path.split(dirName)[0])

## CLI below
import ConfigParser

from basic.test_report import *


def create(parent):
    return ManagerFrame(parent)

[wxID_MANAGERFRAME, wxID_MANAGERFRAMEBUTTON_LOADFILE, 
 wxID_MANAGERFRAMEBUTTON_LOAD_ALL_SAVE, wxID_MANAGERFRAMEBUTTON_RUN, 
 wxID_MANAGERFRAMEBUTTON_RUNSELECTED, wxID_MANAGERFRAMEGAUGE_PROCESSBAR, 
 wxID_MANAGERFRAMELISTCTRL_TESTCASESLIST, wxID_MANAGERFRAMELISTCTRL_TESTSTAT, 
 wxID_MANAGERFRAMEMAIN_PANEL, wxID_MANAGERFRAMESTATICTEXT_OUTPUT, 
 wxID_MANAGERFRAMESTATICTEXT_TCLIST, wxID_MANAGERFRAMETEXTCTRL_LOGWINDOW, 
 wxID_MANAGERFRAMETEXTCTRL_TEST_SET, 
] = [wx.NewId() for _init_ctrls in range(13)]

class ManagerFrame(wx.Frame):
    def _init_coll_listCtrl_TestcasesList_Columns(self, parent):
        # generated method, don't edit

        parent.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT,
              heading=u'Test Case', width=300)
        parent.InsertColumn(col=1, format=wx.LIST_FORMAT_LEFT,
              heading=u'Test Result', width=-1)

    def _init_coll_listCtrl_TestStat_Columns(self, parent):
        # generated method, don't edit

        parent.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT, heading=u'Total',
              width=-1)
        parent.InsertColumn(col=1, format=wx.LIST_FORMAT_LEFT,
              heading=u'Finished', width=-1)
        parent.InsertColumn(col=2, format=wx.LIST_FORMAT_LEFT, heading=u'Pass',
              width=-1)
        parent.InsertColumn(col=3, format=wx.LIST_FORMAT_LEFT, heading=u'Fail',
              width=-1)
        parent.InsertColumn(col=4, format=wx.LIST_FORMAT_LEFT, heading=u'Error',
              width=-1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_MANAGERFRAME, name=u'ManagerFrame',
              parent=prnt, pos=wx.Point(1896, 92), size=wx.Size(1004, 717),
              style=wx.DEFAULT_FRAME_STYLE, title='Test Manager')
        self.SetClientSize(wx.Size(988, 678))

        self.main_panel = wx.Panel(id=wxID_MANAGERFRAMEMAIN_PANEL,
              name=u'main_panel', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(988, 678), style=wx.TAB_TRAVERSAL)

        self.button_Run = wx.Button(id=wxID_MANAGERFRAMEBUTTON_RUN,
              label=u'Run All', name=u'button_Run', parent=self.main_panel,
              pos=wx.Point(224, 528), size=wx.Size(96, 48), style=0)
        self.button_Run.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.NORMAL,
              False, u''))
        self.button_Run.Bind(wx.EVT_BUTTON, self.OnButton_RunButton,
              id=wxID_MANAGERFRAMEBUTTON_RUN)

        self.button_load_all_save = wx.Button(id=wxID_MANAGERFRAMEBUTTON_LOAD_ALL_SAVE,
              label=u'Load All and Save', name=u'button_load_all_save',
              parent=self.main_panel, pos=wx.Point(25, 382), size=wx.Size(111,
              30), style=0)
        self.button_load_all_save.Bind(wx.EVT_BUTTON,
              self.OnButton_LoadAllButton,
              id=wxID_MANAGERFRAMEBUTTON_LOAD_ALL_SAVE)

        self.button_LoadFile = wx.Button(id=wxID_MANAGERFRAMEBUTTON_LOADFILE,
              label=u'Load ...', name=u'button_LoadFile',
              parent=self.main_panel, pos=wx.Point(24, 425), size=wx.Size(112,
              30), style=0)
        self.button_LoadFile.Bind(wx.EVT_BUTTON, self.OnButton_LoadFileButton,
              id=wxID_MANAGERFRAMEBUTTON_LOADFILE)

        self.button_RunSelected = wx.Button(id=wxID_MANAGERFRAMEBUTTON_RUNSELECTED,
              label=u'Run Selected', name=u'button_RunSelected',
              parent=self.main_panel, pos=wx.Point(88, 536), size=wx.Size(112,
              40), style=0)
        self.button_RunSelected.Show(True)
        self.button_RunSelected.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL,
              wx.NORMAL, False, u'Calibri'))
        self.button_RunSelected.Bind(wx.EVT_BUTTON,
              self.OnButton_RunSelectedButton,
              id=wxID_MANAGERFRAMEBUTTON_RUNSELECTED)

        self.textCtrl_LogWindow = wx.TextCtrl(id=wxID_MANAGERFRAMETEXTCTRL_LOGWINDOW,
              name=u'textCtrl_LogWindow', parent=self.main_panel,
              pos=wx.Point(504, 160), size=wx.Size(464, 480),
              style=wx.TE_LINEWRAP | wx.TE_MULTILINE, value=u'')
        self.textCtrl_LogWindow.SetEditable(False)
        self.textCtrl_LogWindow.Bind(wx.EVT_LEFT_DCLICK,
              self.OnTextCtrl_LogWindowLeftDclick)

        self.staticText_TClist = wx.StaticText(id=wxID_MANAGERFRAMESTATICTEXT_TCLIST,
              label=u'Test Cases List', name=u'staticText_TClist',
              parent=self.main_panel, pos=wx.Point(16, 8), size=wx.Size(81, 14),
              style=0)

        self.staticText_Output = wx.StaticText(id=wxID_MANAGERFRAMESTATICTEXT_OUTPUT,
              label=u'Log Output', name=u'staticText_Output',
              parent=self.main_panel, pos=wx.Point(504, 133), size=wx.Size(64,
              14), style=0)

        self.textCtrl_test_set = wx.TextCtrl(id=wxID_MANAGERFRAMETEXTCTRL_TEST_SET,
              name=u'textCtrl_test_set', parent=self.main_panel,
              pos=wx.Point(144, 430), size=wx.Size(344, 22), style=0,
              value=u'')

        self.gauge_ProcessBar = wx.Gauge(id=wxID_MANAGERFRAMEGAUGE_PROCESSBAR,
              name=u'gauge_ProcessBar', parent=self.main_panel,
              pos=wx.Point(500, 40), range=100, size=wx.Size(464, 24),
              style=wx.GA_HORIZONTAL)
        self.gauge_ProcessBar.SetBezelFace(3)
        self.gauge_ProcessBar.SetShadowWidth(3)

        self.listCtrl_TestStat = wx.ListCtrl(id=wxID_MANAGERFRAMELISTCTRL_TESTSTAT,
              name=u'listCtrl_TestStat', parent=self.main_panel,
              pos=wx.Point(504, 76), size=wx.Size(464, 50), style=wx.LC_REPORT)
        self._init_coll_listCtrl_TestStat_Columns(self.listCtrl_TestStat)

        self.listCtrl_TestcasesList = wx.ListCtrl(id=wxID_MANAGERFRAMELISTCTRL_TESTCASESLIST,
              name=u'listCtrl_TestcasesList', parent=self.main_panel,
              pos=wx.Point(24, 32), size=wx.Size(432, 320), style=wx.LC_REPORT)
        self._init_coll_listCtrl_TestcasesList_Columns(self.listCtrl_TestcasesList)
        self.listCtrl_TestcasesList.Bind(wx.EVT_LIST_ITEM_SELECTED,
              self.OnListCtrl_TestcasesListListItemSelected,
              id=wxID_MANAGERFRAMELISTCTRL_TESTCASESLIST)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.__CLI_init__()

    def __CLI_init__(self, config_file='config.ini'):
        result = sys_init(config_file)
        if result != '':
            self.GUI_update_log_window(result)
            msg = 'Something missing and this tool is not available. Please fix the issue and try again'
            self.GUI_update_log_window(result)
            return


        self.log_win_dclick = False
        self.all_TC_tuple_list = []
        self.selected_TC_list = []
        self.selected_TC_index = -1

        self.config_file_name = config_file
        self.config_file = ConfigParser.ConfigParser()
        g_main_test_paras.config_file = self.config_file
        self.config_file.read(config_file)
        self.case_re = r'^ats_\d{8}_\w+_test\.py$'

        # create log dir is not exist
        self.log_dir = self.config_file.get("system", "result_dir")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        #load test set
        rootfolder = "./testcases/"
        self.all_local_TCs = get_TC_files(rootfolder)
        tcset_file = self.config_file.get("system", "test_set_file")
        self.LoadTCsetFile(tcset_file)
        #self.textCtrl_LogWindow.SetInsertionPoint(-1)

    def GUI_update_cases_list(self):

        rootfolder = "./testcases/"
        file_filter = "*_test.*"
        self.file_filter = file_filter

        self.selected_TC_index = -1
        self.listCtrl_TestcasesList.DeleteAllItems()

        # try:
        for tc_name in self.TC_list:
            entry = [tc_name, '']
            self.listCtrl_TestcasesList.Append(entry)

        self.button_RunSelected.Enable(False)

    def GUI_update_log_window(self, msg):
        format_msg = ' '+msg+'\n'
        if self.log_win_dclick:
            self.textCtrl_LogWindow.Freeze()
            (curSelectionStart, curSelectionEnd) = self.textCtrl_LogWindow.GetSelection()
            self.textCtrl_LogWindow.AppendText(format_msg)
            self.textCtrl_LogWindow.SetInsertionPoint(self.curCaretPosition)
            self.textCtrl_LogWindow.SetSelection(curSelectionStart, curSelectionEnd)
            self.textCtrl_LogWindow.Thaw()
        else:
            self.textCtrl_LogWindow.AppendText(format_msg)

        #self.textCtrl_LogWindow.AppendText(format_msg)


    def GUI_enable(self, isRunning):
        toEnable = (not isRunning)
        self.button_RunSelected.Enable(toEnable)
        self.button_Run.Enable(toEnable)
        self.button_load_all_save.Enable(toEnable)
        self.button_LoadFile.Enable(toEnable)
        self.textCtrl_test_set.Enable(toEnable)

    def GUI_update_test_result(self, TC_status_list):
        for TC_status in TC_status_list:
            index = 0
            for tc_dict in self.all_TC_tuple_list:
                if tc_dict['test_case'] == TC_status[0]:
                    #self.listCtrl_TestcasesList.GetItem(index, 1).SetText(TC_status[1])
                    self.listCtrl_TestcasesList.SetStringItem(index, 1, TC_status[1])
                    break
                index = index + 1
        pass

    def GUI_clear_test_result(self):
        totalNum = self.listCtrl_TestcasesList.GetItemCount()
        for index in range(0, totalNum):
            #self.listCtrl_TestcasesList.GetItem(index, 1).SetText('')
            self.listCtrl_TestcasesList.SetStringItem(index, 1, '')

    def PercentageShow(self, totalNum, passedNum, failNum, errorlNum):
        self.listCtrl_TestStat.DeleteAllItems()
        if 0 == totalNum:
            entry = [0, 0, 0, 0, 0]
            self.listCtrl_TestStat.Append(entry)
            self.gauge_ProcessBar.SetValue(0)
            return False

        finishedNum = passedNum + failNum + errorlNum
        entry = [totalNum, finishedNum, passedNum, failNum, errorlNum]
        self.listCtrl_TestStat.Append(entry)

        percent = finishedNum*1.0 / totalNum
        percent = int(percent * 100)
        self.gauge_ProcessBar.SetValue(percent)

        return True


    def OnButton_LoadAllButton(self, event):
        event.Skip()
        #find all files

        #copy and save
        cur_path = os.getcwd() + '\\'
        tpl_name = cur_path + '\\test_plan_tpl.xls'
        tcset_file = 'all_test_cases.xls'
        copy_report_from_template(tpl_name, tcset_file, cur_path)
        tcset_file = cur_path + tcset_file

        #update the GUI
        self.LoadTCsetFile(tcset_file, False)


    def OnButton_LoadFileButton(self, event):
        wildcard = "Excel source (*.xls)|*.xls|" \
                   "All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a file", os.getcwd(),
                "", wildcard, wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            tcset_file = dialog.GetPath()
            self.LoadTCsetFile(tcset_file)

        dialog.Destroy()

    def LoadTCsetFile(self, tcset_file, load_tcset_file=True):
        g_test_report.set_config(tcset_file)
        if load_tcset_file:
            test_plan_TCs = g_test_report.parse_test_set()
            self.all_TC_tuple_list, self.not_run_TC_list = decide_testcases(test_plan_TCs, self.all_local_TCs)
            not_num = len(self.not_run_TC_list)
            if not_num > 0:
                msg = "%d test cases in the excel file don't exist in the local testcases folder" % (not_num)
                self.GUI_update_log_window(msg)
                for tpl in self.not_run_TC_list:
                    self.GUI_update_log_window(tpl['test_case'])
        else: #load all and save
            g_test_report.insert_TC_rows(self.all_local_TCs)
            self.all_TC_tuple_list = self.all_local_TCs
            self.not_run_TC_list = []

        #save to config.ini
        self.config_file.set(u'system', u'test_set_file', tcset_file)
        self.config_file.write(open(self.config_file_name, "w"))
        g_main_test_paras.all_TC_tuple_list = self.all_TC_tuple_list

        #update GUI
        self.textCtrl_test_set.ChangeValue(tcset_file)
        self.TC_list = []
        for fl in self.all_TC_tuple_list:
            self.TC_list.append(fl['test_case'])
        self.GUI_update_cases_list()

    def OnTextCtrl_LogWindowLeftDclick(self, event):
        self.log_win_dclick ^= True
        self.curCaretPosition = self.textCtrl_LogWindow.GetInsertionPoint()
        strLabel = 'Double click on log window to lock or unlock output:  '
        if self.log_win_dclick:
            strLabel += 'locked now!'
            #self.ResultLock.SetLabel(strLabel)
        else:
            strLabel += 'unlocked now!'
            #self.ResultLock.SetLabel(strLabel)
        print strLabel

        event.Skip()

    def OnButton_RunSelectedButton(self, event):
        #
        g_main_test_paras.all_TC_tuple_list = self.selected_TC_list
        self.GUI_clear_test_result()
        self.GUI_enable(True)
        self.damon_thread = running_thread(self)
        self.damon_thread.start()

    def OnButton_RunButton(self, event):
        g_main_test_paras.all_TC_tuple_list = self.all_TC_tuple_list
        self.GUI_clear_test_result()
        self.GUI_enable(True)
        self.damon_thread = running_thread(self)
        self.damon_thread.start()

    def OnListCtrl_TestcasesListListItemSelected(self, event):
        self.selected_TC_index = event.m_itemIndex
        self.selected_TC_list = []
        TC_name = self.listCtrl_TestcasesList.GetItem(self.selected_TC_index, 0).GetText()
        for tc_tuple in self.all_TC_tuple_list:
            if tc_tuple['test_case'] == TC_name:
                self.selected_TC_list.append(tc_tuple)
        self.button_RunSelected.Enable(True)



if __name__ == '__main__':
    #self.treeCtrl_TestcasesList
    # self.testcases_name = []
    # self.cases = {} #dict of Case classes with attributes filename, path, etc
    # self.suites = {} # dict of Suite classes with
    # self.suite_name_to_id = {}
    pass
