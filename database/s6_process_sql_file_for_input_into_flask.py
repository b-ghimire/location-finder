import sqlite3

def combine_data(census_sql_fpath, in_census_sql_db_fname, out_sql_db_fname):
    # this function combines census, labor and health data sql tables into a single sql table for input into python flask
    ###################################################################################################################
    ###################################################################################################################

    con=sqlite3.connect(census_sql_fpath + in_census_sql_db_fname)

    # This will cause cur to return str instead of automatically trying to decode the str with the UTF-8
    # if this is not done the following error occurs when reading the data using fetchall()
    # error: sqlite3.operationalerror could not decode to utf-8 column
    con.text_factory = str

    # to read data as list of tuples
    con.row_factory = sqlite3.Row

    cur=con.cursor()
    query='SELECT noByAgeAndEmploymentAbove16yrs from census_data'
    query = '''

    SELECT
    County_Name,
    County_ID,
    STATE_NAME,
    State_ID,
    ROUND( totPop/CENSUSAREA, 2 ) AS popDensity,
    CAST (medianEarnings AS REAL),
    CAST( medianAge AS REAL),
    CAST( avgHouseholdSize AS REAL),
    ROUND( CAST(totalVacantHousingUnits AS REAL) / CAST(totalHousingUnits AS REAL) * 100, 2) AS percVancantHousingUnits,
    ROUND( (CAST(noBachelor AS REAL) + CAST(noGraduate AS REAL))/ CAST(noOfEducAndNotEduc AS REAL) * 100, 2) AS percBachelorEducAndHigher,
    CAST(rentAsPercOfHouseholdIncome AS REAL),
    unemploymentRate,
    diabetics,
    obesity,
    inactivity

    from
    census_data, table_labor, table_diabetics, table_obesity, table_inactivity

    where
    census_data.State_ID=table_labor.stateFIPSCode AND
    census_data.County_ID=table_labor.countyFIPSCode AND

    census_data.State_ID=table_diabetics.stateFIPSCode AND
    census_data.County_ID=table_diabetics.countyFIPSCode AND

    census_data.State_ID=table_obesity.stateFIPSCode AND
    census_data.County_ID=table_obesity.countyFIPSCode AND

    census_data.State_ID=table_inactivity.stateFIPSCode AND
    census_data.County_ID=table_inactivity.countyFIPSCode
    '''

    cur.execute(query)

    data = cur.fetchall()

    con.close()
    ###################################################################################################################
    ###################################################################################################################


    # writing data to sql file
    ###################################################################################################################
    ###################################################################################################################

    # set sql connection
    con = sqlite3.connect(census_sql_fpath + out_sql_db_fname)

    # get cursor
    cursor = con.cursor()

    # create table
    query='''
    CREATE TABLE TableReloc

    (CountyName TEXT,
    CountyFIPSCode TEXT,
    StateName TEXT,
    StateFIPSCode TEXT,
    popDensity REAL,
    medianEarnings REAL,
    medianAge REAL,
    avgHouseholdSize REAL,
    percVancantHousingUnits REAL,
    percBachelorEducAndHigher REAL,
    rentAsPercOfHouseholdIncome REAL,
    unemploymentRate REAL,
    diabeticsRate REAL,
    obesityRate REAL,
    inactivityRate REAL)
    '''

    cursor.execute(query)

    # create query to insert
    query = """
    INSERT INTO TableReloc
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # execute sql query
    cursor.executemany(query, data)

    # close cursor
    cursor.close()

    # commit transaction
    con.commit()

    # close connection
    con.close()
    ###################################################################################################################
    ###################################################################################################################


if __name__ == '__main__':
    census_sql_fpath = '/Users/BGhimire/data_science_large_data/location_finder/census_county_map/'
    in_census_sql_db_fname = 'census_county_clip_joined.db'
    out_sql_db_fname = 'census_county_clip_joined_flask.db'

    combine_data(census_sql_fpath, in_census_sql_db_fname, out_sql_db_fname)