---
layout: post
category: datapreparation
subcategory: datatransformation
title: "Winsorization"
ordinal: 3
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
Many statistics can be heavily influenced by outliers. One strategy is to set all outliers to a specified percentile of the data. This is called Winsorization of Winsorizing. In Winsorization, extreme values are limited in the statistical data to reduce the effect of these spurious outliers. For example, a 90\% Winsorisation would see all data below the 5th percentile set to the 5th percentile, and data above the 95th percentile set to the 95th percentile. Winsorised estimators are usually more robust to outliers than their more standard forms, although there are alternatives, such as trimming, that will achieve a similar effect.
Note that Winsorising is not equivalent to trimming or truncation. In a trimmed estimator, the extreme values are discarded; in a Winsorised estimator, the extreme values are instead replaced by certain percentiles (the trimmed minimum and maximum). Therefore, statistics derived from the two sets would not be equivalent (e.g. a Winsorised mean is not equal to a truncated mean).
