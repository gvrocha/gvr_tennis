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
import argparse

#---
missing_string     = ""
this_dir           = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
today              = datetime.datetime.now()

#---
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--mode', metavar='N', type=int, nargs='+',
                    help='an integer for the accumulator')
parser.add_argument('mode',            type = str, help = "collect data for 'singles' or 'doubles'")
parser.add_argument('player_tag',      type = str, help = "player tag (e.g. 'novak-djokovic')")
parser.add_argument('player_number',   type = str, help = "player id in ATP website (e.g. 'd643')")
parser.add_argument('season',          type = str, help = "either the year for which to collect or 'all'")
parser.add_argument('--quiet',         dest = "quiet",         action = 'store_const', const = True,      default = False,      help = "")
parser.add_argument('--screen_output', dest = "screen_output", action = 'store_const', const = True ,     default = False,      help = "")
parser.add_argument('--skip_log',      dest = "keep_log",      action = 'store_const', const = False,     default = True,       help = "")
parser.add_argument('--outdir',        dest = "outdir",        type = str, default = "",                                        help = "output directory (default: '%s/../data/ranking_files/<mode>/collected')" % (this_dir))

#---
args                = parser.parse_args()
mode                = args.mode
this_player_tag     = args.player_tag
this_player_number  = args.player_number
this_year           = args.season
verbose             = not args.quiet
output_dir          = args.outdir
screen_output       = args.screen_output
keep_log            = args.keep_log

if(output_dir == ""):
	output_dir = "%s/../data/player_activity/%s/" % (this_dir, mode)

year_re = re.compile("^(\d{4,4}|all)$")

year_match = year_re.match(this_year)
if not year_match:
	print("Error: Year is not 'yyyy' or 'all'")
	sys.exit()

#---
collection_date = datetime.datetime.now().strftime("%Y%m%d")
print("BEGIN: %s" % (datetime.datetime.now().strftime("%Y/%m/%d,%H:%M:%S")))
print("Type:             %s" % (mode));
print("Player tag:       %s" % (this_player_tag));
print("Player number:    %s" % (this_player_number));
print("Year:             %s" % (this_year));
print("Output directory: %s" % (output_dir));
print("Verbose:          %s" % (str(verbose)));
print("Screen output:    %s" % (screen_output));
print("Keep log:         %s" % (keep_log));

this_player_activity_url = "http://www.atpworldtour.com/players/%s/%s/player-activity?year=%s&matchType=%s" % (this_player_tag, this_player_number, this_year, mode)
if verbose:
	print("URL: %s" % (this_player_activity_url))

#---

this_activity_page       = requests.get(this_player_activity_url)
this_activity_soup       = bs4.BeautifulSoup(this_activity_page.text)

#---

tournament_list          = this_activity_soup.select('div.activity-tournament-table')
n_tournaments = len(tournament_list)
if(verbose):
	print("Number of tournaments: %d" % (n_tournaments))

#---
# loop over tournaments here:
tournament_df = pd.DataFrame(columns=['tourney_type',
                                      'tourney_name',
                                      'tourney_location',
                                      'tournament_start_date',
                                      'tournament_end_date',
                                      'tourney_code',
                                      'tourney_tag',
                                      'tourney_number',
                                      'tournament_surface',
                                      'tournament_bracket_size',
                                      'prize_money',
                                      'financial_commitment',
                                      'player_tag',
                                      'player_number',
                                      'partner_tag',
                                      'partner_number',
                                      'player_points',
                                      'player_prize',
                                      'player_ranking'])
match_df      = pd.DataFrame(columns=['tourney_type',
                                      'tourney_name',
                                      'tourney_tag',
                                      'tourney_number',
                                      'tournament_start_date',
                                      'tournament_end_date',
                                      'player_tag',
                                      'player_number',
                                      'partner_tag',
                                      'partner_number',
                                      'round',
                                      'opponent_rank',
                                      'opponent_name',
                                      'opponent_tag',
                                      'opponent_number',
                                      'opponent_partner_rank',
                                      'opponent_partner_name',
                                      'opponent_partner_tag',
                                      'opponent_partner_number',
                                      'match_outcome',
                                      'match_link',
                                      'match_score'])
