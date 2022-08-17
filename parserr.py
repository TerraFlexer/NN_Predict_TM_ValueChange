from bs4 import BeautifulSoup
import requests
import csv
import env


#dictionary for changing letters in players' names
letter_table = {'\'': '', 'ä': 'a', 'ó': 'o', 'Ł': 'L', 'ç': 'c', 'í': 'i', 'ü': 'u', 'ń': 'n', 'ß': 's', 'ö': 'o', '-': ' ', 'ï': 'i',
'É': 'E', 'ø': 'o', 'ğ': 'g', 'ě': 'e', 'ć': 'c', 'á': 'a', 'é': 'e', 'İ': 'I', 'ú': 'u', 'ş': 's', 'ë': 'e', 'Ü': 'U', 'Ç': 'C', 'ã': 'a',
'č': 'c', 'Ø': 'O', 'š': 's', 'ð': 'd', 'Ș': 'S', 'Ñ': 'N', 'ă': 'a', 'ý': 'y', 'è': 'e', 'ô': 'o', 'ō': 'o', 'ř': 'r', 'ț': 't', 'ò': 'o',
'ł': 'l', 'Ó': 'O', 'ı': 'i', 'Ö': 'O', 'î': 'i', 'æ': 'e', 'ę': 'e', 'ñ': 'n', 'ą': 'a', 'Á': 'A', 'Đ': 'D', 'Ľ': 'L', 'ó': 'o', 'å': 'a',
'Ć': 'C', 'é': 'e', '.': '', 'ž': 'z', 'ș': 's', 'à': 'a', 'ê': 'e', 'Š': 'S', ',': ' ', '▲': '', 'â': 'a', 'Ž': 'Z', 'ů': 'u', 'Ş': 'S', 'Ż': 'Z'}
leag_pos = {'eng ENG': 1, 'es ESP': 2, 'it ITA': 3, 'de GER': 4, 'fr FRA': 5}
pos_table = {'DF': 0.1, 'MF': 0.2, 'FW': 0.3, 'DF,MF': 0.15, 'MF,FW': 0.25, 'FW,DF': 0.35, 'MF,DF': 0.15, 'FW,MF': 0.25, 'DF,FW': 0.35}

#set with unusual letters
bad_letters = set()

def parse_players(season):
	#opening files with players' stats
	with open(env.plsh_page_src[season], encoding='utf-8', newline='') as fp: 
		soupsh = BeautifulSoup(fp, "html.parser")

	with open(env.plps_page_src[season], encoding='utf-8', newline='') as fp: 
		soupps = BeautifulSoup(fp, "html.parser")

	with open(env.plcr_page_src[season], encoding='utf-8', newline='') as fp: 
		soupcr = BeautifulSoup(fp, "html.parser")

	with open(env.pldf_page_src[season], encoding='utf-8', newline='') as fp: 
		soupdf = BeautifulSoup(fp, "html.parser")

	player_stats = []

	#finding table rows with stats
	sh = soupsh.find_all('tr')
	playerssh = []
	for i in sh:
		if (i.find_all('td', attrs={"data-stat": "player"}) != []):
			playerssh.append(i)

	player_stats.append(playerssh)

	ps = soupps.find_all('tr')
	playersps = []
	for i in ps:
		if (i.find_all('td', attrs={"data-stat": "player"}) != []):
			playersps.append(i)

	player_stats.append(playersps)

	cr = soupcr.find_all('tr')
	playerscr = []
	for i in cr:
		if (i.find_all('td', attrs={"data-stat": "player"}) != []):
			playerscr.append(i)

	player_stats.append(playerscr)

	df = soupdf.find_all('tr')
	playersdf = []
	for i in df:
		if (i.find_all('td', attrs={"data-stat": "player"}) != []):
			playersdf.append(i)

	player_stats.append(playersdf)

	#finding and adding unusual letters to the set
	for i in playerssh:
		player_info = i.find_all('td')
		for j in player_info[0].text:
			if (not('a' <= j <= 'z') and not('A' <= j <= 'Z') and j != ' ' and not('0' <= j <= '9')):
				bad_letters.add(j)

	#creating csv file and writer for him
	f = open(env.pl_csv_src[season], 'w', newline='')
	writer = csv.writer(f, delimiter=',')

	#making header and rows for the csv file
	#array with rows
	rows = []
	#index for rows
	ind = 0

	#creating header
	shheader = soupsh.find("table", id="stats_shooting")
	shheader = shheader.find_next("tr", attrs={'class': None})
	head_info = shheader.find_all('th')

	#adding separate names header to the rows
	rows.append([])
	rows[ind].append(head_info[1].text)
	rows[ind].append(head_info[3].text)
	rows[ind].append(head_info[4].text)
	rows[ind].append(head_info[6].text)

	#adding shooting stats names header
	for i in head_info[8:-1]:
		rows[ind].append(i.text)

	#parsing passing header
	psheader = soupps.find("table", id="stats_passing")
	psheader = psheader.find_next("tr", attrs={'class': None})

	head_info = psheader.find_all('th')

	#adding passing stats names header
	for i in head_info[9:-1]:
		rows[ind].append(i.text)

	#parsing creation header
	crheader = soupcr.find("table", id="stats_gca")
	crheader = crheader.find_next("tr", attrs={'class': None})

	head_info = crheader.find_all('th')

	#adding creation stats names header
	for i in head_info[9:-1]:
		rows[ind].append(i.text)

	#parsing defense header
	dfheader = soupdf.find("table", id="stats_defense")
	dfheader = dfheader.find_next("tr", attrs={'class': None})

	head_info = dfheader.find_all('th')

	#adding creation stats names header
	for i in head_info[9:-1]:
		rows[ind].append(i.text)

	#increasing index after header was added
	ind += 1

	#adding name, club and shooting stats
	for i in player_stats[0]:
		name = ""
		club = ""
		player_info = i.find_all('td')
		#goalkepeers are not added
		if (player_info[2].text.find('GK') > -1):
			continue

		#adding empty row
		rows.append([])

		#creating name with ususal letters
		for a in player_info[0].text:
			if (a in bad_letters):
				b = letter_table[a]
				name += b
			else:
				name += a

		#adding name to the row
		rows[ind].append(name)

		#adding position from the table
		rows[ind].append(pos_table[player_info[2].text])

		#creating club name with usual letters
		for a in player_info[3].text:
			if (a in bad_letters):
				b = letter_table[a]
				club += b
			else:
				club += a

		#adding club name
		rows[ind].append(club)

		#adding age
		rows[ind].append(player_info[5].text)

		#adding shooting stats
		for j in player_info[7:-1]:
			if (j.text == ''):
				rows[ind].append(0)
			else:
				rows[ind].append(float(j.text))

		#increasing row index
		ind += 1

	#adding players stats from other 3 tables(passing, creation, defending)
	for table in player_stats[1:]:
		#setting index = 1 because rows[0] is header
		ind = 1

		#adding passing, creation and defense stats except goalkeepers
		for i in table:
			player_info = i.find_all('td')
			if (player_info[2].text.find('GK') > -1):
				continue

			#if not a GK add stats
			for j in player_info[8:-1]:
				if (j.text == ''):
					rows[ind].append(0)
				else:
					rows[ind].append(float(j.text))

			#increasing row index
			ind += 1

	#writing rows in the file
	for row in rows:
		writer.writerow(row)

	#closing file with players stats csv
	f.close()



