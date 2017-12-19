#!/bin/sh
''''exec python -u -- "$0" ${1+"$@"} # '''
#execfile("/Users/gvrocha/Documents/projects/atp_data_collection/code/create_collection_lists.py")

import csv
import sqlite3
import os
import sys
import re
import argparse
import datetime
import pandas as pd

#if len(sys.argv) < 2: 
if '__file__' not in globals():
	db_filename                 = "/Users/gvrocha/Documents/projects/atp_data_collection/data/ranking_db.sqlite"
	singles_collection_filename = "/Users/gvrocha/Documents/projects/atp_data_collection/data/player_activity/singles_collection_list.txt"
	doubles_collection_filename = "/Users/gvrocha/Documents/projects/atp_data_collection/data/player_activity/doubles_collection_list.txt"
	verbose                     = True
else:
	this_dir                = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
	base_dir                = "%s/../data" % (this_dir)
	default_db_filename     = "%s/atp_db.sqlite" % (base_dir)
	default_singles_colfile = "%s/player_activity/singles_collection_list.txt" % (base_dir)
	default_doubles_colfile = "%s/player_activity/doubles_collection_list.txt" % (base_dir)
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--db_filename',      dest = "db_filename",      type = str, default = default_db_filename,       help = "SQLite database location (default: %s)" % (default_db_filename))
	parser.add_argument('--singles_colfile',  dest = "singles_colfile",  type = str, default = default_singles_colfile,   help = "Filename where singles collection file will be written (default: %s)" % (default_db_filename))
	parser.add_argument('--doubles_colfile',  dest = "doubles_colfile",  type = str, default = default_doubles_colfile,   help = "Filename where doubles collection file will be written (default: %s)" % (default_db_filename))
	parser.add_argument('--quiet',            dest = "quiet",         action = 'store_const', const = True,      default = False,      help = "")
	
	args                        = parser.parse_args()
	db_filename                 = args.db_filename
	singles_collection_filename = args.singles_colfile
	doubles_collection_filename = args.doubles_colfile
	verbose                     = not args.quiet

if verbose:
	print("db_filename:     %s" % (db_filename))
	print("singles_colfile: %s" % (singles_collection_filename))
	print("doubles_colfile: %s" % (doubles_collection_filename))
	print("verbose:         %s" % (verbose))
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
singles_collection_dir  = os.path.dirname(singles_collection_filename)
if not os.path.isdir(singles_collection_dir):
	os.makedirs(singles_collection_dir);
singles_collection_file = open(singles_collection_filename, "w")
singles_collection_file.write(singles_collection_list.to_csv(sep='\t', index = False, columns =["mode", "player_tag", "player_code", "year"]))
singles_collection_file.close()

if verbose:
	print("%s: Writing doubles collection list to file %s" % (datetime.datetime.now().strftime('%Y.%m.%d,%H:%M:%S'), doubles_collection_filename))
doubles_collection_dir  = os.path.dirname(doubles_collection_filename)
if not os.path.isdir(doubles_collection_dir):
	os.makedirs(doubles_collection_dir);
doubles_collection_file = open(doubles_collection_filename, "w")
doubles_collection_file.write(doubles_collection_list.to_csv(sep='\t', index = False, columns =["mode", "player_tag", "player_code", "year"]))
doubles_collection_file.close()