#this_tournament          = tournament_list[0]
k = 0
for this_tournament in tournament_list:
	k  += 1
	if(verbose):
		print("Processing tournament %d/%d" % (k, n_tournaments))
	tournament_header_list   = this_tournament.select('table.tourney-results-wrapper')
	match_table_list         = this_tournament.select('table.mega-table')
	tournament_footer_list   = this_tournament.select('div.activity-tournament-caption')
	
	if(len(tournament_header_list)>1):
		print("Warning: more than one tournament header found")	
	
	if(len(match_table_list)>1):
		print("Warning: more than one match table found")
	
	if(len(tournament_footer_list)>1):
		print("Warning: more than one tournament footer found")
	
	tournament_header = tournament_header_list[0]
	tournament_footer = tournament_footer_list[0]
	match_table       = match_table_list[0]
	
	#---
	# Process header:
	tournament_name_list     = tournament_header.select("a.tourney-title")      # This will be empty for Davis Cup or unlinked tournaments
	linked_tournament        = True;
	if(len(tournament_name_list)==0):
		tournament_name_list = tournament_header.select("span.tourney-title")   # This should handle Davis Cup and unlinked tournaments
		linked_tournament    = False;
	
	tournament_location_list = tournament_header.select("span.tourney-location")
	tournament_dates_list    = tournament_header.select("span.tourney-dates")
	
	tournament_name         = tournament_name_list[0].text.strip()
	tournament_location     = tournament_location_list[0].text.strip()
	tournament_dates        = tournament_dates_list[0].text.strip()
	tournament_dates_vec    = [x.strip() for x in tournament_dates.split("-")]
	tournament_start_date   = tournament_dates_vec[0]
	if(len(tournament_dates_vec)>1):
		tournament_end_date = tournament_dates_vec[1]
	else: # Nadal, ATP Masters Series Paris Q, France, 2003.10.27: is this a bug in ATP page?
		tournament_end_date = missing_string
	
	if(verbose):
		print("%s, %s, %s" % (tournament_name, tournament_location, tournament_dates))
	sys.stdout.flush()
	
	# --- 
	# Process details within header:
	tournament_detail_list  = tournament_header.select("td.tourney-details-table-wrapper")
	tournament_detail       = tournament_detail_list[0]
	detail_pieces           = tournament_detail.select("td.tourney-details")
	tournament_bracket_size = re.sub("\s+", "\t", detail_pieces[0].text.strip())
	tournament_bracket_size = re.sub("([SGL|DBL])\\t+", "\\1:", tournament_bracket_size)
	tournament_surface      = re.sub("\s+", " ", detail_pieces[1].text.strip())

	if len(tournament_detail.select("td.prize-money"))==1:
		prize_money = tournament_detail.select("td.prize-money")[0].text.strip()
		prize_money = re.sub("\\s+",       "", prize_money)
		prize_money = re.sub("PrizeMoney", "", prize_money)
		prize_money = re.sub(",",          "", prize_money)
	else:
		prize_money = missing_string

	if len(tournament_detail.select("td.fin-commit"))==1:
		financial_commitment = tournament_detail.select("td.fin-commit")[0].text.strip()
		financial_commitment = re.sub("\\s+",                     "", financial_commitment)
		financial_commitment = re.sub("TotalFinancialCommitment", "", financial_commitment)
		financial_commitment = re.sub(",",                        "", financial_commitment)
	else:
		financial_commitment = missing_string

	if(linked_tournament):
		tournament_link     = tournament_name_list[0].get("href") # This will return None for Davis Cup and unlinked tournaments
		tournament_code     = tournament_link.replace("/en/tournaments/","").replace("/overview", "")
		tournament_tag      = tournament_code.split("/")[0]
		tournament_number   = tournament_code.split("/")[1]
	else:
		tournament_link     = missing_string
		tournament_code     = missing_string
		tournament_tag      = missing_string
		tournament_number   = missing_string
	
	#---
	# Process footer:
	footer_text = tournament_footer.text
	if(mode == "doubles"):
		footer_text_pieces = footer_text.split(", Partner")
		footer_text        = footer_text_pieces[0]
		partner_name       = footer_text_pieces[1]
		partner_code       = tournament_footer.select("a")[0].get("href").replace("/en/players/","").replace("/overview", "")
		if(partner_code == "#"):
			partner_tag        = missing_string
			partner_number     = missing_string
		else:
			partner_tag        = partner_code.split("/")[0]
			partner_number     = partner_code.split("/")[1]
	else:
		partner_name       = missing_string
		partner_tag        = missing_string
		partner_number     = missing_string
	footer_text = re.sub("(\\d),(\\d)", "\\1\\2", footer_text) # Erases commas as thousand separators
	footer_dict = {x.split(":")[0].strip():x.split(":")[1].strip() for x in footer_text.split(",")}

	#---
	# Collect all tournament result data into a dataframe:
	tourney_data_dict = { 'tourney_type'            : [mode],
	                      'tourney_name'            : [tournament_name],
	                      'tourney_location'        : [tournament_location],
	                      'tournament_start_date'   : [tournament_start_date],
	                      'tournament_end_date'     : [tournament_end_date],
	                      'tourney_code'            : [tournament_code],
	                      'tourney_tag'             : [tournament_tag],
	                      'tourney_number'          : [tournament_number],
	                      'tournament_surface'      : [tournament_surface],
	                      'tournament_bracket_size' : [tournament_bracket_size],
	                      'prize_money'             : [prize_money],
	                      'financial_commitment'    : [financial_commitment],
	                      'player_tag'              : [this_player_tag],
	                      'player_number'           : [this_player_number],
	                      'partner_tag'             : [partner_tag],
	                      'partner_number'          : [partner_number],
	                      'player_points'           : footer_dict["This Event Points"],
	                      'player_prize'            : footer_dict["Prize Money"],
	                      'player_ranking'          : footer_dict["ATP Ranking"]}
	
	tournament_row    = pd.DataFrame(tourney_data_dict)
	tournament_df     = pd.concat([tournament_df, tournament_row])
	
	match_list      = match_table.select("tr")
	n_matches       = len(match_list)
	if(verbose):
		print("Number of matches in this tournament: %d" % (n_matches))

	#---
	# loop over matches here:
	#this_match      = match_list[0]
	j = 0
	for this_match in match_list:
		j += 1
		if(verbose):
			print("Processing match %d/%d" % (j, n_matches))
		match_pieces    = this_match.select("td")
		round           = match_pieces[0].text.strip()
		opponent_rank   = match_pieces[1].text.strip()
		if(mode == "singles"):
			if(len(match_pieces[2].select("a.mega-player-name"))==1):
				opponent_name   = match_pieces[2].select("a.mega-player-name")[0].text
				opponent_link   = match_pieces[2].select("a.mega-player-name")[0].get("href")
				opponent_code   = opponent_link.replace("/en/players/","").replace("/overview", "")
				# This is a patch for when links to opponent appear to be missing:
				if(opponent_code == "#"):
					opponent_tag    = opponent_name
					opponent_number = missing_string
				else:
					opponent_tag    = opponent_code.split("/")[0]
					opponent_number = opponent_code.split("/")[1]
			else:
				opponent_name   = match_pieces[2].text.strip()
				opponent_link   = missing_string
				opponent_code   = missing_string
				opponent_tag    = missing_string
				opponent_number = missing_string
				
			opponent_partner_name   = missing_string
			opponent_partner_link   = missing_string
			opponent_partner_code   = missing_string
			opponent_partner_tag    = missing_string
			opponent_partner_number = missing_string
			opponent_partner_rank   = missing_string
			
		elif(mode == "doubles"):
			opponent_ranks          = re.sub("\t|\n", "", opponent_rank).split("\r")
			# This if-else is a bit of a patch: In doubles BYEs, no line break in this cell...
			# But I am not sure this will let in other issues...
			if(len(match_pieces[2].select("a.mega-player-name"))==2):
				opponent_name   = match_pieces[2].select("a.mega-player-name")[0].text
				opponent_link   = match_pieces[2].select("a.mega-player-name")[0].get("href")
				opponent_code   = opponent_link.replace("/en/players/","").replace("/overview", "")
				if(opponent_code == "#"):
					opponent_tag    = opponent_name
					opponent_number = missing_string
				else:
					opponent_tag    = opponent_code.split("/")[0]
					opponent_number = opponent_code.split("/")[1]
				opponent_rank   = opponent_ranks[0]
				
				opponent_partner_name   = match_pieces[2].select("a.mega-player-name")[1].text
				opponent_partner_link   = match_pieces[2].select("a.mega-player-name")[1].get("href")
				opponent_partner_code   = opponent_partner_link.replace("/en/players/","").replace("/overview", "")
				if(opponent_partner_code == "#"):
					opponent_partner_tag    = opponent_name
					opponent_partner_number = missing_string
				else:
					opponent_partner_tag    = opponent_partner_code.split("/")[0]
					opponent_partner_number = opponent_partner_code.split("/")[1]
				opponent_partner_rank   = opponent_ranks[1]
			else:
				opponent_name   = match_pieces[2].text.strip()
				opponent_link   = missing_string
				opponent_code   = missing_string
				opponent_tag    = missing_string
				opponent_number = missing_string
				
				opponent_partner_name   = missing_string
				opponent_partner_link   = missing_string
				opponent_partner_code   = missing_string
				opponent_partner_tag    = missing_string
				opponent_partner_number = missing_string
				opponent_partner_rank   = missing_string
		#
		match_outcome = match_pieces[3].text.strip();
		if(len(match_pieces[4].select("a"))==1):
			match_link    = match_pieces[4].select("a")[0].get("href")
			match_score   = match_pieces[4].select("a")[0].text.strip()
		else:
			match_link    = missing_string
			match_score   = match_pieces[4].text.strip()
		#
		if(verbose):
			print("%s, %s, %s" % (round, opponent_rank, opponent_name))
		#
		match_row     = pd.DataFrame({ 'tourney_type'            : [mode],
		                               'tourney_name'            : [tournament_name],
		                               'tourney_tag'             : [tournament_tag],
		                               'tourney_number'          : [tournament_number],
		                               'tournament_start_date'   : [tournament_start_date],
		                               'tournament_end_date'     : [tournament_end_date],
		                               'player_tag'              : [this_player_tag],
		                               'player_number'           : [this_player_number],
		                               'partner_tag'             : [partner_tag],
		                               'partner_number'          : [partner_number],
		                               'round'                   : [round],
		                               'opponent_rank'           : [opponent_rank],
		                               'opponent_name'           : [opponent_name],
		                               'opponent_tag'            : [opponent_tag],
		                               'opponent_number'         : [opponent_number],
		                               'opponent_partner_rank'   : [opponent_partner_rank],
		                               'opponent_partner_name'   : [opponent_partner_name],
		                               'opponent_partner_tag'    : [opponent_partner_tag],
		                               'opponent_partner_number' : [opponent_partner_number],
		                               'match_outcome'           : [match_outcome],
		                               'match_link'              : [match_link],
		                               'match_score'             : [match_score]})
		match_df      = pd.concat([match_df, match_row])

