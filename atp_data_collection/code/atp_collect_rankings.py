#!/bin/sh
''''exec python -u -- "$0" ${1+"$@"} # '''

#mode      	sys.argv[1]
#start_date sys.argv[2] in yyyy.mm.dd
#final_date sys.argv[3] in yyyy.mm.dd

# Used above concoction to make this less dependent on where python lives...
# In my mac, which python = /Library/Frameworks/Python.framework/Versions/2.7/bin/python
import __main__ as main
import requests
import datetime
import bs4
import os
import unicodedata
import sys
import argparse
import re
import math

#---
def get_ranking_on_date(a_date, mode, field_sep  = ",", line_sep = "\n", verbose = False):
	if verbose:
		print("In get_ranking_on_date")
		print("a_date:    %s" % (a_date.strftime('%Y-%m-%d')))
		print("mode:      %s" % (mode))
		print("field_sep: %s" % (field_sep))
	out_string = ""
	try:
		url    = 'http://www.atpworldtour.com/en/rankings/%s?rankDate=%s&rankRange=1-5000' % (mode, a_date.strftime('%Y-%m-%d'))
		page   = requests.get(url)
		soup   = bs4.BeautifulSoup(page.text, 'html.parser')
		tables = soup.select('table.mega-table')
		rows   = tables[0].select('tr')
		
		for x in rows:
			# Header row:
			these_pieces = [unicodedata.normalize('NFKD', y.text.strip()).encode('ascii', 'ignore')  for y in x.select("th")]
			if(len(these_pieces)>0):
				data_pieces = ["date", "mode"]+these_pieces+["normalized_country", "player_code", "player_tag", "player_number"]
				out_string += field_sep.join(data_pieces)+line_sep
			
			# Data row:
			these_entries = x.select("td")
			these_pieces  = [unicodedata.normalize('NFKD', y.text.strip()).encode('ascii', 'ignore') for y in these_entries]
			these_pieces  = [y.replace(field_sep,"") for y in these_pieces] # In case commas are used
			if(len(these_entries)>0):
				player_link    = these_entries[3].select("a")[0].get("href")
				if(not player_link): # If missing (none) , fill entry with NA
					player_code   = "NA"
					player_tag    = "NA"
					player_number = "NA"
				else:
					player_code   = player_link.replace("/en/players/","").replace("/overview", "")
					player_tag    = player_code.split("/")[0]
					player_number = player_code.split("/")[1]
				
				player_country = these_entries[2].select("img")[0].get("alt")
				if(not player_country): # If missing (none) , fill entry with NA
					player_country = "NA";
				
				data_pieces = [a_date.strftime('%Y-%m-%d'), mode]+these_pieces+[player_country, player_code, player_tag, player_number]	
				out_string += field_sep.join(data_pieces)+line_sep
		
		return(out_string)
	except Exception as inst:
		raise inst

#---
this_dir           = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
today              = datetime.datetime.now()
default_start_date = today -  datetime.timedelta(days=6)
default_final_date = today

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--doubles',       dest = "doubles",       action = 'store_const', const = True,      default = False,      help = "collect data for singles or doubles (default: 'singles')")
parser.add_argument('--quiet',         dest = "quiet",         action = 'store_const', const = True,      default = False,      help = "")
parser.add_argument('--screen_output', dest = "screen_output", action = 'store_const', const = True ,     default = False,      help = "")
parser.add_argument('--skip_log',      dest = "keep_log",      action = 'store_const', const = False,     default = True,       help = "")
parser.add_argument('--start_date',    dest = "start_date",    type = str, default = default_start_date.strftime('%Y.%m.%d'),   help = "start date for collection in yyyy.mm.dd format (default: 'today - 6 days')")
parser.add_argument('--final_date',    dest = "final_date",    type = str, default = default_final_date.strftime('%Y.%m.%d'),   help = "start date for collection in yyyy.mm.dd format (default: 'today - 6 days')")
parser.add_argument('--outdir',        dest = "outdir",        type = str, default = "",                                        help = "output directory (default: '%s/../data/ranking_files/<mode>/collected')" % (this_dir))

args           = parser.parse_args()
doubles        = args.doubles
start_date_str = args.start_date
final_date_str = args.final_date
verbose        = not args.quiet
output_dir     = args.outdir
screen_output  = args.screen_output
keep_log       = args.keep_log

if(doubles):
	mode = "doubles"
else:
	mode = "singles"
if(output_dir == ""):
	output_dir = '%s/../data/ranking_files/%s/collected' % (this_dir, mode)

date_re = re.compile("^(\d{4,4}).(\d{2,2}).(\d{2,2})$")

start_date_match = date_re.match(start_date_str)
final_date_match = date_re.match(final_date_str)

if not start_date_match:
	print("Error: start date does not match date string pattern yyyy.mm.dd")
	sys.exit()

if not final_date_match:
	print("Error: start date does not match date string pattern yyyy.mm.dd")
	sys.exit()	

start_date = datetime.datetime(int(start_date_match.group(1)), int(start_date_match.group(2)), int(start_date_match.group(3)))
final_date = datetime.datetime(int(final_date_match.group(1)), int(final_date_match.group(2)), int(final_date_match.group(3)))

