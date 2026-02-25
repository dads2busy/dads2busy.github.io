---
layout: post
category: r
subcategory: "Import"
title: "Load CSV file into R/RStudio"
ordinal: 1
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->

    myDataFrame <- read.csv("GradeRetentionData.csv")

The read.csv function assumes that your file has a header row, so row 1 is the name of each column. If that's not the case, you can add header=FALSE to the command:

    mydata <- read.csv("filename.txt", header=FALSE)

If your data use another character to separate the fields, not a comma, R also has the more general read.table function. So if your separator is a tab, for instance, this would work:

    mydata <- read.table("filename.txt", sep="\t", header=TRUE)

**Note that when using read.table you need to specify header=TRUE if the first row is column names (default is FALSE which is the opposite of read.csv where default is TRUE).**
