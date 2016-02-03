---
layout: post
category: r
subcategory: "Parallel"
title: "Parallel Processing with foreach"
ordinal: 3
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->

# Parallel Processing with foreach
### In R, "foreach" is used for parallel processing (as opposed to most programming languages where it is just shorthand for a "for" loop).

## 1. Create a cluster of 20 processors to be used in parallel
    myCluster<-makeCluster(20)

## 2. Register the cluster
    registerDoParallel(myCluster)

## 3a. Create a foreach loop
### It is the %dopar% piece that tells R to use the parallel cluster. If you want to just use a single processor, substitute with %do%.
    ls <- foreach(i=1:num_rows) %dopar% {   

      <your code>

      }
    }

## 3b. Append results of loop to output variable using "to."
    ls <- foreach(i=1:num_rows) %dopar% {

      if(<some_condition>) > 1){
        to.ls <- <some_result>

      }
    }
