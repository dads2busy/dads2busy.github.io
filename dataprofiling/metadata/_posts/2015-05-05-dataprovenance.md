---
layout: post
category: dataprofiling
subcategory: "Metadata"
title: "Data Provenance"
ordinal: 7
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
The concept of Provenance is very broad and has different meanings within different fields of inquiry. For the purposes of Data Profiling, we find it useful to apply the definition provided by the World Wide Web Consortium (W3C)

"Provenance of a resource is a record that describes entities and processes involved in producing and delivering or otherwise influencing that resource. Provenance provides a critical foundation for assessing authenticity, enabling trust, and allowing reproducibility. Provenance assertions are a form of contextual metadata and can themselves become important records with their own provenance."
[https://www.w3.org/2005/Incubator/prov/wiki/What_Is_Provenance]

An example of why it is important to consider data provenance was seen in the housing case study. Some of the datasets used were provided by 3rd party vendors. As part of the value-added of these data products, 3rd party vendors often perform some set of transformations on the original data to enhance data consistency and quality. Sometimes the transformation processes used are readily available to the client, and the client can validate their application by repeating the transformations and producing identical results. Other this information is not made available, thus necessitating further investigation and experimentation on the part of the client to ensure that the data provided is, in fact, a true representation of the original source data.
