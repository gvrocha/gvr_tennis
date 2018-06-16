remove(list = objects())

library(ggplot2)

setwd("~/Documents/projects/tennis/git/tennis_pointbypoint/")
source("./code/R/draft_functions.R")

#---

these_data = rbind(read.csv("pbp_matches_atp_main_current.csv", stringsAsFactors = F),
                   read.csv("pbp_matches_atp_main_archive.csv", stringsAsFactors = F))

get_pairs = function(x){
  x         = dplyr::mutate(x, idx = 1:nrow(x))
  all_pairs = merge(x, x,  by = NULL, suffixes = c(".1", ".2"))
  all_pairs = subset(all_pairs, idx.1<idx.2)
  return(all_pairs)
}

player_df        = data.frame(player_name = sort(unique(c(these_data$server1, these_data$server2))))
nplayers         = nrow(player_df)
player_pairs     = get_pairs(player_df)
  
distance.methods = c('osa','lv','dl','hamming','lcs','qgram','cosine','jaccard','jw')
dist.methods     = list()

t0 = proc.time()
player_pairs = plyr::adply(.data = player_pairs, 
                           .margins = 1, 
                           .progress = "text",
                           .fun = function(y){
                             return(data.frame(dist = stringdist(tolower(y$player_name.1),
                                                                 tolower(y$player_name.2),
                                                                 method = 'osa')))
                             })
t1 = proc.time()

tournament_df        = data.frame(tournament_name = tolower(sort(unique(these_data$tny_name))))
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
