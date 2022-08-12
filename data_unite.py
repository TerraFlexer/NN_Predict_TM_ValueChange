import pandas as pd
import re
import env

pl_csv_src = env.pl_csv_src
cl_csv_src = env.cl_csv_src
tmpl_csv_src = env.tmpl_csv_src
tmvl_csv_src = env.tmvl_csv_src

players = pd.read_csv(pl_csv_src)
clubs = pd.read_csv(cl_csv_src)
tm_players = pd.read_csv(tmpl_csv_src)
tm_values = pd.read_csv(tmvl_csv_src)

pl_club_stats = []
cl_header = list(clubs.columns)[1:]

cl_header.append("Value 2020")
cl_header.append("Value 2021")
print(cl_header)

for i in range(len(clubs.count()) + 1):
	pl_club_stats.append([])
print(pl_club_stats)
pattern20 = "2020-04..."
pattern21 = "2021-06..."
for i in range(len(players)):
	squad = " " + players.loc[i].at['Squad']
	name = players.loc[i].at['Player']

	club_stats = clubs.loc[clubs['Squad'] == squad]
	for i in range(1, len(club_stats.count())):
		pl_club_stats[i - 1].append(club_stats.iloc[0].at[cl_header[i - 1]])

	row = tm_players.loc[tm_players['pretty_name'] == name]
	if (row.empty):
		pl_club_stats[-2].append(None)
		pl_club_stats[-1].append(None)
		continue
	if (len(row) == 1):
		pl_id = row.iloc[0].at['player_id']
	else:
		pl_club_stats[-2].append(None)
		pl_club_stats[-1].append(None)
		continue
	all_values = tm_values.loc[tm_values['player_id'] == pl_id]
	for i in range(len(all_values)):
		row = all_values.iloc[i]
		if (re.fullmatch(pattern20, row['date'])):
			value20 = row['market_value']
		if (re.fullmatch(pattern21, row['date'])):
			value21 = row['market_value']
	pl_club_stats[-2].append(value20)
	pl_club_stats[-1].append(value21 - value20)

for i in range(len(cl_header) - 2):
	cl_header[i] = "Cl_" + cl_header[i]

print(pl_club_stats)

for i in range(len(pl_club_stats)):
	#print(cl_header[i])
	#print(pl_club_stats[i])
	players.insert(len(players.count()), cl_header[i], pl_club_stats[i])

del pl_club_stats['Player']
del pl_club_stats['Squad']

players.to_csv(env.final_csv, index=False)