'''
Python flask web application for selecting different locations (i.e., counties) in United States based on multiple factors.
The different factors are standardized using linear transformation
and then aggregated into a suitability index by weighting each standardized factor with user-specified importance weights.
'''

from flask import Flask, render_template, g, jsonify, request
from flask.ext.bootstrap import Bootstrap
import sqlite3
import json
import numpy as np
import pandas as pd

DATABASE='census_county_clip_joined_flask.db'

app=Flask(__name__)  # create (constructor) flask app object
bootstrap=Bootstrap(app) # create (constructor) bootstrap object
app.config.from_object(__name__)   # required for sqlite connection

@app.before_request
def before_request():
    g.db = sqlite3.connect(app.config['DATABASE'])

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

# performs weighted linear combinations (WLC)
@app.route('/WLC/', methods=['GET'])
def WLC():

    # weights for each variable based on user choices recorded from the front-end/browser
    factor_weights_list = [ float(request.args.get('popDensity')),
                            float(request.args.get('medianEarnings')),
                            float(request.args.get('medianAge')),
                            float(request.args.get('percVancantHousingUnits')),
                            float(request.args.get('percBachelorEducAndHigher')),
                            float(request.args.get('rentAsPercOfHouseholdIncome')),
                            float(request.args.get('unemploymentRate')),
                            float(request.args.get('diabeticsRate')),
                            float(request.args.get('inactivityRate'))]

    # getting all data as string
    query = "select CountyName, CountyFIPSCode, StateName, StateFIPSCode, PopDensity, MedianEarnings, MedianAge, PercVancantHousingUnits, PercBachelorEducAndHigher, RentAsPercOfHouseholdIncome, UnemploymentRate, DiabeticsRate, InactivityRate from TableReloc"
    cur = g.db.execute(query)
    varnames = cur.description   # census column names
    no_vars = len(varnames)  # no of census variables
    data_ListOfTuple_string = cur.fetchall()  # get all the data

    # getting only numeric data
    query = "select PopDensity, MedianEarnings, MedianAge, PercVancantHousingUnits, PercBachelorEducAndHigher, RentAsPercOfHouseholdIncome, UnemploymentRate, DiabeticsRate, InactivityRate from TableReloc"
    cur = g.db.execute(query)
    data_ListOfTuple_numeric = cur.fetchall()

    # convert to numpy array
    data_array_numeric = np.array(data_ListOfTuple_numeric)
    factor_weights_array = np.array(factor_weights_list)

    # linear standardization of variables
    data_array_numeric_std=(data_array_numeric-data_array_numeric.min(axis=0)) / (data_array_numeric.max(axis=0)-data_array_numeric.min(axis=0))

    # reverse/flip certain standardized variables
    subset_var_index = np.array([2, 5, 6, 7, 8])
    data_array_numeric_std[:,subset_var_index] = 1.0 - data_array_numeric_std[:,subset_var_index]

    # multiply by variable weights
    data_array_numeric_std_wts=data_array_numeric_std * factor_weights_array

    # weighted linear combination of the variables
    weighted_scores = data_array_numeric_std_wts.sum(axis=1)/factor_weights_array.sum(axis=0)   # scores range from 0 to 1

    # round to 2 decimal places
    weighted_scores = np.around(weighted_scores, decimals=2)

    # ranking the scores in descending order [highest score gets value of 1, second highest value of 2 and so on]
    df=pd.DataFrame({"weightedScores" : weighted_scores })      # convert numpy array to pandas dataframe
    df["rank"]=df['weightedScores'].rank(method='first', ascending=False)    # rank in descending order
    rank = np.array(df["rank"])     # convert pandas dataframe column to numpy array

    # converting list of tuples to dictionary of list
    census_data={}  # declare empty dictionary
    for index_var in range(no_vars):
        var_name = varnames[index_var][0]
        census_data[var_name]=[row[index_var] for row in data_ListOfTuple_string]   # convert list of tuples to dictionary of list
    cur.close()

    # ret_data is data returned to client (i.e., frontend)
    ret_data = census_data
    ret_data["weightedScores"]=weighted_scores.tolist()   # appending item to dictionary
    ret_data["rank"]=rank.tolist()   # appending item to dictionary
    ret_data["healthIndex"]=np.around(data_array_numeric_std[:,7], decimals=2).tolist()   # appending item to dictionary

    return jsonify(ret_data)

@app.route('/')
def index():
    return render_template('index.html')

if __name__=='__main__':
    app.run(debug=True)   # starting/launching web server

