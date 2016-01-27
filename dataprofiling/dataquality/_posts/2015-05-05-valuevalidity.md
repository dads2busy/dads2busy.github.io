---
layout: post
category: dataprofiling
subcategory: "Data Quality"
title: "Value Validity"
ordinal: 2
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
The concept of value validity can be conceptualized as the percentage of elements whose attributes possess expected values. The actualization of this concept generally comes in the form of straight-forward domain constraint rules. For example, to ascertain how many entries contain non-valid values for a non-empty text field representing gender, an example pseudo-code domain \textit{comparison-constraint rule} would look something like:

    count gender where gender is not in (male, female)

Or, to ascertain how many entries contain non-valid values for a non-empty integer field representing age, a pseudo-code domain \textit{interval-constraint rule} would look something like:

    count age where age is not between [0,110]

It should be noted that in many discussions of data quality, this concept is simply referred to as "Validity" (Redman, DoD, ...). However, the term validity has many differing and complex meanings (and attendant sub-definitions) within the social and behavioral sciences. Therefore, here we use our own sub-definition "value validity" to be clear which specific form of validity is being discussed.

An example of a discovered value validity problem can be seen in Figure \ref{valuevalidity}. While profiling MLS data for a particular locality, it was discovered that the values entered for the field "zoning" were extensively varied. It is clear that the mechanism of input provided for this field was 'free text' where anything can be typed. The domain comparison-constraint for this field is the official list of zoning district names for that locality. It was found that none of the entries for this field in this particular dataset qualify as valid values. However, it should be noted that there may still vary well be usable information contained within the zoning field. The lack of valid values simply points to a potential problem in need of further investigation. For example, if the question at hand simply requires a count of how many properties are "Resdiential", it may very well be possible to transform the existing entries to adequately represent a true or false in this respect. However, the executions of such transformations are left for the Data Transformation stage.

<img src="/images/value_validity.png" style="border-width:0px;" />
