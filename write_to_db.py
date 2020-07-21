import requests
from bs4 import BeautifulSoup
import mysql.connector as mc
import extraction


cnx = mc.connect(user='bisola', password='@1Bullshit', host='127.0.0.1', database='sa_cricket')
cursor = cnx.cursor()

def write_matches_by_year(start, stop):

	# Note this function might not work properly because I just cut and edit from write_match(tr)

	'''
	with open('./wp/year.html', 'r') as file:
		soup = BeautifulSoup(file, 'lxml')
	'''

	for year in range(start, stop+1):
		res = requests.get('https://stats.espncricinfo.com/ci/engine/records/team/match_results.html?class=2;id={};team=3;type=year'.format(year))
		res.raise_for_status
		soup = BeautifulSoup(res.text, 'lxml')
		matches = soup.find('table', 'engineTable').tbody.find_all('tr')

		#print(matches)

		for tr in matches:
			write_match(tr)

def write_match(tr):
	'''
	write match data to match table in db
	'''
	m = tr.find_all('td')
	#print(m)
	team1 = m[0].a['href'].split('/')[-1].split('.')[0]
	team2 = m[1].a['href'].split('/')[-1].split('.')[0]
	if team1=='3':
		opposition = int(team2)
	else:
		opposition = int(team1)

	ground = m[4].a['href'].split('/')[-1].split('.')[0]
	date = m[5].string
	match_id = m[6].a['href'].split('/')[-1].split('.')[0]
	odi_no = m[6].a.string.split(' # ')[1]

	print(opposition, ground, date, match_id, odi_no)

	match_url = 'https://stats.espncricinfo.com/ci/engine/match/{}.html'.format(match_id)
	match, bat, bowl = extraction.full_match_extraction(match_url)
	
	add_match = '''
					insert into mat
					(match_id, odi_no, opposition, ground, match_date, toss, series, result, match_days)
					values(%d, %d, %d, %d, str_to_date("%s", "%%M %%d, %%Y"), "%s", "%s", "%s", "%s");
				'''
	# Double quotes are added above for all %s to avoid error (because some strings have comma)
	# strings are bs4.navigableString object. Therefore, convert to normal py string
	match_data = (int(match_id), int(odi_no), int(opposition), int(ground), str(date), str(match[0]), str(match[1]), str(match[2]), str(match[3]))

	print(add_match % match_data)
	cursor.execute(add_match % match_data)
	cnx.commit()


'''
The following functions would be added
'''
def write_player():
	# Select unique players from match table and extract their data using extraction module
	player_url = 'https://www.espncricinfo.com/southafrica/content/player/{}.html'
	pass

def write_ground():
	# Same method as player
	ground_url = 'https://www.espncricinfo.com/ci/content/ground/{}.html'
	pass




write_match()


cursor.close()
cnx.close()