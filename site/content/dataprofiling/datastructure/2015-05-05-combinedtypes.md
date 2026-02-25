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

An example from the housing case study is given in Figure 3.3. The dataset provided wascomprised of single records with 128 fields. Each original record was identified by a unique“List Number.” However, if a parcel was listed twice it would have two different “List Num-bers.” As a result, changes in a property or parcel over time could not be tracked from theserecords because the structure only identified the list number not the parcel number. Changingthe structure to include the “Parcel ID” allowed the required historical tracking of changes.

<img src="/images/CombinedObservationalUnitTypes.png" style="border-width:0px;" />
