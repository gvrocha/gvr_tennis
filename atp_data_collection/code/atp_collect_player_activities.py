#!/bin/sh
''''exec python -u -- "$0" ${1+"$@"} # '''

#import itertools
import __main__ as main
import sys
import datetime
import requests
import bs4
import os
import unicodedata
import re
import pandas as pd
import subprocess
import time
import argparse

missing_string           = ""

is_interactive = not hasattr(main, '__file__');
today = datetime.datetime.now()

if(is_interactive):
	infile    = "/Users/gvrocha/Documents/projects/atp_data_collection/data/player_activity/doubles_collection_list.txt"
	exec_file = "/Users/gvrocha/Documents/projects/atp_data_collection/code/atp_get_player_activity.py"
else:
	this_dir          = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
	default_exec_file = "%s/atp_get_player_activity.py" % (this_dir)
	
	parser = argparse.ArgumentParser(description='This script manages collection of a list of player activities.')
	parser.add_argument('infile',      type = str, help = "A file contaning list of players activities to download")
	parser.add_argument('--exec_file', type = str, help = "Script to be used to download player activities", default = default_exec_file)
	
	args      = parser.parse_args()
	infile    = args.infile
	exec_file = args.exec_file

indir           = os.path.dirname(infile)
infile_basename = os.path.basename(infile)
processed_name  = infile+".processed"
failed_name     = infile+".failed"
progress_name   = infile+".progress"

collection_date = datetime.datetime.now().strftime("%Y%m%d")
print("BEGIN: %s" % (datetime.datetime.now().strftime("%Y/%m/%d,%H:%M:%S")))
print("Infile:           %s" % (infile));
print("Exec:             %s" % (exec_file));

activity_list_file  = open(infile, "r")
activity_list       = activity_list_file.readlines()
activity_list_file.close()

max_pings = 120
ping_time = 0.5
processed_list_file = open(processed_name, "a")
failed_list_file    = open(failed_name, "a")
progress_list_file  = open(progress_name, "a")
#this_activity       = activity_list[0]
for this_activity in activity_list:
	this_activity = this_activity.strip()
	this_command  = "python %s %s" % (exec_file, this_activity.strip())
	print("%s\t%s" % (datetime.datetime.now().strftime("%Y/%m/%d,%H:%M:%S"), this_command))
	process    = subprocess.Popen(this_command, shell=True, stdout=progress_list_file, stderr=progress_list_file)
	this_check = process.poll()
	ping       = 0
	while this_check is None and ping < max_pings:
		time.sleep(0.5)
		sys.stdout.write(".")
		ping += 1
		this_check = process.poll()
	sys.stdout.write("\n")
	if this_check is None:
		print("%s: failed    %s\n" % (datetime.datetime.now().strftime("%Y/%m/%d,%H:%M:%S"), this_activity))
		failed_list_file.write(this_activity+"\n")
		failed_list_file.flush()
	else:
		print("%s: completed %s\n" % (datetime.datetime.now().strftime("%Y/%m/%d,%H:%M:%S"), this_activity))
		processed_list_file.write(this_activity+"\n")
		processed_list_file.flush()
	progress_list_file.flush()

processed_list_file.close()
failed_list_file.close()

