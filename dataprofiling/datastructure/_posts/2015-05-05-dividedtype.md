---
layout: post
category: dataprofiling
subcategory: "Data Structure"
title: "Divided Observation Unit Type"
ordinal: 5
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
Within administrative data systems, it is also not uncommon to find that a single observation unit type has been split among multiple datasets.This is similar to the consistency discussion of multiple observations with overlapping demographic information. The difference here is that you may have information split among several datasets. For example, there may be, as was the case with one state's educational records, separate tables that duplicate the collection of student demographics. Figure \ref{dividedtype} captures gender mismatches across two tables from the same education record information system, linked on the Unique Id of the student. Decisions on whether and how to transform inconsistent data as a result of divided observation unit type need to factor in the magnitude of the issue as well as the ability to accurately correct the data in a timely enough fashion given the project at hand.  

<img src="/images/divided_type.png" style="border-width:0px;" />
Example of divided observational units for gender mismatched in multiple tables.