#function for parsing clubs
def parse_clubs(season):
	#opening file with club_stats
	with open(env.cl_page_src[season], encoding='utf-8', newline='') as fp: 
		soup1 = BeautifulSoup(fp, "html.parser")

	#finding table with stats
	uh = soup1.find_all('tr')
	clubs = []
	for i in uh:
		if (i.find_all('td', attrs={"data-stat": "team"}) != []):
			clubs.append(i)

	#finding and adding unusual letters to the set
	for i in clubs:
		club_info = i.find_all('td')
		for j in club_info[0].text:
			if (not('a' <= j <= 'z') and not('A' <= j <= 'Z') and j != ' ' and not('0' <= j <= '9')):
				bad_letters.add(j)
				for j in club_info[-2].text:
					if (not('a' <= j <= 'z') and not('A' <= j <= 'Z') and j != ' ' and not('0' <= j <= '9')):
						bad_letters.add(j)

	#creating csv file and writer for him
	f1 = open(env.cl_csv_src[season], 'w', newline='')
	writer = csv.writer(f1, delimiter=',')

	#finding header for clubs
	clheader = soup1.find("caption", string="Big 5 Table Table")
	clheader = clheader.find_next("tr", attrs={'class': None})

	head_info = clheader.find_all('th')

	#creating row for header
	row = []

	#adding header info to the row
	for i in head_info[1:3]:
		row.append(i.text)

	#adding league rank without last not utf-8 symbol
	row.append(head_info[3].text[:-1])

	#adding ramining stats names header except Pts and Pts/MP
	for i in head_info[8:11]:
		row.append(i.text)
	for i in head_info[13:-3]:
		row.append(i.text)

	#writing header to the csv
	writer.writerow(row)

	#writing rows with club_stats
	for i in clubs:
		club = ""
		row = []

		#finding all rows in html with club_stats
		club_info = i.find_all('td')

		#creating club name with usual letters
		for a in club_info[0].text:
			if (a in bad_letters):
				b = letter_table[a]
				club += b
			else:
				club += a

		#adding club to the row
		row.append(club)

		#adding league quality according to the table
		row.append(leag_pos[club_info[1].text])

		#adding league rank
		row.append(club_info[2].text)

		#adding reamining club stats except Pts and Pts/MP
		for j in club_info[7:10]:
			row.append(j.text)
		for j in club_info[12:-3]:
			row.append(j.text)

		#writing row to the csv
		writer.writerow(row)

	#closing clubs.csv
	f1.close()