---
layout: post
category: r
subcategory: "GIS"
title: "Geocoding with R and Google"
ordinal: 2
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->

# Geocoding with Google Maps

## connect to database
    setwd("~/sdal/PRJ_201505_CENSUS/analysis/aschroed")
    source(file="pg_connect.R")

    library("ggmap")


## simple example
    gc <- geocode("1220 S Villge Way, Blackburg, VA", output = c("more"), source = c("google"))
    print(paste(gc$address, "lat =", gc$lat, "lon =", gc$lon))
    View(gc)


## example pulling addresses from MLS database

    geosleep <- function(){
      geocode(output = 'more', source = 'google')
      Sys.sleep(0.3)
    }

## build and run query to get listing address info
    listingAddresses <- dbGetQuery(con, "SELECT list_number, st_number, st_direction,
                      street_name, street_suffix, city, state, zip_code
                      FROM housing.w_mls_location_data limit 5")

## get geocoding of each address and add column to end of listingAddresses
    listingAddresses$geo <- lapply(paste(listingAddresses$st_number, listingAddresses$st_direction,
             listingAddresses$street_name, listingAddresses$street_suffix,
             listingAddresses$city, listingAddresses$state, listingAddresses$zip_code,
             sep=" "), geocode, output = 'more', source = 'google')


    geocode_sleep <- function(location, output = c("more"), source = c("google"), sleep_time = 0.3) {
      # regular geocode function call
      ret <- geocode(location, output, source)
     # sleep!
      Sys.sleep(sleep_time)
      ret
    }

    listingAddresses$geo <- lapply(paste(listingAddresses$st_number, listingAddresses$st_direction,
                                     listingAddresses$street_name, listingAddresses$street_suffix,
                                     listingAddresses$city, listingAddresses$state, listingAddresses$zip_code,
                                     sep=" "), geocode_sleep)

    print(listingAddresses$geo)[aschroed@snowmane aschroed]$
