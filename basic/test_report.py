'''
Created on 2017-11-23
'''
import os
import shutil
import win32com.client

def get_column(column='A'):
    '''
    column: one letter string. 
    '''
    return ord(column) - ord('A') + 1


fields_COLUMN = {
              'test_suite'         : get_column('A'),
              'test_case'           : get_column('B'),
              'test_result'         : get_column('C'),
              'test_notes'          : get_column('D'),
              'execution_time'      : get_column('E'),
              'tester'               : get_column('F'),
              }
FIRST_ROW = 4


class test_report():
    '''
    classdocs
    '''
    def __init__(self):
        '''
        report_name: string. please use a full path.
        '''
        self.report_name = ""
        self.tc_counter = 0
    
    
    def set_config(self, report_name):
        '''
        Initial the report name and move the pointer of the next item to the first line.
        Note: Call this function for one report_name file for one time. You can call clear_file() to clear the report.
        
        report_name: the full path and name for the report
        '''
        if self.report_name == report_name: #Don't call this function  for one report_name file for the second time.
            return
        
        self.report_name = report_name
        self.tc_counter = 0
    
    
    def clear_file(self):
        '''
        Clear all the items of test cases in the report and  move the pointer of the next item to the first line. 
        Don't call this function unless you really want to discard the items in the report.
        Note: this function will take 10+ seconds if there are hundreds of items.
         
        '''
        ################open the file
        msg = "The tool is generating file for test report according to the file for test plan, please wait." + 5*'#'
        print msg
        work_book = easyExcel(self.report_name)
        sheetName = work_book.xlBook.Sheets(1).Name
        rows = work_book.GetRows(sheetName)
        cols = work_book.GetColumns(sheetName)
        
        for ir in range(rows + 1):
            if ir < FIRST_ROW:
                continue
            for ic in range(cols):
                work_book.setCell(sheetName, ir+1, ic+1, '')
        
        ################Save the file
        work_book.save()
        work_book.close()
        
        self.tc_counter = 0

    def parse_test_set(self):
        '''
        lResult: List.
        '''
        MAX_EMPTY_NUM = 1
        lResult = []

        xls = easyExcel(self.report_name)
        sheetName = xls.xlBook.Sheets(1).Name
        line = FIRST_ROW
        all_lines = xls.GetRows(sheetName)
        emptyLineNum = 0
        while emptyLineNum <= MAX_EMPTY_NUM:
            caseDict = {}
            test_suite = xls.getCell(sheetName, line, 'A')
            test_case = xls.getCell(sheetName, line, 'B')

            if None == test_case or test_case.strip() == '':
                line += 1
                emptyLineNum += 1
                continue
            if None == test_suite:
                test_suite = ''
            caseDict['test_case'] = test_case.strip()
            caseDict['test_suite'] = test_suite.strip()
            lResult.append((caseDict))
            line += 1

        xls.close()

        return lResult


    def update_one_row(self, newInfoDict, row_index):
        '''

        :param newInfoDict:
            fields_COLUMN = {
                  'test_suite'         : get_column('A'),
                  'test_case'           : get_column('B'),
                  'test_result'         : get_column('C'),
                  'test_notes'          : get_column('D'),
                  'execution_time'      : get_column('E'),
                  'tester'               : get_column('F'),
                  }
        :param index:
        :return:
        '''

        row = FIRST_ROW+row_index
        for key in newInfoDict:
            value = newInfoDict[key]
            rol = fields_COLUMN[key]
            self.set_cell(row, rol, value)


    def insert_TC_rows(self, dictList, begin_row_index=0):
        '''

        :param dictList:
        :param begin_index:
        :return:
        '''
        work_book = easyExcel(self.report_name)
        sheetName = work_book.xlBook.Sheets(1).Name

        row = FIRST_ROW + begin_row_index
        for caseDict in dictList:
            col = fields_COLUMN['test_suite']
            work_book.setCell(sheetName, row, col, caseDict['test_suite'])
            col = fields_COLUMN['test_case']
            work_book.setCell(sheetName, row, col, caseDict['test_case'])
            row = row + 1

        ################Save the file
        work_book.save()
        work_book.close()



    def set_cell(self, row, col, text):
        '''
        Set text in the cell(row, col) of the sheet
        row: integer
        col: integer
        text:string
        '''
        work_book = easyExcel(self.report_name)
        sheetName = work_book.xlBook.Sheets(1).Name
        
        work_book.setCell(sheetName, row, col, text)
        
        ################Save the file
        work_book.save()
        work_book.close()
        

