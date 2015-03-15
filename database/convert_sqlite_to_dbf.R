#!/usr/bin/Rscript

# R script to convert SQL file to DBF file

rm(list=ls()) 

####################################### read SQL file ##################################################
library("RSQLite")

in_fname = 'census_county_clip_joined'

setwd("/Users/BGhimire/data_science_large_data/location_finder/census_county_map")

## connect to db
con <- dbConnect(drv="SQLite", dbname=paste(in_fname,".db",sep=''))

## list all tables
tables <- dbListTables(con)

## exclude sqlite_sequence (contains table information)
tables <- tables[tables != "sqlite_sequence"]

lDataFrames <- vector("list", length=length(tables))

## create a data.frame for each table
for (i in seq(along=tables)) {
  lDataFrames[[i]] <- dbGetQuery(conn=con, statement=paste("SELECT * FROM '", tables[[i]], "'", sep=""))
}
##########################################################################################################

####################################### write DBF file ##################################################
library(foreign)

out_fname = paste(in_fname,".dbf",sep='')
write.dbf(lDataFrames[[1]], file=out_fname)

##########################################################################################################