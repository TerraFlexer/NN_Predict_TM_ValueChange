import pandas as pd
import re
import env
from parserr import *
import csv


#array with seasons which are going to be processed
seasons = ["19-20", "20-21"]

#array with unnecessary columns
unnec_columns = ["Player", "Squad", "Cl_Squad"]

#patterns for regular
patterns = {"19": ["2019-07...", "2019-06..."], "20": ["2020-04..."], "21": ["2021-06..."]}

#arrays with player and clubs databases
players_db = []
clubs_db = []

#creating writer to the final.csv
f = open(env.final_csv, 'w', newline='')
writer = csv.writer(f, delimiter=',')

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
def cr_wr_rows(pl_frame, cl_frame, patterns1, patterns2):
	for i in range(len(pl_frame)):
		#initializing row with player_statrs
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

		#print(all_values)

		#extract values
		for i in range(len(all_values)):
			vl_row = all_values.iloc[i]
			for pattern1 in patterns1:
				if (re.fullmatch(pattern1, vl_row['date'])):
					start_vl = vl_row['market_value']
			for pattern2 in patterns2:
				if (re.fullmatch(pattern2, vl_row['date'])):
					end_vl = vl_row['market_value']

		#add values to the row
		row.append(start_vl / 1000000)
		row.append(end_vl / 1000000)
		writer.writerow(row)


#launching parsing functions generating seasonal stats for players and clubs
for season in seasons:
	parse_players(season)
	parse_clubs(season)
	players_db.append(pd.read_csv(env.pl_csv_src[season]))
	clubs_db.append(pd.read_csv(env.cl_csv_src[season]))

#uniting stats to a dicts
pl_frames = dict(zip(seasons, players_db))
cl_frames = dict(zip(seasons, clubs_db))

#flag for header
header_created_flag = 0

for season in seasons:
	#if header is not created - create it and write to the final.csv
	if (not(header_created_flag)):
		writer.writerow(create_header(pl_frames[season], cl_frames[season]))
		header_created_flag = 1

	#process seasonal stats
	cr_wr_rows(pl_frames[season], cl_frames[season], patterns[season[:2]], patterns[season[3:]])

#closing final
f.close()

#opening db again to delete needless columns
final = pd.read_csv(env.final_csv)

#deleting needless columns
for column in unnec_columns:
	del final[column]

#convert final dataframe to final.csv
final.to_csv(env.final_csv, index=False)