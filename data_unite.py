import pandas as pd
import re
import env
from parserr import *
import csv


#array with training_seasons which are going to be processed
training_seasons = ["19-20", "20-21"]

#array with testing_seasons
testing_seasons = ["21-22"]

#array with unnecessary columns
unnec_columns = ["Player", "Squad", "Cl_Squad"]

#patterns for regular
patterns = {"19": ["2019-04...", "2019-05...", "2019-06...", "2019-07...", "2019-08...", "2019-09..."],
	"20": ["2020-04...", "2020-05...", "2020-06...", "2020-07...", "2020-08..."], "21": ["2021-05...", "2021-06...", "2021-07...", "2021-08..."],
	"22": ["2022-05...", "2022-06...", "2022-07...", "2022-08..."]}

#arrays with player and clubs databases for training
tr_players_db = []
tr_clubs_db = []

#arrays with player and clubs databases for testing
ts_players_db = []
ts_clubs_db = []

#creating writer to the final.csv
final_file = open(env.final_csv, 'w', newline='')
final_writer = csv.writer(final_file, delimiter=',')

#creating writer to the test.csv
test_file = open(env.test_csv, 'w', newline='')
test_writer = csv.writer(test_file, delimiter=',')

#opening transfermarkt databases
tm_players = pd.read_csv(env.tmpl_csv_src)
tm_values = pd.read_csv(env.tmvl_csv_src)

#function creating header
def create_header(pl_frame, cl_frame):
	pl_header = list(pl_frame.columns)
	cl_header = list(cl_frame.columns)

	for i in range(len(cl_header)):
		cl_header[i] = "Cl_" + cl_header[i]

	#uniting 2 headers
	header = pl_header + cl_header

	#adding columns names for TM values
	header.append("Start_Value")
	header.append("Value_Change")
	return header

#function creating and writing rows into the final.csv
def cr_wr_rows(pl_frame, cl_frame, patterns1, patterns2, writer):
	for i in range(len(pl_frame)):
		#exlude players who played less than 5 matches in total(counting in total minutes)
		if (pl_frame.iloc[i].at["90s"] < 5):
			continue

		#initializing row with player_stats
		row = list(pl_frame.iloc[i])

		#extracting squad name and player name to connect with other dbs
		squad = " " + pl_frame.iloc[i].at['Squad']
		name = pl_frame.iloc[i].at['Player']

		#find club_stats corresponding the player
		club_stats = cl_frame.loc[cl_frame['Squad'] == squad]

		#add club_stats to the row
		row = row + list(club_stats.iloc[0])

		#find tm_row corresponding the player and extract player_id
		tm_row = tm_players.loc[tm_players['pretty_name'] == name]
		if (tm_row.empty):
			continue
		if (len(tm_row) == 1):
			pl_id = tm_row.iloc[0].at['player_id']
		else:
			continue

		#find rows with exact player_id
		all_values = tm_values.loc[tm_values['player_id'] == pl_id]


		found = 0
		#extract values
		for i in range(len(all_values)):
			vl_row = all_values.iloc[i]
			for pattern1 in patterns1:
				if (re.fullmatch(pattern1, vl_row['date'])):
					start_vl = vl_row['market_value']
			for pattern2 in patterns2:
				if (re.fullmatch(pattern2, vl_row['date'])):
					end_vl = vl_row['market_value']
					found = 1

		#add values to the row
		row.append(start_vl / 1000000)
		if (found):
			row.append(end_vl / 1000000)
		else:
			row.append(start_vl / 1000000)
		writer.writerow(row)


#launching parsing functions generating training seasonal stats for players and clubs
for season in training_seasons:
	parse_players(season)
	parse_clubs(season)
	tr_players_db.append(pd.read_csv(env.pl_csv_src[season]))
	tr_clubs_db.append(pd.read_csv(env.cl_csv_src[season]))

#launching parsing functions generating testing seasonal stats for players and clubs
for season in testing_seasons:
	parse_players(season)
	parse_clubs(season)
	ts_players_db.append(pd.read_csv(env.pl_csv_src[season]))
	ts_clubs_db.append(pd.read_csv(env.cl_csv_src[season]))

#uniting training stats to a dicts
tr_pl_frames = dict(zip(training_seasons, tr_players_db))
tr_cl_frames = dict(zip(training_seasons, tr_clubs_db))

#uniting training stats to a dicts
ts_pl_frames = dict(zip(testing_seasons, ts_players_db))
ts_cl_frames = dict(zip(testing_seasons, ts_clubs_db))

#flag for header
header_created_flag = 0

#processing training data
for season in training_seasons:
	#if header is not created - create it and write to the final.csv
	if (not(header_created_flag)):
		final_writer.writerow(create_header(tr_pl_frames[season], tr_cl_frames[season]))
		header_created_flag = 1

	#process seasonal stats
	cr_wr_rows(tr_pl_frames[season], tr_cl_frames[season], patterns[season[:2]], patterns[season[3:]], final_writer)

#flag for header
header_created_flag = 0

#processing testing data
for season in testing_seasons:
	#if header is not created - create it and write to the final.csv
	if (not(header_created_flag)):
		test_writer.writerow(create_header(ts_pl_frames[season], ts_cl_frames[season]))
		header_created_flag = 1

	#process seasonal stats
	cr_wr_rows(ts_pl_frames[season], ts_cl_frames[season], patterns[season[:2]], patterns[season[3:]], test_writer)

#closing final
final_file.close()

#closing test
test_file.close()

#opening db again to delete needless columns
final = pd.read_csv(env.final_csv)

#deleting needless columns
for column in unnec_columns:
	del final[column]

#convert final dataframe to final.csv
final.to_csv(env.final_csv, index=False)

#opening db again to delete needless columns
test = pd.read_csv(env.test_csv)

#deleting needless columns
for column in unnec_columns:
	del test[column]

#convert final dataframe to final.csv
test.to_csv(env.test_csv, index=False)