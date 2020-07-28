import requests
from bs4 import BeautifulSoup
import mysql.connector as mc
import extraction


cnx = mc.connect(user='bisola', password='@1Bullshit', host='127.0.0.1', database='sa_cricket')
cursor = cnx.cursor()

def write_matches_by_year(start, stop=2019):

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

		c=0
		for tr in matches:
			write_full_match(tr)
			c+=1
			print(c, 'match')
			#if c==2: break

def write_full_match(tr):
	'''
	write match data to match table in db
	'''
	m = tr.find_all('td')
	#print(m)

	# Don't execute for games without result
	winner = m[2].string
	if winner=='no result': 
		print('found no result')
		return False

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
	add_bat = '''
				insert into bat
				values(%d, %d, %d, %d, %d, %d, %d, %f);
			  '''
	add_bowl = '''
				insert into bowl
				values(%d, %d, %f, %d, %d, %d, %f, %d, %d, %d, %d, %d);
			   '''
	
	# strings are bs4.navigableString object. Therefore, convert to normal py string
	match_data = (int(match_id), int(odi_no), int(opposition), int(ground), str(date), str(match[0]), str(match[1]), str(match[2]), str(match[3]))
	#print(add_match % match_data)
	cursor.execute(add_match % match_data)
	cnx.commit()

	for b in bat:
		bat_data = (int(b[0]), int(match_id), int(b[1]), int(b[2]), int(b[3]), int(b[4]), int(b[5]), float(b[6]))
		cursor.execute(add_bat % bat_data)
		cnx.commit()

	for b in bowl:
		bowl_data = (int(b[0]), int(match_id), float(b[1]), int(b[2]), int(b[3]), int(b[4]), float(b[5]), int(b[6]), int(b[7]), int(b[8]), int(b[9]), int(b[10]))
		cursor.execute(add_bowl % bowl_data)
		cnx.commit()

	return True

'''
The following functions would be added
'''
def write_player():
	# Select unique players from bat and bowl table and extract their data using extraction module
	select_batters = 'select distinct player from bat;'
	cursor.execute(select_batters)
	rows = cursor.fetchall()

	select_bowlers = 'select distinct player from bowl;'
	cursor.execute(select_bowlers)
	rows.extend(cursor.fetchall())

	add_player = '''
					insert into player
					values(%d, "%s",  str_to_date("%s", "%%M %%d, %%Y"), "%s", "%s", "%s", "%s")
				 '''

	for player in set(rows):
		player = player[0]	# Tuples were returned from select query
		print('working on', player)
		player_url = 'https://www.espncricinfo.com/southafrica/content/player/{}.html'.format(player)
		b = extraction.extract_player(player_url)
		player_data = (player, str(b[0]), str(b[1]), str(b[2]), str(b[3]), str(b[4]), str(b[5]))
		cursor.execute(add_player % player_data)
		cnx.commit()
		print('added player', player)


def write_ground():
	# Select unique grounds from mat table and extract their data using extraction module
	select_query = 'select distinct ground from mat;'
	add_ground = '''
					insert into ground
					values(%d, "%s", "%s");
				 '''
	cursor.execute(select_query)
	rows = cursor.fetchall()

	for ground in rows:
		ground = ground[0] # Tuples were returned from select query
		print('working on', ground)
		ground_url = 'https://www.espncricinfo.com/ci/content/ground/{}.html'.format(ground)
		g = extraction.extract_ground(ground_url)
		ground_data = (ground, str(g[0]), str(g[1]))
		cursor.execute(add_ground % ground_data)
		cnx.commit()
		print('added ground', ground)
	
	return True

#write_matches_by_year(2017)
write_player()

#print(extraction.extract_player('https://www.espncricinfo.com/southafrica/content/player/379143.html'))

cursor.close()
cnx.close()