def copy_report_from_template(template_file, report_name, report_path=None):
    '''
    template_file: String. File name of the template file. It must be a absolute path.
    report_name: String. File name of the test report. It just a name string.
    report_path: String. The path to put the test report. If it's None, make it the same path with template_file. 
    return value: report_name, with it's absolute path.
    Notes:
        1.This function is to copy the file "template_file" to the file "report_name"
    '''
    #If report_path is None, make it the same path with template_file. 
    if report_path == None:
        report_path = os.path.split(os.path.realpath(template_file))[0] + os.path.sep
    report_name = report_path + report_name

    shutil.copy(template_file, report_name)
    return report_name


g_test_report = test_report()


class easyExcel:
    """A utility to make it easier to get at Excel.    Remembering
    to save the data is your problem, as is    error handling.
    Operates on one workbook at a time."""

    def __init__(self, filename=None):
        '''
        filename: should be with absolute path
        '''
        self.xlApp = win32com.client.DispatchEx('Excel.Application')
        if filename:
            self.filename = filename
            self.xlBook = self.xlApp.Workbooks.Open(filename)
        else:
            self.xlBook = self.xlApp.Workbooks.Add()
            self.filename = ''

    def save(self, newfilename=None):
        if newfilename:
            self.filename = newfilename
            self.xlBook.SaveAs(newfilename)
        else:
            self.xlBook.Save()

    def close(self):
        self.xlBook.Close(SaveChanges=0)
        del self.xlApp

    def GetRows(self, sheet):
        count = 0
        sht = self.xlBook.Worksheets(sheet)
        rs = sht.UsedRange.Rows
        for i in rs:
            count += 1
        return count

    def GetColumns(self, sheet):
        count = 0
        sht = self.xlBook.Worksheets(sheet)
        cs = sht.UsedRange.Columns
        for i in cs:
            count += 1
        return count

    def getCell(self, sheet, row, col):
        "Get value of one cell"
        # sht = self.xlBook.Worksheets(sheet)
        #  return sht.Cells(row, col).Value

        if sheet:
            sht = self.xlBook.Worksheets(sheet)
        else:
            sht = self.xlApp.ActiveSheet
        return sht.Cells(row, col).Value

    def setCell(self, sheet, row, col, value):
        "set value of one cell"
        # sht = self.xlBook.Worksheets(sheet)
        # sht.Cells(row, col).Value = value         

        if sheet:
            sht = self.xlBook.Worksheets(sheet)
        else:
            sht = self.xlApp.ActiveSheet

        sht.Cells(row, col).Value = value

    def getRange(self, sheet, row1, col1, row2, col2):
        "return a 2d array (i.e. tuple of tuples)"
        sht = self.xlBook.Worksheets(sheet)
        return sht.Range(sht.Cells(row1, col1), sht.Cells(row2, col2)).Value

    def addPicture(self, sheet, pictureName, Left, Top, Width, Height):
        "Insert a picture in sheet"
        sht = self.xlBook.Worksheets(sheet)
        sht.Shapes.AddPicture(pictureName, 1, 1, Left, Top, Width, Height)

    def copySheet(self, before):
        "copy sheet"
        shts = self.xlBook.Worksheets
        shts(1).Copy(None, shts(1))

    def getActiveSheet(self):
        return self.xlApp.ActiveSheet


if __name__ == '__main__':
#    import win32api
#    e_msg = win32api.FormatMessage(-2147352567)
#    print e_msg

#    execution_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#    print execution_time

    pass

    