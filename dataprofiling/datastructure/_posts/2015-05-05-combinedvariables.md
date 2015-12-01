---
layout: post
category: dataprofiling
subcategory: "Data Structure"
title: "Combined Variables"
ordinal: 2
date: 2012-05-22 16:25:06 -0700
comments: true
---
Combined variables refers to the condition where more than one variable is represented in a record field. Sometimes, especially, after some form of correction to the previous problem of missing variables has been address,
we end up with column variable names comprised of a combination of multiple underlying
variable names. It should be note that many times, like duplication, this is an issue of problem definition. A common example with administrative record files occurs when we use parts of the date_of_birth field. For example, in the education case study, there was a need at one point to categorize students by birth_year. To achieve this categorization, it was first necessary to divide out from the date_of_birth field the variables birth_month, birth_day, and birth_year. While this is often achieved within the programming of a query (i.e. select datepart('year', date_of_birth), what in fact is occurring is the separation of previously combined variables.
