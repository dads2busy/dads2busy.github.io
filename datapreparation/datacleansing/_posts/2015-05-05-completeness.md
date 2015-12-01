---
layout: post
category: dataprofiling
subcategory: "Data Quality"
title: "Completeness"
ordinal: 1
date: 2012-05-22 16:25:06 -0700
comments: true
---
The concept of data completeness can be generalized as the proportion of data provided versus the proportion of data required. Data that is missing may additionally be categorized as record fields not containing data, records not containing necessary fields, or datasets not containing the requisite records. The most common conceptualization of completeness is the first, record field not containing data. This conceptualization of data completeness can be thought of as *the proportion of the data that has values to the proportion of data that ’should’ have values*. That is, a set of data is complete with respect to a given purpose if the set contains all the relevant data for that purpose. Completeness is application specific. It would be incorrect to simply measure the number of missing field values in a record without first considering which of the fields are actually necessary for completion of the task at hand.

For example, in our study of Multiple Listing Service Real Estate (MLS) data, a datset was provided with each record containing 128 fields. Per record, many of these fields are missing data, however, most of these fields were not important to the purpose of the study (e.g. Listing Agent, Owner Name, Owner Phone). It would not be helpful to categorize the proportion of missing values for these fields. Instead, a decision must first be made as to which fields belong in the analysis for the current purpose. An example pseudo-code would look something like:

    for each field in (select needed_field_1, needed_field_2, needed_field_3)
    count needed_field_n where
    needed_field_n DOES NOT EQUAL 0
    and needed_field_n IS NOT BLANK
    and needed_field_n IS NOT NULL
