---
layout: post
category: dataprofiling
subcategory: "Data Quality"
title: "Uniqueness"
ordinal: 4
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---

The concept of data uniqueness can be generalized as the number of unique valid values that have been entered in a record field, or as a combination of record field values within a dataset. Uniqueness is not generally discussed in terms of data quality, but for the purposes of answering research questions, the variety and richness of the data is of paramount importance. Most notably, if a record field has very little value uniqueness (e.g. entries in the field 'State' for an analysis of housing within a county, which of course would be within a single state), then its utility would be quite low and can be conceptualized as having low quality in terms of the research question at hand.

A basic birth year distribution plot is shown using R and SQL:

    values_birth_year = dbGetQuery(con, "SELECT birth_year
                                         FROM student_mobility_fields_2005_2015")

    # frequency distribution plot of birth_year values
    birth_year_frequencies = table(values_birth_year$birth_year)
    barplot(birth_year_frequencies, main="Birth Year Value Distribution", horiz=TRUE)

<img src="/images/BirthYearFreqDist.png" style="border-width:0px;" />
