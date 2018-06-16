remove(list = objects())

library(ggplot2)

setwd("~/Documents/projects/tennis/git/tennis_pointbypoint/")
source("./code/R/draft_functions.R")

#---
these_data           = rbind(read.csv("pbp_matches_atp_main_current.csv", stringsAsFactors = F),
                             read.csv("pbp_matches_atp_main_archive.csv", stringsAsFactors = F))

these_data           = dplyr::mutate(these_data, 
                                     date         = as.Date(date, format = "%d %b %y"), 
                                     tny_name     = sapply(tny_name, regularize_tny_name),
                                     atp_tny      = sapply(tny_name, get_atp_piece), 
                                     year         = as.numeric(strftime(date, "%Y")), 
                                     month        = as.numeric(strftime(date, "%m")), 
                                     month_str    = sprintf("%02d", as.numeric(strftime(date, "%m"))), 
                                     plain_score  = sapply(score, get_plain_score),
                                     n_points     = sapply(pbp, get_npoints),
                                     n_points.alt = sapply(pbp, get_npoints.alt),
                                     n_games      = sapply(pbp, get_ngames),
                                     n_games.alt  = sapply(score, get_ngames.alt), 
                                     tny          = ifelse(!is.na(atp_tny), atp_tny, tny_name))

tournament_df        = data.frame(tournament_name = sort(unique(these_data$tny)), stringsAsFactors = F)
tournament_pairs     = get_pairs(tournament_df)
t2 = proc.time()
tournament_pairs     = plyr::adply(.data = tournament_pairs, 
                                   .margins = 1, 
                                   .progress = "text",
                                   .fun = function(y){
                                     return(data.frame(dist = stringdist(tolower(y$tournament_name.1),
                                                                         tolower(y$tournament_name.2),
                                                                         method = 'osa')))
                                     })
t3 = proc.time()

tournament_pairs = dplyr::arrange(tournament_pairs, dist, tournament_name.1, tournament_name.2)
