---
layout: post
category: r
subcategory: "Parallel"
title: "Split and Parallel Example in R"
ordinal: 1
date: 2012-05-22 16:25:06 -0700
comments: true
website: ""
---
<!--break-->

    #Import packages
    library(foreach)
    library(doParallel)
    library(data.table)
    library(dplyr)
    library(Matrix)
    library(igraph)

    setwd("~/R/ForEach/HealthIT")
    data <- fread("ili_data.csv", sep=",")
    data_pt_hosp <- data %>%
      select(studyid,DMISID)

    #Setup parallel backend to use 20 processors
    cl<-makeCluster(8)
    registerDoParallel(cl)

    chunk <- 100000
    it <- idiv(nrow(data_pt_hosp), chunkSize=chunk)
    startRow <- 1
    endRow <- chunk
    edgeTableFinal <- data.table(a=character(),b=character())
    try(
    for (i in 1:10000) {
      #start time
      strt<-Sys.time()

      data_pt_hosp_cast <- dcast.data.table(data_pt_hosp[startRow:endRow],studyid~DMISID,fun=length)

      #head(data_pt_hosp_cast)
      #set rownames:
      setkey(data_pt_hosp_cast,studyid)
      #data table without the study id column:
      data_pt_hosp_cast[,studyid:=NULL]

      hospitals <- colnames(data_pt_hosp_cast)

      hospital_adj <- Matrix(0, length(hospitals), length(hospitals), sparse=TRUE)
      row.names(hospital_adj) <- hospitals
      colnames(hospital_adj) <- hospitals

      data_pt_hosp_cast$non_zero <- apply(data_pt_hosp_cast,1,nnzero)
      data_pt_hosp_cast <- data_pt_hosp_cast[data_pt_hosp_cast$non_zero > 1,]
      data_pt_hosp_cast[,non_zero:=NULL]

      num_rows <- nrow(data_pt_hosp_cast)

    # Parallel loop
      ls<-foreach(i=1:num_rows) %dopar% {

        row_matrix <- as.matrix(data_pt_hosp_cast[i, ])
        rows_of_hospitals <- row_matrix[,row_matrix != 0]
        hospital_ids <- names(rows_of_hospitals)

        if(length(hospital_ids) > 1){
          to.ls <- combn(hospital_ids, 2, simplify = FALSE)
        }
      }

      list_col1 <- list()
      for (i in seq(ls)) {
        for (j in seq(ls[[i]])) {
          list_col1 <- c(list_col1, ls[[i]][[j]][[1]])
        }
      }

      list_col2 <- list()
      for (i in seq(ls)) {
        for (j in seq(ls[[i]])) {
          list_col2 <- c(list_col2, ls[[i]][[j]][[2]])
        }
      }

      edgeTable <- data.table(a=list_col1,b=list_col2)
      edgeTableFinal <- rbind(edgeTableFinal, edgeTable)

      print(Sys.time()-strt)

      startRow <- endRow + 1
      endRow <- endRow + nextElem(it)
    }
    , silent = TRUE)
    stopCluster(cl)
    registerDoSEQ()
    # print(edgeTableFinal)
    # write.table(as.matrix(edgeTableFinal), "/home/aschroed/R/ForEach/HealthIT/edgeTable.csv", sep=",")
