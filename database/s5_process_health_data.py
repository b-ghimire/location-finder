# this script downloads the CDC (health) excel file, and converts the excel file to sql database

import xlrd
import sqlite3
import os

class processHealthData(object):

    def __init__(self, health_data_fpath, in_health_excel_fname, out_health_sql_fname, health_vars, health_varname):

        self.health_data_fpath = health_data_fpath
        self.in_health_excel_fname = in_health_excel_fname
        self.out_health_sql_fname = out_health_sql_fname
        self.health_vars = health_vars
        self.health_varname = health_varname

    def downloadHealthData(self):
        # this function downloads health data

        health_data_http_link = self.health_vars[self.health_varname][2]
        os.environ['health_data_http_link'] = health_data_http_link # passing variable from python to bash
        os.environ['health_data_fpath'] = self.health_data_fpath # passing variable from python to bash
        os.environ['in_health_excel_fname'] = self.in_health_excel_fname # passing variable from python to bash
        if not os.path.exists(self.health_data_fpath + self.in_health_excel_fname):
            # download file
            os.system('wget -O ${health_data_fpath}${in_health_excel_fname} ${health_data_http_link}${in_health_excel_fname}')

    def healthDataToSql(self):
        # this function converts excel to sql

        # open workbook
        book = xlrd.open_workbook(self.health_data_fpath + self.in_health_excel_fname)
        excel_sheet_name = self.health_vars[self.health_varname][1]
        sheet = book.sheet_by_name(excel_sheet_name)

        # set sql connection
        con = sqlite3.connect (self.health_data_fpath + self.out_health_sql_fname)

        # get cursor
        cursor = con.cursor()

        # create table
        query='''
        CREATE TABLE table_%s
        (stateFIPSCode TEXT, countyFIPSCode TEXT, %s REAL)
        ''' % (self.health_varname, self.health_varname)

        cursor.execute(query)

        query = """
        INSERT INTO table_%s
        VALUES (?, ?, ?)
        """   % (self.health_varname)

        # iterate rows of xls file, starting at row 2 to skip the headers
        for row in range(2, sheet.nrows):
            FIPSCode           = sheet.cell(row,1).value
            stateFIPSCode      = FIPSCode[0:2]
            countyFIPSCode     = FIPSCode[2:5]
            healthRate         = sheet.cell(row,56).value

            if stateFIPSCode!="":   # if not empty
                values = (stateFIPSCode, countyFIPSCode, healthRate)
                cursor.execute(query, values)   # execute query

        # close cursor
        cursor.close()

        # commit transaction
        con.commit()

        # close connection
        con.close()


if __name__ == "__main__":

    health_data_fpath='/Users/BGhimire/data_science_large_data/location_finder/census_county_map/'
    out_health_sql_fname='census_county_clip_joined.db'

    # stores the excel file name, excel sheet name and http link for the health files
    health_vars ={'diabetics':['DM_PREV_ALL_STATES.xls', 'diabetes prevalence','http://www.cdc.gov/diabetes/atlas/countydata/DMPREV/'],
                  'obesity':['OB_PREV_ALL_STATES.xls', 'obesity','http://www.cdc.gov/diabetes/atlas/countydata/OBPREV/'],
                  'inactivity':['LTPIA_PREV_ALL_STATES.xls', 'inactivity','http://www.cdc.gov/diabetes/atlas/countydata/LTPIAPREV/']
                 }

    health_varnames = ['diabetics', 'obesity', 'inactivity']

    for health_varname in health_varnames:
        in_health_excel_fname = health_vars[health_varname][0]

        process = processHealthData(health_data_fpath, in_health_excel_fname, out_health_sql_fname, health_vars, health_varname)
        process.downloadHealthData()
        process.healthDataToSql()



