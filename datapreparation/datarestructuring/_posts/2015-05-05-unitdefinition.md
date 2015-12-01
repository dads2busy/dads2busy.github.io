---
layout: post
category: dataprofiling
subcategory: "Metadata"
title: "Observation Unit Definition"
ordinal: 1
date: 2012-05-22 16:25:06 -0700
comments: true
---
When a dataset is provided without definition of the purpose of that dataset, we have an issue with the Observation Unit Definition. Why was this data collected? When dealing with datasets not orignally collected for research purposes (e.g administrative data), there is often no easy answer to this question. To correct issues of observational unit definition, it is often necessary to first generate separate new datasets from the dataset provided, each representing only a single observational unit type. At this point a new observational unit definition can be created.

This type of metadata is issue is quite common, and we experienced said issue when dealing with certain 3rd-party produced housing datasets. A single dataset would include, within each record(row), multiple potential observational units (e.g housing unit data, listing service data, owner data, neighborhood data). Only after defining the observational units needed and extracting the necessary fields could a new observational unit definition be generated (e.g. Housing Unit Specifications for Arlington County VA from CY 20XX to CY 20XX).
