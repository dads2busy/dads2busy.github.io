---
layout: post
category: r
subcategory: "Misc"
title: "Timing Code"
ordinal: 1
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->

# Single-line timing
A common way to time a line of `R` code is to save `Sys.time()` to a variable before the code you want to evaluate, and then find the difference of `Sys.time()` after.  This will have `R` output text something along the lines of `Time difference of 5.335534 secs`

However, if you are running a script that has multiple of these timings, the printed results are not useful.
A `hack` would be to do a `print()` statement before the time difference calculation, but that just looks ugly,
especially in knitr documents.

Below is a function that will take a string of what you are timing, and the difftime calculation, and
cats back a nice prompt for you.

    print_difftime_prompt <- function(str_what_did_you_time, diff_time, sep=':'){
        parse_time <- unclass(diff_time)[1]
        parse_units <- attr(unclass(diff_time), 'units')
        prompt_string <- sprintf('%s took: %s %s', str_what_did_you_time, parse_time, parse_units)
        cat(prompt_string, '\n')
        # return(prompt_string)
    }

For example:  
    strt <- Sys.time()
    print_difftime_prompt('add simulation dataframes to list', Sys.time() - strt)
will return:  
`add simulation dataframes to list took: 36.1213629245758 secs`

# Microbenchmark
Additionally, do get an accurate time, use the `microbenchmark()` function in the `microbenchmark` package.
See Hadley's [post](http://adv-r.had.co.nz/Performance.html) about it's use.
