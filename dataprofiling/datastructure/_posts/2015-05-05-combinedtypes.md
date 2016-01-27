---
layout: post
category: dataprofiling
subcategory: "Data Structure"
title: "Combined Observational Unit Types"
ordinal: 4
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
Within administrative records, multiple types of data are often combined for expediency. By multiple types we mean different sets of data fields, each set representing a different type of observational unit (e.g. property information and listing agent information in the same record). The observational unit types necessary to the project at hand need to be separated out into individual observations or individual datasets in the restructuring phase.

One example encountered in the education case study had to do with a dataset containing both individual demographic data and a periodic measurement of weekly attendance where demographic data and weekly attendance are separate observational units and needed to be in separate datasets for the purposes of the study.

Another example, this time from the housing case study, was given in Figure . Pulling out a definitive list of unique properties using "Parcel ID" was a possible restructuring. However, "Parcel ID" in this case has been left blank in over 7\% of the entries. Therefore, extra work was required employing the use of a geocoding API to locate a property within county parcel maps that already include a Parcel ID. In addition, an additional complication is the fact that no standardized address format was used in the creation of the MLS record. Therefore, a small amount of direct interaction and decision making by an analyst was also necessary to finalize the geographic matching.
