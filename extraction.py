import requests
from bs4 import BeautifulSoup

'''
In extract_match and extract_player, I created a list of all information provided (according).
The reason is to use the index in extracting the specific information I need.
'''
def full_match_extraction(url):
	'''	
	# Incase I need to work with file on my pc (e.g for testing and experimenting)
	with open(url, 'r') as file:
		soup = BeautifulSoup(file, 'lxml')
	'''

	res = requests.get(url)
	res.raise_for_status
	soup = BeautifulSoup(res.text, 'lxml')


	innings = soup.find_all('div', 'Collapsible')
	in1 = innings[0]
	in2 = innings[1]
	team1 = in1.find('h5', 'header-title').string
	team2 = in2.find('h5', 'header-title').string

	if 'South Africa' in team1:
		bat_table = in1.find('table', 'batsman')
		bowl_table = in2.find('table', 'bowler')
	else:
		bat_table = in2.find('table', 'batsman')
		bowl_table = in1.find('table', 'bowler')


	match = extract_match(soup)
	bat = extract_bat(bat_table)
	bowl = extract_bowl(bowl_table)

	return match, bat, bowl

def extract_match(soup):
	'''
	Return a list of match details
	'''

	# venue and odi_no are not returned because we already have them in write_to_db
	# match_day is included even though we already have date because we might probably get time for other attributes in the analysis
	match_table = soup.find('div', 'table-responsive').table.tbody
	venue = match_table.contents[0].string	# Excluded

	info = []
	for x in match_table.contents:
		info.append(x.find('td').string)

	toss = match_table.contents[info.index('Toss')].contents[1].string
	series = match_table.contents[info.index('Series')].contents[1].string

	# Unfortunately, some matches do not contain 'Series result'
	# So to prevent breaking, we got an if statement
	if 'Series result' in info:
		series_result = match_table.contents[info.index('Series result')].contents[1].string
	else:
		series_result = ''

	odi_no = match_table.contents[info.index('Match number')].contents[1].string.split('. ')[1] # Excluded
	match_days = match_table.contents[info.index('Match days')].contents[1].string

	return [toss, series, series_result, match_days]

def extract_bat(bat_table):
	'''
	Return a list of batmen and there stats
	'''
	batman = bat_table.tbody.find_all('tr')
	bat = []

	for b in batman:
		batman_cell = b.find('td', 'batsman-cell')
		# The if statement is required because of some empty rows that are probably used for padding or design shits like that
		if batman_cell:
			player_id = batman_cell.a['href'].split('/')[-1].split('.')[0]
			out = batman_cell.next_sibling
			runs = out.next_sibling
			ball_faced = runs.next_sibling

			# This if statement below prevents working with strike_rate = '-'
			# Also, 0 ball faced will probably mess with analysis
			if ball_faced.string == '0':
				continue

			M = ball_faced.next_sibling
			# I don't know what the heck M means but some are '-' too.
			# M might be useful for someone else or later on so I'm droping it.
			# Fortunately, I can't find M=0. So,
			if M.string == '-':
				M.string.replace_with('0')

			_4s = M.next_sibling
			_6s = _4s.next_sibling
			strike_rate = _6s.next_sibling
			bat.append([player_id, runs.string, ball_faced.string, M.string, _4s.string, _6s.string, strike_rate.string])
	return bat

def extract_bowl(bowl_table):
	'''
	Return a list of bowlers and their stats
	'''
	bowler = bowl_table.tbody.find_all('tr')
	bowl = []
	
	for b in bowler:
		# Unlike bat_table, there are no empty rows here
		info = b.contents

		player_id = info[0].a['href'].split('/')[-1].split('.')[0]
		overs = info[1].string
		M = info[2].string
		runs_conceded = info[3].string
		wickets_taken = info[4].string
		econ = info[5].string
		_0s = info[6].string
		_4s = info[7].string
		_6s = info[8].string
		wide = info[9].string
		no_ball = info[10].string
		bowl.append([player_id, overs, M, runs_conceded, wickets_taken, econ, _0s, _4s, _6s, wide, no_ball])
	return bowl

def extract_ground(url):
	'''
	return a list: [ground_name, ground_country]
	'''

	res = requests.get(url)
	res.raise_for_status
	soup = BeautifulSoup(res.text, 'lxml')
	
	'''
	# Incase I need to work with file on my pc (e.g for testing and experimenting)
	with open(url, 'r') as file:
		soup = BeautifulSoup(file, 'lxml')
	'''
	return soup.title.string.split(' | ')[0:2]


def extract_player(url):
	'''
	Return a list containing details of player
	'''

	'''
	# Incase I need to work with file on my pc (e.g for testing and experimenting)
	with open(url, 'r') as file:
		soup = BeautifulSoup(file, 'lxml')
	'''

	res = requests.get(url)
	res.raise_for_status
	soup = BeautifulSoup(res.text, 'lxml')

	name = soup.title.string.split(' - ')[0]

	# ODI DEBUT
	tbody_tag = soup.find_all('table', 'engineTable')[2]
	tr_tag = tbody_tag.find_all('tr', 'data2')[3]
	odi_debut = tr_tag.contents[3].contents[0].string

	print(tbody_tag)
	# The above odi_debut is like 'team1 v team2 at ground, Jan 19, 2013'
	# Other details are not required
	odi_debut = odi_debut.split(', ', 1)[1]

	# Other details
	playing_role = ''
	batting_style = ''
	bowling_style = ''
	fielding_position = ''

	info_tag = soup.find_all('p', 'ciPlayerinformationtxt')
	info = []
	for x in info_tag:
		info.append(x.find('b').string)

	if 'Playing role' in info:
		i = info.index('Playing role')
		playing_role = info_tag[i].find('span').string

	if 'Batting style' in info:
		i = info.index('Batting style')
		batting_style = info_tag[i].find('span').string

	if 'Bowling style' in info:
		i = info.index('Bowling style')
		bowling_style = info_tag[i].find('span').string

	if 'Fielding position' in info:
		i = info.index('Fielding position')
		fielding_position = info_tag[i].find('span').string

	return [name, odi_debut, playing_role, batting_style, bowling_style, fielding_position]


'''
match, bat, bowl = full_match_extraction('https://www.espncricinfo.com/series/10904/scorecard/1075506/south-africa-vs-bangladesh-3rd-odi-bangladesh-tour-of-sa-2017-18')
print(match)
for x in bat: print(x)
for y in bowl: print(y)
'''

print(extract_player('https://www.espncricinfo.com/southafrica/content/player/379143.html'))
# 698189, 379143

#print(full_match_extraction('./wp/match1.html'))
#print(full_match_extraction('https://stats.espncricinfo.com/ci/engine/match/800471.html'))
# extract_match()





'''
for x in range(2017,2020):
	url = 'https://stats.espncricinfo.com/ci/engine/records/team/match_results.html?class=2;id={};team=3;type=year'
	url =  url.format(x)
	print(url)
'''
