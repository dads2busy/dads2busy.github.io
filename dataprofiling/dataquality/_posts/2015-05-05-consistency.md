---
layout: post
category: dataprofiling
subcategory: "Data Quality"
title: "Consistency"
ordinal: 3
date: 2012-05-22 16:25:06 -0700
comments: true
---
A measure of the degree to which two or more data attributes satisfy a well-defined dependency constraint – relationship validation.

e.g. zip-code – state consistency gender – pregnancy consistency

<!--break-->

###Data Quality Example - Consistency

####The Degree to Which Two or More Attributes Satisfy a Dependency Constraint

* Simple example
  * Unordered List ItemLocation disagreements like zip and state
* More complex example
  * Consistency with locally derived “truth”
  * VDOE Student Record, no definitive list of student demographics (actually very common)
  * Truth must be derived from multiple observations
  * Student Record has multiple observations per school year
  * Query here shows disagreement on gender for some of the observations when Student Record is matched to itself
    * select count(distinct a.internalid) from vdoe.studentrecord a join vdoe.studentrecord b on a.internalid = b.internal_id and a.gender <> b.gender

####16,310 / 2,346,058 individuals have more than one value for gender
####Truth becomes probabilistic and/or time-based
