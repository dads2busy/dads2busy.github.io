---
layout: post
category: r
subcategory: "Database"
title: "RPostgreSQL Commands"
ordinal: 2
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->

<HTML>
<h2><a name="Summary_of_basic_usage"></a>Summary of basic usage<a href="#Summary_of_basic_usage" class="section_anchor"></a></h2>
<p>1. dbDriver(drv, ...) instantiates the driver object. Eg.  </p><pre class="prettyprint">drv &lt;- dbDriver(&quot;PostgreSQL&quot;)</pre>
<p>2.dbConnect(drv,...) creates and opens a connection to the database implemented by the driver drv. Connection string should be specified with parameters like user, password, dbname, host, port, tty and options. For more details refer to the documentation. Eg. </p><pre class="prettyprint">con &lt;- dbConnect(drv, dbname=&quot;tempdb&quot;)</pre>
<p>3.dbListConnection(drv, ...) provides List of connections handled by the driver Eg. </p><pre class="prettyprint">dbListConnections(drv)</pre>
<p>4.dbGetInfo(dbObject, ...) and summary(dbObject) returns information about the dbObject (driver, connection or resultSet).  Eg. </p><pre class="prettyprint">dbGetInfo(drv)
summary(con)</pre>
<p>5.dbSendQuery(con, statement, ...) submits one statement to the database.  Eg.  </p><pre class="prettyprint">dbSendQuery(con,&quot;select * from TableName&quot;)</pre>
<p>6.fetch(rs,n, ...) fetches the next n elements from the result set.  Eg.  </p><pre class="prettyprint">fetch(rs,n=-1) ## return all elements
fetch(rs,n=2) ##returns last 2 elements in record set.</pre>
<p>7. dbGetQuery(con,statement, ...) submits, execute, and extract output in one operation. Eg. </p><pre class="prettyprint">result <- dbGetQuery(con,&quot;select * from TableName&quot;)</pre>
<p>8. dbGetException(con, ...) returns the status of the last DBMS statement sent over the connection.  Eg.  </p><pre class="prettyprint">dbGetException(con)</pre>
<p>9. dbListResults(con, ...) returns the resultsets active on the given connection. Please note that the current RPostgreSQL package can handle only one resultset per connection (which may change in the future). Eg.  </p><pre class="prettyprint">dbListResults(con)</pre>
<p>10. dbListTables(con, ...) returns the list of tables available on the connection.  Eg.  </p><pre class="prettyprint">dbListTables(con)</pre>
<p>11. dbExistsTable(con, TableName, ...) checks whether a particular table exists on the given connection. Returns a logical. Eg.  </p><pre class="prettyprint">dbExistsTable(con,&quot;TableName&quot;)</pre>
<p>12. dbRemoveTable(con, TableName, ...) removes the specified table on the connection. Returns a logical indicating operation succeeded or not.  Eg. </p><pre class="prettyprint">dbRemoveTable(con,&quot;TableName&quot;)</pre>
<p>13. dbListFields(con, TableName, ...) returns the list of column names (fields) in the table. ***DOES NOT SEEM TO WORK***  Eg.  </p>
<pre class="prettyprint">dbListFields(con,&quot;TableName&quot;)</pre>
<p>14. dbColumnInfo(res, ...) produces a query that describes the output of the query. Eg.  </p><pre class="prettyprint">dbColumnInfo(rs)</pre>
<p>15. dbReadTable(conn, name, ...) imports the data stored remotely in the table name on connection conn. Use the field row.names as the row.names attribute of the output data.frame. Returns a data.frame. Eg.  </p><pre class="prettyprint">dframe &lt;-dbReadTable(con,&quot;TableName&quot;). </pre>
<p>16. dbWriteTable(conn, name, value, ...) writes the contents of the dataframe value into the table name specified. Returns a logical indicating whether operation succeeded or not.  Eg.  </p><pre class="prettyprint">dbWriteTable(con,&quot;newTable&quot;,dframe)</pre>
<p>17. dbGetStatement(res, ...) returns the DBMS statement associated with the result. Eg.  </p><pre class="prettyprint">dbGetStatement(rs)</pre>
<p>18. dbGetRowsAffected(res, ...) returns the rows affected the executed statement. If no rows are affected, &quot;-1&quot; is returned. Eg.  </p><pre class="prettyprint">dbGetRowsAffected(rs)</pre>
<p>19. dbHasCompleted(res, ...) returns a logical to indicate whether an operation is completed or not. Eg.  </p><pre class="prettyprint">dbHasCompleted(rs)</pre>
<p>20.dbGetRowCount(res, ...) returns number of rows fetched so far. Eg.  </p><pre class="prettyprint">dbGetRowCount(rs)</pre>
<p>21.dbBeginTransaction begins the PostgreSQL transaction. dbCommit commits the transaction while dbRollback rolls back the transaction. Returns a logical indicating whether the operation succeeded or not. Eg.   </p><pre class="prettyprint">dbBeginTransaction(con)
dbRemoveTable(con,&quot;newTable&quot;)
dbExistsTable(con,&quot;newTable&quot;)
dbRollback(con)
dbExistsTable(con,&quot;newTable&quot;)

dbBeginTransaction(con)
dbRemoveTable(con,&quot;newTable&quot;)
dbExistsTable(con,&quot;newTable&quot;)
dbCommit(con)
dbExistsTable(con,&quot;newTable&quot;)</pre>
<p>22. dbClearResult(rs, ...) flushes any pending data and frees the resources used by resultset. Eg. </p><pre class="prettyprint">dbClearResult(rs)</pre>
<p>23. dbDisconnect(con, ...) closes the connection.  Eg. </p><pre class="prettyprint">dbDisconnect(con)</pre>
<p>24. dbUnloadDriver(drv,...) frees all the resources used by the driver. Eg. </p><pre class="prettyprint">dbUnloadDriver(drv)</pre><h2><a name="Example"></a>Example<a href="#Example" class="section_anchor"></a></h2>

#### loads the PostgreSQL driver
    library(RPostgreSQL)
    drv <- dbDriver(&quot;PostgreSQL&quot;)

#### Open a connection
    con <- dbConnect(drv, dbname=&quot;R_Project&quot;)

#### Submits a statement
    rs <- dbSendQuery(con, &quot;select * from R_Users&quot;)

#### fetch all elements from the result set
    fetch(rs,n=-1)

#### Submit and execute the query
    dbGetQuery(con, &quot;select * from R_packages&quot;)

#### Closes the connection
    dbDisconnect(con)

#### Frees all the resources on the driver
    dbUnloadDriver(drv)
</HTML>
