---
layout: post
category: dataprofiling
subcategory: "Metadata"
title: "Semantic Confusion"
ordinal: 3
date: 2012-05-22 16:25:06 -0700
comments: true
---
The concept of semantic interoperability here refers to the ability of data systems to exchange data with other data systems unambiguously. Semantic interoperability is concerned not just with the data syntax, but also with the transmission of the meaning with the data (semantics). This is generally accomplished by adding metadata to a dataset, thereby defining a controlled, shared vocabulary. Without this shared vocabulary, \textbf{Semantic Confusion} can occur, where names and syntax may agree, but definitions don't. For example, while combining two data sets, it may be found that two fields(attributes) have the same name (say "Grade") but their definitions are completely different (because “Grade” can refer to both a 'score' for a test/class or the 'level/year' of schooling).

<img src="/images/symantic_confusion.png" style="border-width:0px;" />