collection_date = datetime.datetime.now().strftime("%Y%m%d")

tournament_df = tournament_df[['tourney_type',
                               'tourney_name',
                               'tourney_location',
                               'tournament_start_date',
                               'tournament_end_date',
                               'tourney_code',
                               'tourney_tag',
                               'tourney_number',
                               'tournament_surface',
                               'tournament_bracket_size',
                               'prize_money',
                               'financial_commitment',
                               'player_tag',
                               'player_number',
                               'partner_tag',
                               'partner_number',
                               'player_points',
                               'player_prize',
                               'player_ranking']]

match_df = match_df[['tourney_type',
                     'tourney_name',
		             'tourney_tag',
		             'tourney_number',
		             'tournament_start_date',
		             'tournament_end_date',
		             'player_tag',
		             'player_number',
		             'partner_tag',
		             'partner_number',
		             'round',
		             'opponent_rank',
		             'opponent_name',
		             'opponent_tag',
		             'opponent_number',
		             'opponent_partner_rank',
		             'opponent_partner_name',
		             'opponent_partner_tag',
		             'opponent_partner_number',
		             'match_outcome',
		             'match_link',
		             'match_score']]

this_player_group        = this_player_number[0:1]

match_list_filename      = "%s/match_lists/collected/%s/match_list_%s_%s_%s_%s_%s.csv"           % (output_dir, this_player_group, this_player_tag, this_player_number, mode, this_year, collection_date)
tournament_list_filename = "%s/tournament_lists/collected/%s/tournament_list_%s_%s_%s_%s_%s.csv" % (output_dir, this_player_group, this_player_tag, this_player_number, mode, this_year, collection_date)

if verbose:
	print("Saving match      list to %s" % (match_list_filename))
	print("Saving tournament list to %s" % (tournament_list_filename))

if not os.path.exists(os.path.dirname(match_list_filename)):
    os.makedirs(os.path.dirname(match_list_filename))

if not os.path.exists(os.path.dirname(tournament_list_filename)):
    os.makedirs(os.path.dirname(tournament_list_filename))

if screen_output:
	match_df.to_string(buf = sys.stdout)
	match_df.to_string(buf = sys.stdout)
	#tournament_df.to_string(buf = sys.stdout)
else:
	match_df.to_csv(match_list_filename, index = False, encoding='utf-8')
	tournament_df.to_csv(tournament_list_filename, index = False, encoding='utf-8')

if verbose:
	print("END:   %s" % (datetime.datetime.now().strftime("%Y/%m/%d,%H:%M:%S")))
