---
layout: post
category: r
subcategory: "Dataframes"
title: "Subset of data frame in R"
ordinal: 1
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->

### Keeping/dropping columns by name
Taken from [here](http://stackoverflow.com/questions/5234117/how-to-drop-columns-by-name-in-a-data-frame) and [here](http://stackoverflow.com/questions/4605206/drop-columns-r-data-frame)

```r
# Creating the data frame
fname <- c('Bob', 'Sally', 'John', 'Jane')
lname <- c('Dole', 'Doe', 'Doe', 'Smith')
age <- c(32, 24, 28, 25)
df <- data.frame(fname, lname, age)
df
```

```
##   fname lname age
## 1   Bob  Dole  32
## 2 Sally   Doe  24
## 3  John   Doe  28
## 4  Jane Smith  25
```


```r
# keeping columns by name
keep <- c('fname', 'age')
df[, names(df) %in% keep]
```

```
##   fname age
## 1   Bob  32
## 2 Sally  24
## 3  John  28
## 4  Jane  25
```


```r
# dropping columns by name
drop <- c('lname')
df[, !(names(df) %in% drop)]
```

```
##   fname age
## 1   Bob  32
## 2 Sally  24
## 3  John  28
## 4  Jane  25
```

### Work on a subset of data frame using regular expression
Sometimes you want to do some kind of calculation or munge on a aubset of a data frame.  For example, survey data might be coded q1a - q1k and you want to average the values, sum the values, look at the values, etc...


```r
# Create a data frame
q13 <- c(1:5)
q14a <- c(2:6)
q14b <- c(3:7)
q14c <- c(4:8)
q14z <- c(5:9)
df <- data.frame(q13, q14a, q14b, q14c, q14z)
df
```

```
##   q13 q14a q14b q14c q14z
## 1   1    2    3    4    5
## 2   2    3    4    5    6
## 3   3    4    5    6    7
## 4   4    5    6    7    8
## 5   5    6    7    8    9
```


```r
# regular expresstion for only sum q14a - q14c, do not include q14z
q14pattern <- '^q14[a-cA-C]'

# search the column names for a pattern match, return vector of column indices
q14columns <- grep(pattern = q14pattern, x = names(df))

# do something with the subset data, here I am summing the rows
df$q14.sum <- rowSums(x = df[, q14columns])
df
```

```
##   q13 q14a q14b q14c q14z q14.sum
## 1   1    2    3    4    5       9
## 2   2    3    4    5    6      12
## 3   3    4    5    6    7      15
## 4   4    5    6    7    8      18
## 5   5    6    7    8    9      21
```

We can also do a similar process to only look at the q14 variables

```r
q14patternAll <- '^q14'
q14columnsAll <- grep(pattern = q14patternAll, x = names(df))
head(df[, q14columnsAll], n = 2)
```

```
##   q14a q14b q14c q14z q14.sum
## 1    2    3    4    5       9
## 2    3    4    5    6      12
```
