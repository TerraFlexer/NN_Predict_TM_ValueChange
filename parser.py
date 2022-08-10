from bs4 import BeautifulSoup 
import requests

with open("20-21BIG5.html", encoding='utf-8', newline='') as fp: 
    soup = BeautifulSoup(fp, "html.parser") 
 
print(soup.title.string)

#players = soup.findAll('td', attrs={"data-stat": "player"})
hu = soup.find_all('tr')
players = []
for i in hu:
	if (i.find_all('td', attrs={"data-stat": "player"}) != []):
		players.append(i)

for i in players:
	player_info = i.find_all('td')
	for j in player_info[:-1]:
		print(j.text, end = " ")
	print("\n")

bad_letters = set()

for i in players:
	player_info = i.find_all('td')
	for j in player_info[0].text:
		if (not('a' <= j <= 'z') and not('A' <= j <= 'Z') and j != ' '):
			bad_letters.add(j)

print(bad_letters)

letter_table = {'\'': '', 'ä': 'a', 'ó': 'o', 'Ł': 'L', 'ç': 'c', 'í': 'i', 'ü': 'u', 'ń': 'n', 'ß': 'b', 'ö': 'o', '-': ' ', 'ï': 'i',
	'É': 'E', 'ø': 'o', 'ğ': 'g', 'ě': 'e', 'ć': 'c', 'á': 'a', 'é': 'e', 'İ': 'I', 'ú': 'u', 'ş': 's', 'ë': 'e', 'Ü': 'U', 'Ç': 'C', 'ã': 'a',
	'č': 'c', 'Ø': 'O', 'š': 's', 'ð': 'd'}

'''for i in players:
	player_info = i.find_all('td')
	for a in player_info[0].text:
		if (a in bad_letters):
			b = letter_table[a]
			print(b, end = "")
		else:
			print(a, end = "")
	print(" ", end = "")
	for j in player_info[1:-1]:
		print(j.text, end = " ")
	print("\n")'''