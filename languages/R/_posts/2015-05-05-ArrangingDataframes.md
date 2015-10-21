---
layout: post
category: r
subcategory: "Dataframes"
title: "Arrange data frame columns"
ordinal: 1
date: 2012-05-22 16:25:06 -0700
comments: true
---
<!--break-->

### Re-odering columns without specfying all of them
When working with datasets with many columns, sometimes you just want to have
the key row identification variables together and in the beginning.  For example
if you are dealing with patient data, you may want the `id`, `dob`, and `gender`
as the first 3 rows, respectively, and not in arbitrary column positions in the data

To arrange columns by specfying all of them and/or just a subset, please see the
[cookbook](http://www.cookbook-r.com/Manipulating_data/Reordering_the_columns_in_a_data_frame/)
link and the
[dplyr vignette on `select()`](http://cran.rstudio.com/web/packages/dplyr/vignettes/introduction.html)

```r
# Create a dataframe example
df <- as.data.frame(matrix(c(1:20), ncol=10))
names(df)[c(3, 5, 7)] <- c("gender", "id", "dob")
df
```

```
##   V1 V2 gender V4 id V6 dob V8 V9 V10
## 1  1  3      5  7  9 11  13 15 17  19
## 2  2  4      6  8 10 12  14 16 18  20
```


```r
# we want to bring "id", "dob", and "gender" to the beginning, and keep
# everything else the way it is
toBeginning <- c("id", "dob", "gender")
df <- cbind(df[, toBeginning],
            df[, !names(df) %in% toBeginning])
df
```

```
##   id dob gender V1 V2 V4 V6 V8 V9 V10
## 1  9  13      5  1  3  7 11 15 17  19
## 2 10  14      6  2  4  8 12 16 18  20
```
