---
layout: post
category: r
subcategory: "Database"
title: "Connect to PostgreSQL from RStudio"
ordinal: 1
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->

<hr />
## Create a connection file to include in all of your database code (saves some time)

  * description: basic connection to and query of the PostgreSQL database, use this as a source file R source code files.
  * created: 9/19/2014
  * author: Aaron D. Schroeder

### Create database driver
    library(RPostgreSQL) # load the database connection library

    drv <- dbDriver("PostgreSQL") # create instance of database driver

### Close all existing connections
    all_cons <- dbListConnections(drv)
    for(con in all_cons)
       {dbDisconnect(con)}

### Using the driver instance, create a new connection to the database and set the dbname, user and password variables
    con <- dbConnect(drv, dbname="sampleDb", host="localhost", port=5432
        , user="aaron", password="aaron")

<hr />
## View for all tables in the connected database

### connect to database
    source(file="~/R/pg_connect.R")

    dbname <- dbGetQuery(con, "SELECT table_catalog FROM information_schema.tables LIMIT 1")
    View(dbname)

### build query
    sql = paste("SELECT table_schema, table_name
                 FROM information_schema.tables
                 WHERE table_catalog = '", dbname, "'
                 AND table_schema NOT IN ('pg_catalog', 'files', 'information_schema')
                 ORDER BY table_schema, table_name", sep="")

### run query
    dbTables <- dbGetQuery(con, sql)

### display query results
    View(dbTables)

<hr />
## View all columns in a given table

### connect to database
    source(file="pg_connect.R")

### set schema and table variables
    schemaName = "sample_schema"
    tableName = "sample_table"

### build query
    sql = paste("SELECT column_name, data_type
                 FROM information_schema.columns
                 WHERE table_schema = '",schemaName,"'
                 AND table_name = '",tableName,"'", sep="")

### run query
    tableColumns <- dbGetQuery(con, sql)

### display query results
    View(tableColumns)

<hr />
## A simple query

### connect to database (set database in pg_connect.R, see above)
    source(file="pg_connect.R")

### build and run query
    myTable <- dbGetQuery(con, "SELECT  id, item, description
                                FROM sample_schema.sample_table")

### display query results
    View(myTable)