print("Doubles:          %s" % (doubles))
print("Mode:             %s" % (mode))
print("Output directory: %s" % (output_dir))
print("Start date:       %s" % (start_date.strftime('%Y.%m.%d')))
print("Final date:       %s" % (final_date.strftime('%Y.%m.%d')))
print("Verbose:          %s" % (str(verbose)))   
print("screen_output:    %s" % (str(screen_output)))   
print("keep_log:         %s" % (str(keep_log)))   
print("output_dir:       %s" % (output_dir))

if not os.path.isdir(output_dir):
	os.makedirs(output_dir);

if not os.path.isdir(output_dir):
	sys.exit("%s is not a directory" % (output_dir))

if keep_log:
	logfilename = "%s/%s_rankings_collection_log.txt" % (output_dir, mode);
	logfile     = open(logfilename, "a")
	if verbose:
		print("logfilename: %s" % (logfilename))
else:
	print("No log being kept.")

list_filename = "%s/%s_collected_rankings_list.txt" % (output_dir, mode);
list_file     = open(list_filename, "a")
if verbose:
	print("list_filename: %s" % (list_filename))

start_date = start_date.replace(hour =  0, minute =  0, second =  0, microsecond=0)
final_date = final_date.replace(hour = 23, minute = 59, second = 59, microsecond=999999)

#---
# Get list of dates for which ranking is available:
url = 'http://www.atpworldtour.com/en/rankings/%s' % (mode) # This URL returns current top 100 by default
atp_ranking_content = requests.get(url)
soup                = bs4.BeautifulSoup(atp_ranking_content.text, 'html.parser')
dropdown_wrapper    = soup.select('div.dropdown-wrapper')
dropdowns           = dropdown_wrapper[0].select("ul")
dirty_date_list     = dropdowns[0].select("li")
date_tag_list       = [x.get_text().strip() for x in dirty_date_list]
date_tag_list       = list(set(date_tag_list))
date_tag_list.sort()
if verbose:
	print("Date list:")
	print("Date list size: %d" % (len(date_tag_list)))
	print("Initial date:   %s" % (date_tag_list[0]))
	print("Final   date:   %s" % (date_tag_list[-1]))
	#print("\n".join(date_tag_list))

#---
# Set log-file if not interactive
datelist_filename = "%s/%s_datelist.csv" % (output_dir, mode);
datelist_file     = open(datelist_filename, "w")
datelist_file.write("\n".join(date_tag_list));
datelist_file.close()

#---
# Filter all available dates for requested dates:
date_list = [datetime.datetime(int(x.split('.')[0]), 
                               int(x.split('.')[1]), 
                               int(x.split('.')[2])) for x in date_tag_list]
date_list = [x for x in list(set(date_list)) if x<= final_date and x>=start_date]
date_list.sort()

#---
if verbose:
	print("Preparing to collect data for dates:")
	print("\n".join([x.strftime('%Y-%m-%d') for x in date_list]))

#---
# Collect data:
for this_date in date_list:
	if verbose:
		print("Collecting data for %s, %s" % (mode, this_date.strftime('%Y.%m.%d')))
	try:
		data_string = get_ranking_on_date(this_date, mode, verbose=False)
	except Exception as inst:
		if verbose:
			print("Crashed")
		if keep_log:
			logfile.write("%s: Collection %s, %s, failed: %s.\n" % (datetime.datetime.now().strftime('%Y.%m.%d,%H:%M:%S'), mode, this_date.strftime('%Y.%m.%d'), str(inst)))
			logfile.flush()
	else:
		if keep_log:
			logfile.write("%s: Collection %s, %s, completed.\n"  % (datetime.datetime.now().strftime('%Y.%m.%d,%H:%M:%S') , mode, this_date.strftime('%Y.%m.%d')))
			logfile.flush()
		if verbose:
			print("Ran OK")
		if screen_output:
			print(data_string)
		else:
			this_decade = 10*math.floor(int(this_date.strftime('%Y'))/10)
			outfilename = "%s/%d/%s_ranking_%s.csv" % (output_dir, this_decade, mode, this_date.strftime('%Y%m%d'));
			this_outdir = os.path.dirname(outfilename)
			if not os.path.isdir(this_outdir):
				os.makedirs(this_outdir);
			if not os.path.isdir(this_outdir):
				sys.exit("%s is not a directory" % (this_outdir))
			if verbose:
				print("Outputting data to %s" % (outfilename))
			outfile     = open(outfilename, "w")
			outfile.write(data_string)
			outfile.flush();
			outfile.close();
			list_file.write("%s\t%s\t%s\n"% (mode, this_date.strftime('%Y.%m.%d'), outfilename))
			list_file.flush()

#---
if keep_log:
	if verbose:
		print("Closing log file.")
	logfile.close()

list_file.close()

sys.exit()

# Get all player activity:
# http://www.atpworldtour.com/players/wouter-zoomer/z087/player-activity?year=all
# Can dig deeper going to tournament pages and getting list of past champions: US open goes back to 1912
