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

<b>Housing Example</b>
An example of why it is important to consider data provenance was seen in the housing case study. Some of the datasets used were provided by 3rd party vendors. As part of the value-added of these data products, 3rd party vendors often perform some set of transformations on the original data to enhance data consistency and quality. Sometimes the transformation processes used are readily available to the client, and the client can validate their application by repeating the transformations and producing identical results. Other this information is not made available, thus necessitating further investigation and experimentation on the part of the client to ensure that the data provided is, in fact, a true representation of the original source data.

<b>Property Crime Example</b>
Another example from our studies was from a commercial data provider which provided indicators of neighborhood quality based on patented algorithms. We were unable to reconcile differences found in their crime indexes and data from Arlington County, Virginia Police Incident Tracking system. Figure 3.5 presents the misalignment in these data sources by census tract. The figure shows property crime counts as calculated by the commercial provider and as directly pulled from the Arlington County Police Incident Tracking system. The county data had five census tracts with counts greater than 300. These were not shown in the boxplot to allow a better scaled comparison to the commercial provider. The commericial provider did not describe, nor makes available, their methods to adjust the counts.

<img src="/images/ProvenanceProblem.png" style="border-width:0px;" />
