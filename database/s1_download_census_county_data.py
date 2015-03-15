# import library
import os

# download the county census map
census_county_map_fname='gz_2010_us_050_00_5m'
census_county_map_fpath='http://www2.census.gov/geo/tiger/GENZ2010/'
census_county_out_fpath='/Users/BGhimire/data_science_large_data/location_finder/census_county_map/'
os.environ['census_county_map_fname']=census_county_map_fname # passing variable from python to bash
os.environ['census_county_map_fpath']=census_county_map_fpath # passing variable from python to bash
os.environ['census_county_out_fpath']=census_county_out_fpath # passing variable from python to bash
if not os.path.exists(census_county_out_fpath+census_county_map_fname+'.zip'):
    # download file
    os.system('wget -O ${census_county_out_fpath}${census_county_map_fname}.zip ${census_county_map_fpath}${census_county_map_fname}.zip')
    # unzip census county map
    os.system('unzip ${census_county_out_fpath}${census_county_map_fname}.zip -d ${census_county_out_fpath}')
