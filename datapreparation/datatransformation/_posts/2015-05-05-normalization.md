---
layout: post
category: datapreparation
subcategory: datatransformation
title: "Normalization"
ordinal: 2
date: 2012-05-22 16:25:06 -0700
comments: true
---
When normalizing a dataset, one maps the original data range into another data range. This is a form of scaling. The generalized steps for normalization of a dataset field is to identify the minimum and maximum values in the orginal dataset field, identify the minimum and maximum values of the new normalized scale, then calculate the new normalized field value of any number x in the original dataset using an equation similar in form to newvalue = (max'-min')/(max-min)*(value-max)+max'.
