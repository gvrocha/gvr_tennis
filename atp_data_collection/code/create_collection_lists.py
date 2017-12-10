#!/bin/sh
''''exec python -u -- "$0" ${1+"$@"} # '''
#execfile("/Users/gvrocha/Documents/projects/atp_data_collection/code/create_collection_lists.py")

import csv
import sqlite3
import os
import re
import argparse
import datetime
import pandas as pd

db_filename                 = "/Users/gvrocha/Documents/projects/atp_data_collection/data/ranking_db.sqlite"
singles_collection_filename = "/Users/gvrocha/Documents/projects/atp_data_collection/data/player_activity/singles_collection_list.txt"
doubles_collection_filename = "/Users/gvrocha/Documents/projects/atp_data_collection/data/player_activity/doubles_collection_list.txt"
verbose                     = True

if verbose:
	print("%s: Connecting to database at %s." % (datetime.datetime.now().strftime('%Y.%m.%d,%H:%M:%S'), db_filename))
con     = sqlite3.connect(db_filename)
cur     = con.cursor()
columns = ["mode", "player_tag", "player_code", "year", "best_rank"]

if verbose:
	print("%s: Querying database." % (datetime.datetime.now().strftime('%Y.%m.%d,%H:%M:%S')))
res     = cur.execute("select mode, player_tag, player.player_code as player_code, 'all' as year, best_rank from player, top_ranking where top_ranking.player_code = player.player_code;")
collection_list = []
for this_row in res:
	collection_list.append(this_row)

con.close()
if verbose:
	print("%s: Creating data frame." % (datetime.datetime.now().strftime('%Y.%m.%d,%H:%M:%S')))
complete_collection_list = pd.DataFrame(collection_list, columns = columns).sort_values(['best_rank', 'mode', 'player_tag'])

if verbose:
	print("%s: Splitting list between singles and doubles." % (datetime.datetime.now().strftime('%Y.%m.%d,%H:%M:%S')))
singles_collection_list  = complete_collection_list.loc[complete_collection_list['mode'] == 'singles']
doubles_collection_list  = complete_collection_list.loc[complete_collection_list['mode'] == 'doubles']

if verbose:
	print("%s: Writing singles collection list to file %s" % (datetime.datetime.now().strftime('%Y.%m.%d,%H:%M:%S'), singles_collection_filename))
singles_collection_file = open(singles_collection_filename, "w")
singles_collection_file.write(singles_collection_list.to_csv(sep='\t', index = False, columns =["mode", "player_tag", "player_code", "year"]))
singles_collection_file.close()

if verbose:
	print("%s: Writing doubles collection list to file %s" % (datetime.datetime.now().strftime('%Y.%m.%d,%H:%M:%S'), doubles_collection_filename))
doubles_collection_file = open(doubles_collection_filename, "w")
doubles_collection_file.write(doubles_collection_list.to_csv(sep='\t', index = False, columns =["mode", "player_tag", "player_code", "year"]))
doubles_collection_file.close()
