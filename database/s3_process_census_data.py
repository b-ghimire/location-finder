# import library
import os


# install necessary packages
install_opt=0
if install_opt==1:
  os.system('sudo apt-get install python-numpy')
  os.system('sudo apt-get install python-scipy')
  os.system('sudo pip install pysal')
  os.system('sudo pip install pandas')


# loading necessary libraries
import urllib2
import pysal
import pandas
import sqlite3
import re
import numpy


class processCensusData(object):

    def __init__(self, census_county_out_fpath, census_county_map_fname, countycode_fpath, countycode_fname, statecode_fpath, statecode_fname, out_census_fname):
        self.census_county_out_fpath = census_county_out_fpath
        self.census_county_map_fname = census_county_map_fname
        self.out_census_fname = out_census_fname

        self.countycode_fpath = countycode_fpath
        self.countycode_fname = countycode_fname

        self.statecode_fpath = statecode_fpath
        self.statecode_fname = statecode_fname

    def downloadCensusData(self):
        ############# download census data ##########################
        ##############################################################

        os.environ['countycode_fname']=self.countycode_fname
        os.environ['countycode_fpath']=self.countycode_fpath
        if not os.path.exists(self.countycode_fname):
            os.system('wget ${countycode_fpath}${countycode_fname}')

        os.environ['statecode_fname']=self.statecode_fname
        os.environ['statecode_fpath']=self.statecode_fpath
        if not os.path.exists(self.statecode_fname):
            os.system('wget ${statecode_fpath}${statecode_fname}')

        #############################################################
        #############################################################


    def censusDbfToDataframe(self):
        ############convert census county dbf to dataframe #############
        ##############################################################

        # open dbf file
        dbf = pysal.open(self.census_county_out_fpath + self.census_county_map_fname + '.dbf')

        # print variables in object
        vars(dbf)

        # print table column names
        dbf.header

        # create dict (key value pairs) with column name as key and values as column items
        dict_census_county={col:dbf.by_col(col) for col in dbf.header}

        # converting dictionary to pandas dataframe
        df_census_county=pandas.DataFrame(dict_census_county)

        # adding new column to dataframe for census county, county id and state id
        GEO_ID=df_census_county['GEO_ID']
        df_census_county['STATE_ID']=numpy.nan  # column of NaN
        df_census_county['COUNTY_ID']=numpy.nan
        df_census_county['STATE_ID']=df_census_county['STATE_ID'].astype('str')
        df_census_county['COUNTY_ID']=df_census_county['COUNTY_ID'].astype('str')
        for index, item_geoid in enumerate(GEO_ID):
            df_census_county['STATE_ID'][index]=item_geoid[9:11]
            df_census_county['COUNTY_ID'][index]=item_geoid[11:14]

        # closing file
        dbf.close()

        return df_census_county

        ##############################################################
        ##############################################################


    def censusTextToDataframe(self):
        ############## convert census county and state code text files to dataframe ##########
        ##############################################################

        df_countycode = pandas.read_table(self.countycode_fname, sep=',', dtype=object)

        df_statecode = pandas.read_table(self.statecode_fname, sep='|', dtype=object)

        return df_countycode, df_statecode

        ##############################################################
        ##############################################################


    def joinCensusDataframes(self, df_census_county, df_countycode, df_statecode):
        ############## joining the dataframes #######################
        #############################################################
        # join table county code and state code dataframe
        df_merge1 = pandas.merge(df_countycode, df_statecode, left_on=['State ANSI'], right_on=['STATE'], how='left')

        # join census county with df_merge1 dataframe
        df_merge2 = pandas.merge(df_census_county, df_merge1, left_on=['STATE_ID','COUNTY_ID'], right_on=['State ANSI','County ANSI'], how='left')

        return df_merge2

        #############################################################
        #############################################################


    def scrapeCensusData(self, df_merge2):
        ################## scraping census data #####################
        #############################################################
        # census variables to add later: household income, educational attainment, travel time, health insurance, industry, earning, household income, family income, employment status, marital status

        # sf1 is the census id for the given survey
        census_vars_2010sf1 = {'totPop':['P0010001', 'sf1', '2010'],
                       	       'medianAge':['P0130001', 'sf1', '2010'],
                               'avgHouseholdSize':['P0170001', 'sf1', '2010'],
                               'totalHousingUnits':['H0030001', 'sf1', '2010'],
                               'totalVacantHousingUnits':['H0030003', 'sf1', '2010']
                              }

        # acs5 is the census id for the given survey
        census_vars_2012acs5 = {'rentAsPercOfHouseholdIncome': ['B25071_001E', 'acs5', '2012'],
                                'medianEarnings': ['B20002_001E', 'acs5', '2012'],
                                'noByAgeAndEmploymentAbove16yrs': ['B23001_001E', 'acs5','2012'],
                                'noOfEducAndNotEduc': ['B06009_001E', 'acs5', '2012'],
                                'noLessThanHighSch': ['B06009_002E', 'acs5', '2012'],
                                'noHighSch': ['B06009_003E', 'acs5', '2012'],
                                'noCollege': ['B06009_004E', 'acs5', '2012'],
                                'noBachelor': ['B06009_005E', 'acs5', '2012'],
                                'noGraduate': ['B06009_006E', 'acs5', '2012']
                               }

        # concatenate two dictionaries
        census_vars = dict(census_vars_2010sf1.items() + census_vars_2012acs5.items())

        df_merge3 = df_merge2
        counter=0

        # census key required for downloading the data
        census_key = ''   # get your own census key, and enter it here

        for censusVar in census_vars:

            counter=counter+1
            print censusVar

            censusObject = urllib2.urlopen("http://api.census.gov/data/"+census_vars[censusVar][2]+"/"+census_vars[censusVar][1]+"?key=+census_key+&get="+census_vars[censusVar][0]+"&for=county:*")
            censusData = censusObject.read()
            #print CensusData
            censusObject.close()

            # clean up the data
            censusStr=censusData
            censusStr=censusStr.replace('"','')
            censusStr=censusStr.replace('[','')
            censusStr=censusStr.replace(']','')
            censusStr=censusStr.replace('\n','')
            censusFields=re.split(',',censusStr)
            #print CensusFields

            # reshape and convert to dataframe
            censusFields_df=pandas.DataFrame(censusFields)  # convert to dataframe
            shape=(len(censusFields_df)/3, 3)   # +1 coz there is header row
            censusFields_reshape=censusFields_df.values.reshape( shape )  # reshaping (note output is array (i.e., not dataframe) even if input was dataframe)
            censusFields_reshape_df=pandas.DataFrame(censusFields_reshape, columns=[censusVar,'StateIden'+str(counter), 'CountyIden'+str(counter)])   # convert to dataframe
            censusFields_reshape_df=censusFields_reshape_df[1:] # removing first row as it is header name

            # table join
            df_merge3 = pandas.merge(df_merge3, censusFields_reshape_df, left_on=['STATE_ID','COUNTY_ID'], right_on=['StateIden'+str(counter),'CountyIden'+str(counter)], how='left')

        return df_merge3

        ############################################################################################################
        ############################################################################################################

    def dataframeToSql(self, df_merge3):
        #################### convert dataframe to sql file #########################################################
        ############################################################################################################

        # before writing to sql, replacing spaces in column names by underscore
        df_merge3.rename(columns=lambda x: x.replace(' ', '_'), inplace=True)

        col_names_array=df_merge3.columns.values
        for iCol, ColName in enumerate(col_names_array):
                if ColName == 'CENSUSAREA':
                    VarType = 'REAL'
                else:
                    VarType = 'TEXT'

                if iCol == 0:
                    query_varname = ColName+' '+VarType+','
                    insert_values = '?,'
                else:
                    query_varname = query_varname+' '+ColName+' '+VarType+','
                    insert_values = insert_values + '?,'

        # remove last comma (,) from string
        query_varname = query_varname[:-1]
        insert_values = insert_values[:-1]

        # connect to sql server
        con=sqlite3.connect(census_county_out_fpath+out_census_fname+'.db')
        con.text_factory = str  # setting text factory; this needs to be set otherwise data cannot be written

        # create table and specify column names and type
        query = "CREATE TABLE census_data ("+ query_varname +");"
        con.execute(query)
        con.commit()

        # converting pandas dataframe to list of tuples for writing to sql
        df_merge3['tuples_column']=df_merge3[col_names_array].apply(tuple, axis=1)  # create a new dataframe column of row tuples
        list_of_tuples=list(df_merge3['tuples_column'])   # converting tuple column to list of tuples for input to sql database

        # write data to sql
        stmt="INSERT INTO census_data VALUES ("+ insert_values+")"
        con.executemany(stmt,list_of_tuples)
        con.commit()

        # closing sql connection
        con.close()

        #############################################################################################################
        #############################################################################################################


    def sqlToDbf(self):
        ############################### calling R script to convert SQL file to DBF file ############################
        #############################################################################################################
        os.system('chmod 777 convert_sqlite_to_dbf.R')   # change file permissions
        os.system('./convert_sqlite_to_dbf.R')  # running R script
        #############################################################################################################
        #############################################################################################################


    def fileCopy(self):
        ############################## copying required files for the new joined shapefile ###########################
        #############################################################################################################
        os.environ['census_county_out_fpath'] = self.census_county_out_fpath # passing variable from python to bash
        os.environ['out_census_fname'] = self.out_census_fname # passing variable from python to bash
        os.environ['census_county_map_fname']=census_county_map_fname # passing variable from python to bash
        os.system('cp ${census_county_out_fpath}${census_county_map_fname}.shp ${census_county_out_fpath}${out_census_fname}.shp')
        os.system('cp ${census_county_out_fpath}${census_county_map_fname}.shx ${census_county_out_fpath}${out_census_fname}.shx')
        os.system('cp ${census_county_out_fpath}${census_county_map_fname}.prj ${census_county_out_fpath}${out_census_fname}.prj')
        #os.system('cp ${census_county_out_fpath}${census_county_map_fname}.xml ${census_county_out_fpath}${out_census_fname}.xml')
        #############################################################################################################
        #############################################################################################################


if __name__ == '__main__':

    # census county map
    census_county_map_fname='census_county_clip'
    census_county_out_fpath='/Users/BGhimire/data_science_large_data/location_finder/census_county_map/' # since file is large store in different path rather than present working directory
    out_census_fname = census_county_map_fname+'_joined'

    # county codes file
    countycode_fname='national_county.txt'
    countycode_fpath='http://www.census.gov/geo/reference/codes/files/'

    # state codes file
    statecode_fname='state.txt'
    statecode_fpath='http://www.census.gov/geo/reference/docs/'


    process=processCensusData(census_county_out_fpath, census_county_map_fname, countycode_fpath, countycode_fname, statecode_fpath, statecode_fname, out_census_fname)

    process.downloadCensusData()

    df_census_county = process.censusDbfToDataframe()

    df_countycode, df_statecode = process.censusTextToDataframe()

    df_merge2 = process.joinCensusDataframes(df_census_county, df_countycode, df_statecode)

    df_merge3 = process.scrapeCensusData(df_merge2)

    process.dataframeToSql(df_merge3)

    process.sqlToDbf()

    process.fileCopy()