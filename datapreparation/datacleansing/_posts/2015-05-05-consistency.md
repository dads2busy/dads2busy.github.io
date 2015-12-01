---
layout: post
category: dataprofiling
subcategory: "Data Quality"
title: "Consistency"
ordinal: 3
date: 2012-05-22 16:25:06 -0700
comments: true
---
The concept of consistency is best understood as the degree of logical agreement "between" record field values in either a single dataset or between two or more datasets. When there is an expected logical relationship between two or more entities, we can refer to the rule specificying this logic as a type of relationship validation called a dependency constraint. Therefore, consistency becomes the degree to which these attributes satisfy said dependency constraint. An example of a logical requirement is that fields A and B must sum to field C. Logical requirements may be quite involved. For example, 'A has two children', 'A is B's father', 'A is C's father', and 'A is D's father' are inconsistent.

A simple example of a dependency constraint violation would be a location disagreement like a zip-code that does not agree with a state code. Another might be the identification of a male who is also pregnant.

A more complex example would involve consistency validation of fields associated with student withdrawal in education records. For example, most education records contain some form of an 'active code' categorizing the student's current form of interaction with the educational system. Most systems will have a code for 'Inactive' and/or 'Not enrolled'. Most systems will also have a field for withdrawal date. If a student has been categorized as 'Inactive' or 'Not enrolled' but does not have an entry for withdrawal date, then there exists a consistency issue.


Causes of inconsistency are varied, but a common source of inconsistency comes from situations where locally derived information is provided with no associated master list or file. An exhaustive 'master list' of individuals receiving a public service are, in fact, quite rare. In our study, this occurred with student records such as from the Virginia Department of Education (VDOE). Here the student demographics occur in multiple records about the same student recorded in the same year. *Truth* must be derived from the multiple observations. For example, the VDOE data we found 16,310 of the  2,346,058 individuals to have more than one value for gender.

A simple consistency check on the field 'gender' (in pseudo-code) would look like:

    count students
    from student_records joined to itself on student\_id
    where gender does not match
