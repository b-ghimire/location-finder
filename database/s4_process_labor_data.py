# this script downloads the labor (employment) excel file, and converts the excel file to sql database

import xlrd
import sqlite3
import os

class processLaborData(object):

    def __init__(self, labor_data_fpath, in_labor_excel_fname, out_labor_sql_fname, labor_data_http_link):

        self.labor_data_fpath = labor_data_fpath
        self.in_labor_excel_fname = in_labor_excel_fname
        self.out_labor_sql_fname = out_labor_sql_fname
        self.labor_data_http_link = labor_data_http_link

    def downloadLaborData(self):
        # this function downloads labor data

        os.environ['labor_data_http_link'] = self.labor_data_http_link # passing variable from python to bash
        os.environ['labor_data_fpath'] = self.labor_data_fpath # passing variable from python to bash
        os.environ['in_labor_excel_fname'] = self.in_labor_excel_fname # passing variable from python to bash
        if not os.path.exists(self.labor_data_fpath + self.in_labor_excel_fname):
            # download file
            os.system('wget -O ${labor_data_fpath}${in_labor_excel_fname} ${labor_data_http_link}${in_labor_excel_fname}')

    def laborDataToSql(self):
        # this function converts excel to sql

        # open workbook
        book = xlrd.open_workbook(self.labor_data_fpath + self.in_labor_excel_fname)
        sheet = book.sheet_by_name("laucnty13")

        # set sql connection
        con = sqlite3.connect(self.labor_data_fpath + self.out_labor_sql_fname)

        # get cursor
        cursor = con.cursor()

        # create table
        query='''
        CREATE TABLE table_labor
        (stateFIPSCode TEXT, countyFIPSCode TEXT, unemploymentRate REAL)
        '''

        cursor.execute(query)

        query = """
        INSERT INTO table_labor
        VALUES (?, ?, ?)
        """

         # iterate rows of xls file, starting at row 2 to skip the headers
        for row in range(6, sheet.nrows): 
            stateFIPSCode      = sheet.cell(row,1).value
            countyFIPSCode     = sheet.cell(row,2).value
            unemploymentRate   = sheet.cell(row,9).value

            if stateFIPSCode!="":   # if not empty
                values = (stateFIPSCode, countyFIPSCode, unemploymentRate)
                cursor.execute(query, values)   # execute query

        # close cursor
        cursor.close()

        # commit transaction
        con.commit()

        # close connection
        con.close()


if __name__ == '__main__':

    labor_data_fpath='/Users/BGhimire/data_science_large_data/location_finder/census_county_map/'
    in_labor_excel_fname='laucnty13.xlsx'
    out_labor_sql_fname='census_county_clip_joined.db'
    labor_data_http_link='http://www.bls.gov/lau/'

    process = processLaborData(labor_data_fpath, in_labor_excel_fname, out_labor_sql_fname, labor_data_http_link)
    process.downloadLaborData()
    process.laborDataToSql()